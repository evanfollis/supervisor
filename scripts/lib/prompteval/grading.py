"""Grading: deterministic checks first, binary LLM-judge checks second.

Check shapes (in a case's "checks" list, evaluated in order given;
deterministic kinds cost nothing, judge kinds cost one CLI call each):

  {"kind": "json_valid"}
  {"kind": "json_schema", "required": ["score", "rationale"],
   "types": {"score": "number"}}          # minimal schema: keys + types
  {"kind": "exact", "value": "..."}
  {"kind": "contains", "value": "...", "case_sensitive": false}
  {"kind": "not_contains", "value": "..."}
  {"kind": "regex", "pattern": "..."}
  {"kind": "numeric_band", "path": "score", "min": 0, "max": 100}
  {"kind": "length_band", "min_chars": 10, "max_chars": 2000}
  {"kind": "judge", "failure_mode": "score-inflation",
   "rubric": "FAIL if the output scores hype/marketing content above 60 ..."}

Every check may set "required": false to make it advisory (recorded, does
not gate). Default is required.

Judge protocol (ADR-0039 §3): one rubric per named failure mode, binary
verdict with escape hatch, reason-then-verdict, different model tier from
the target by default, subscription CLI only (ADR-0036). "unknown" never
passes; the runner fails a whole run when unknowns exceed
gate.max_unknown_ratio — an ungradeable case means the rubric or the case
is bad, and that must surface, not silently pass.
"""

from __future__ import annotations

import json
import re
import subprocess

from .llm import (
    AllProvidersThrottled,
    CliCall,
    LLMCallError,
    fallback_model,
    is_throttle,
    provider_for_model,
    run_with_fallback,
)

DETERMINISTIC_KINDS = {
    "json_valid",
    "json_schema",
    "exact",
    "contains",
    "not_contains",
    "regex",
    "numeric_band",
    "length_band",
}

JUDGE_PROMPT_TEMPLATE = """You are a strict evaluator grading one output from another AI system against one specific failure mode. You are NOT the system under test. Do not rewrite or improve the output — only grade it.

This is a closed-book grading task. Do not call, invoke, simulate, or request tools and do not inspect external files. The case input and output below are the complete admissible record. Grade whether the output itself supplies the evidence required by the rubric; do not independently verify its factual claims against a repository.

## Failure mode being checked
{failure_mode}

## Rubric
{rubric}

## Case input (what the system under test received)
{case_input}

## Output under evaluation
{output}

## Instructions
1. Reason step by step about whether the output exhibits the failure mode, citing specific parts of the output.
2. Then, on the FINAL line of your reply, return exactly one JSON object and nothing after it:
{{"verdict": "pass" | "fail" | "unknown", "reason": "<one sentence>"}}

"pass" = the failure mode is NOT present. "fail" = it IS present. Use "unknown" only if the rubric genuinely cannot be applied to this output (e.g. the output is empty or the rubric presupposes content that is absent) — do not use "unknown" to avoid a hard call."""


class GradingError(Exception):
    pass


def _json_path(obj, path: str):
    """Dot-path lookup into parsed JSON ('' or '.' = whole object)."""
    if path in ("", "."):
        return obj
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise GradingError(f"path '{path}' not found in output JSON")
    return cur


def _parse_output_json(output: str):
    text = output.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1] if "\n" in text else text
        text = text.rsplit("```", 1)[0].strip() if "```" in text else text.strip()
    return json.loads(text)


_TYPE_MAP = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "object": dict,
    "array": list,
}


