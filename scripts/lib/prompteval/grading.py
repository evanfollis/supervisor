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

_VERDICT_RE = re.compile(r'\{[^{}]*"verdict"[^{}]*\}')


def build_judge_prompt(check: dict, case_input, output: str) -> str:
    return JUDGE_PROMPT_TEMPLATE.format(
        failure_mode=check.get("failure_mode", "unspecified"),
        rubric=check.get("rubric", ""),
        case_input=json.dumps(case_input, indent=2, ensure_ascii=False)[:6000],
        output=output[:12000],
    )


def parse_verdict(reply: str) -> tuple[str, str]:
    """Extract the last verdict JSON from a judge reply."""
    matches = _VERDICT_RE.findall(reply or "")
    for candidate in reversed(matches):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        verdict = str(obj.get("verdict", "")).lower()
        if verdict in ("pass", "fail", "unknown"):
            return verdict, str(obj.get("reason", ""))[:500]
    return "unknown", "judge reply had no parseable verdict"


def call_judge_cli(prompt: str, model: str, timeout: int = 240) -> str:
    """One judge call via `claude -p`. Raises GradingError on CLI failure."""
    cmd = ["claude", "-p", "--model", model, prompt]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as exc:
        raise GradingError("claude CLI not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GradingError(f"judge timed out after {timeout}s") from exc
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()[:400]
        if re.search(r"rate.?limit|overloaded|429|usage limit", stderr, re.IGNORECASE):
            raise GradingError(f"THROTTLED: {stderr}")
        raise GradingError(f"judge CLI exited {proc.returncode}: {stderr}")
    return proc.stdout


def run_judge_check(
    check: dict,
    case_input,
    output: str,
    model: str,
    trials: int = 1,
    caller=None,
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
        reply = caller(prompt, model)
        verdict, reason = parse_verdict(reply)
        votes.append(verdict)
        reasons.append(reason)
    tally = {v: votes.count(v) for v in set(votes)}
    best = max(tally.items(), key=lambda kv: kv[1])
    if best[1] * 2 <= len(votes):  # no strict majority
        return "unknown", f"no majority across {len(votes)} trials: {tally}"
    return best[0], reasons[votes.index(best[0])]