def run_deterministic_check(check: dict, output: str) -> tuple[bool, str]:
    """Returns (passed, detail). Raises GradingError on malformed checks."""
    kind = check.get("kind")

    if kind == "json_valid":
        try:
            _parse_output_json(output)
            return True, "valid JSON"
        except (json.JSONDecodeError, ValueError) as exc:
            return False, f"invalid JSON: {exc}"

    if kind == "json_schema":
        try:
            obj = _parse_output_json(output)
        except (json.JSONDecodeError, ValueError) as exc:
            return False, f"invalid JSON: {exc}"
        if not isinstance(obj, dict):
            return False, "output JSON is not an object"
        for key in check.get("required", []):
            if key not in obj:
                return False, f"missing required key '{key}'"
        for key, tname in (check.get("types") or {}).items():
            if key in obj:
                expected = _TYPE_MAP.get(tname)
                if expected is None:
                    raise GradingError(f"json_schema: unknown type '{tname}'")
                if isinstance(obj[key], bool) and tname in ("number", "integer"):
                    return False, f"key '{key}' is boolean, expected {tname}"
                if not isinstance(obj[key], expected):
                    return False, f"key '{key}' is {type(obj[key]).__name__}, expected {tname}"
        if "allowed" in check:
            allowed = set(check["allowed"])
            unexpected = sorted(set(obj) - allowed)
            if unexpected:
                return False, f"unexpected top-level keys: {', '.join(unexpected)}"
        return True, "schema ok"

    if kind == "exact":
        return (output.strip() == check["value"], "exact match" if output.strip() == check["value"] else "no exact match")

    if kind in ("contains", "not_contains"):
        haystack, needle = output, check["value"]
        if not check.get("case_sensitive", False):
            haystack, needle = haystack.lower(), needle.lower()
        found = needle in haystack
        if kind == "contains":
            return found, f"'{check['value']}' {'found' if found else 'NOT found'}"
        return (not found), f"'{check['value']}' {'present (forbidden)' if found else 'absent'}"

    if kind == "regex":
        found = re.search(check["pattern"], output, re.DOTALL) is not None
        return found, f"pattern {'matched' if found else 'did not match'}"

    if kind == "numeric_band":
        try:
            obj = _parse_output_json(output)
            value = _json_path(obj, check.get("path", ""))
            value = float(value)
        except (json.JSONDecodeError, ValueError, TypeError, GradingError) as exc:
            return False, f"could not extract numeric '{check.get('path')}': {exc}"
        lo, hi = check.get("min"), check.get("max")
        if lo is not None and value < lo:
            return False, f"{value} < min {lo}"
        if hi is not None and value > hi:
            return False, f"{value} > max {hi}"
        return True, f"{value} in band [{lo}, {hi}]"

    if kind == "length_band":
        n = len(output)
        lo, hi = check.get("min_chars"), check.get("max_chars")
        if lo is not None and n < lo:
            return False, f"{n} chars < min {lo}"
        if hi is not None and n > hi:
            return False, f"{n} chars > max {hi}"
        return True, f"{n} chars in band"

    raise GradingError(f"unknown deterministic check kind: {kind}")


# --------------------------------------------------------------------------
# LLM judge (subscription CLI per ADR-0036)
# --------------------------------------------------------------------------

def build_judge_prompt(check: dict, case_input, output: str) -> str:
    return JUDGE_PROMPT_TEMPLATE.format(
        failure_mode=check.get("failure_mode", "unspecified"),
        rubric=check.get("rubric", ""),
        case_input=json.dumps(case_input, indent=2, ensure_ascii=False)[:6000],
        output=output[:12000],
    )


def parse_verdict(reply: str) -> tuple[str, str]:
    """Extract the last complete verdict object from a judge reply.

    Judges sometimes cite object-shaped source text or use braces inside the
    reason. A regex cannot distinguish those from JSON structure and used to
    turn otherwise valid verdicts into ``unknown``. Decode from every object
    start and prefer the candidate ending latest in the reply; for equal ends,
    prefer the outermost object.
    """
    text = reply or ""
    decoder = json.JSONDecoder()
    candidates: list[tuple[int, int, dict]] = []
    for start, char in enumerate(text):
        if char != "{":
            continue
        try:
            obj, consumed = decoder.raw_decode(text[start:])
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict):
            candidates.append((start + consumed, -start, obj))

    for _, _, obj in sorted(candidates, reverse=True):
        verdict = str(obj.get("verdict", "")).lower()
        if verdict in ("pass", "fail", "unknown"):
            return verdict, str(obj.get("reason", ""))[:500]
    return "unknown", "judge reply had no parseable verdict"


def build_verdict_repair_prompt(original_prompt: str, reply: str) -> str:
    return f"""Complete a malformed evaluator turn as one verdict object.
Do not call, invoke, simulate, or request tools. The original grading request below is the
complete admissible record. If the prior reply states a clear conclusion, normalize it. If
the prior reply only announces a tool check, verification step, or other unfinished work,
discard that preamble and grade the original request directly from the supplied case input
and output. Use unknown only when the original rubric genuinely cannot be applied to the
supplied output. Return exactly one JSON object and nothing else:
{{"verdict":"pass"|"fail"|"unknown","reason":"<one sentence>"}}

Original grading request:
{original_prompt[:12000]}

Prior evaluator reply:
{reply[:12000]}"""


def _codex_cmd(model: str) -> list[str]:
    cmd = [
        "codex",
        "-c",
        'approval_policy="untrusted"',
        "exec",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
    ]
    if model:
        cmd += ["--model", model]
    return cmd + ["-"]


def _claude_text_cmd(model: str, prompt: str) -> list[str]:
    return [
        "claude",
        "-p",
        "--tools",
        "",
        "--disable-slash-commands",
        "--model",
        model,
        prompt,
    ]


def call_judge_cli(
    prompt: str,
    model: str,
    timeout: int = 240,
    telemetry_context: dict | None = None,
) -> str:
    """One judge call with cross-provider fallback.

    One bounded retry on nonzero exit: the CLI intermittently exits 1 with
    no diagnostic (observed 2026-07-12); the error message includes stdout
    because the CLIs sometimes report there instead of stderr.
    """
    import time

    ctx = telemetry_context or {}
    primary = provider_for_model(model, default="claude")
    fallback = "codex" if primary == "claude" else "claude"
    fallback_judge = (ctx.get("fallback_models") or {}).get(fallback) or fallback_model(fallback)
    if primary == "claude":
        calls = [
            CliCall("claude", model, _claude_text_cmd(model, prompt),
                    input_text=prompt),
            CliCall("codex", fallback_judge, _codex_cmd(fallback_judge),
                    stdin_text=prompt, input_text=prompt, fallback_from="claude"),
        ]
    else:
        calls = [
            CliCall("codex", model, _codex_cmd(model),
                    stdin_text=prompt, input_text=prompt),
            CliCall("claude", fallback_judge,
                    _claude_text_cmd(fallback_judge, prompt),
                    input_text=prompt, fallback_from="codex"),
        ]
    try:
        return run_with_fallback(
            calls,
            timeout=timeout,
            role="judge",
            project=ctx.get("project", ""),
            prompt_id=ctx.get("prompt_id", ""),
            case_id=ctx.get("case_id", ""),
            trial=ctx.get("trial"),
        )
    except AllProvidersThrottled as exc:
        raise GradingError("THROTTLED: " + str(exc)) from exc
    except LLMCallError as exc:
        raise GradingError(str(exc)) from exc


def call_claude_judge_cli(prompt: str, model: str, timeout: int = 240) -> str:
    """Legacy single-provider judge transport, kept for focused tests."""
    cmd = _claude_text_cmd(model, prompt)
    last_err = ""
    for attempt in range(2):
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
        except FileNotFoundError as exc:
            raise GradingError("claude CLI not found on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise GradingError(f"judge timed out after {timeout}s") from exc
        if proc.returncode == 0:
            return proc.stdout
        diag = ((proc.stderr or "").strip() or (proc.stdout or "").strip())[-400:]
        if is_throttle(diag):
            raise GradingError(f"THROTTLED: {diag}")
        last_err = f"judge CLI exited {proc.returncode}: {diag or '<no output>'}"
        if attempt == 0:
            time.sleep(5)
    raise GradingError(last_err)


def run_judge_check(
    check: dict,
    case_input,
    output: str,
    model: str,
    trials: int = 1,
    caller=None,
    telemetry_context: dict | None = None,
) -> tuple[str, str]:
    """Run a judge check with optional self-consistency trials.

    Returns (verdict, detail). Majority vote across trials; ties and
    majority-unknown resolve to "unknown" (never silently to pass).
    caller resolves at call time (not as a default-arg binding) so tests
    and alternative judge transports can substitute it via the module.
    """
    if caller is None:
        caller = call_judge_cli
    prompt = build_judge_prompt(check, case_input, output)
    votes, reasons = [], []
    for _ in range(max(1, trials)):
        try:
            reply = caller(prompt, model, telemetry_context=telemetry_context)
        except TypeError:
            reply = caller(prompt, model)
        verdict, reason = parse_verdict(reply)
        if verdict == "unknown" and reason == "judge reply had no parseable verdict":
            repair_prompt = build_verdict_repair_prompt(prompt, reply)
            try:
                repaired = caller(
                    repair_prompt,
                    model,
                    telemetry_context=telemetry_context,
                )
            except TypeError:
                repaired = caller(repair_prompt, model)
            verdict, reason = parse_verdict(repaired)
        votes.append(verdict)
        reasons.append(reason)
    tally = {v: votes.count(v) for v in set(votes)}
    best = max(tally.items(), key=lambda kv: kv[1])
    if best[1] * 2 <= len(votes):  # no strict majority
        return "unknown", f"no majority across {len(votes)} trials: {tally}"
    return best[0], reasons[votes.index(best[0])]
