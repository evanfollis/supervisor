Reading additional input from stdin...
OpenAI Codex v0.123.0 (research preview)
--------
workdir: /opt/workspace/projects/skillfoundry/skillfoundry-harness
model: gpt-5.4
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019dbb7f-963f-70b3-8395-b041f894091e
--------
user
Adversarial review of /opt/workspace/projects/skillfoundry/skillfoundry-harness/src/skillfoundry_harness/discovery_adapter/.

You are a skeptical reviewer. Read the target file carefully. Then produce a review with exactly these three sections:

1. **Most dangerous assumption** — the claim that if wrong, produces the largest blast radius.
2. **Missing failure mode** — what the design does not account for that is likely to happen in practice.
3. **Boundary most likely to be collapsed in practice** — where the nominal separation will erode under real use.

Cite specific line numbers. Be terse and concrete. End with a 1-2 sentence overall verdict. Under 500 words total. Do not edit any files.
codex
Reviewing `src/skillfoundry_harness/discovery_adapter/` now. I’ll read the package files and trace the contract boundaries before writing a terse adversarial assessment.
exec
/bin/bash -lc 'rg --files src/skillfoundry_harness/discovery_adapter' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
src/skillfoundry_harness/discovery_adapter/__init__.py
src/skillfoundry_harness/discovery_adapter/migrate.py
src/skillfoundry_harness/discovery_adapter/emit.py
src/skillfoundry_harness/discovery_adapter/MAPPING.md

exec
/bin/bash -lc 'git status --short' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
?? .wrangler/

codex
The target is a small package with two code files and a mapping doc. I’m pulling line-numbered source now so the review is tied to the actual contract points rather than the package name alone.
exec
/bin/bash -lc 'nl -ba src/skillfoundry_harness/discovery_adapter/__init__.py' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
     1	"""Canon adapter — emits discovery-framework canon envelopes from skillfoundry
     2	markdown records under `skillfoundry-valuation-context/memory/venture/`.
     3	
     4	The skillfoundry venture layer (CriticalAssumption / Probe / Evidence /
     5	Decision) is a markdown-first ontology: each object is a markdown file with
     6	a backtick-keyed header list (see README.md in each subdirectory). This
     7	adapter parses the markdown, extracts the structured metadata, and emits
     8	canon envelopes conforming to the L1 spec at
     9	/opt/workspace/projects/context-repository/spec/discovery-framework/ (v0.1.0).
    10	
    11	The adapter is additive — the markdown files remain the authoring surface
    12	and are unchanged.
    13	
    14	Public API:
    15	    parse_assumption(md_path)  -> canon Claim dict
    16	    parse_probe(md_path)       -> (phase_transition, methodology_log) events
    17	    parse_evidence(md_path)    -> canon Evidence dict
    18	    parse_decision(md_path)    -> canon Decision dict
    19	    emit_policy_quality_note() -> canon Policy capturing the quality-field note
    20	"""
    21	
    22	from .emit import (
    23	    EMITTER,
    24	    INSTANCE_ID,
    25	    LAYER,
    26	    SPEC_VERSION,
    27	    AdapterParseError,
    28	    emit_policy_quality_note,
    29	    parse_assumption,
    30	    parse_decision,
    31	    parse_evidence,
    32	    parse_probe,
    33	)
    34	
    35	__all__ = [
    36	    "EMITTER",
    37	    "INSTANCE_ID",
    38	    "LAYER",
    39	    "SPEC_VERSION",
    40	    "AdapterParseError",
    41	    "emit_policy_quality_note",
    42	    "parse_assumption",
    43	    "parse_decision",
    44	    "parse_evidence",
    45	    "parse_probe",
    46	]

exec
/bin/bash -lc 'nl -ba src/skillfoundry_harness/discovery_adapter/migrate.py' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
     1	"""One-shot backfill: skillfoundry-valuation-context markdown → canon envelopes.
     2	
     3	Usage:
     4	    python -m skillfoundry_harness.discovery_adapter.migrate \\
     5	        --venture /opt/workspace/projects/skillfoundry/skillfoundry-valuation-context \\
     6	        [--dry-run]
     7	
     8	Reads every assumption, probe, evidence, decision markdown under
     9	`memory/venture/` and emits canon envelopes to `.canon/`.
    10	
    11	Validates every envelope against the L1 discovery-framework JSON Schemas at
    12	`/opt/workspace/projects/context-repository/spec/discovery-framework/schemas/`.
    13	
    14	Exit codes:
    15	    0 — all envelopes valid
    16	    1 — some envelopes failed validation
    17	    2 — adapter / schema loading failure
    18	"""
    19	
    20	from __future__ import annotations
    21	
    22	import argparse
    23	import json
    24	import sys
    25	import traceback
    26	from pathlib import Path
    27	
    28	from skillfoundry_harness.discovery_adapter.emit import (
    29	    QUALITY_POLICY_ID,
    30	    _DECISION_KIND_MAP,
    31	    emit_policy_quality_note,
    32	    parse_assumption,
    33	    parse_decision,
    34	    parse_evidence,
    35	    parse_header,
    36	    parse_probe,
    37	)
    38	
    39	
    40	DEFAULT_SCHEMA_DIR = Path(
    41	    "/opt/workspace/projects/context-repository/spec/discovery-framework/schemas"
    42	)
    43	
    44	
    45	def _load_schema_registry(schema_dir: Path):
    46	    try:
    47	        from jsonschema import Draft202012Validator
    48	        from referencing import Registry, Resource
    49	    except Exception as exc:  # pragma: no cover
    50	        print(f"FATAL: jsonschema + referencing required: {exc}", file=sys.stderr)
    51	        raise
    52	
    53	    resources = []
    54	    schemas: dict[str, dict] = {}
    55	    for p in sorted(schema_dir.glob("*.schema.json")):
    56	        with open(p) as f:
    57	            body = json.load(f)
    58	        schemas[p.name] = body
    59	        resources.append((body["$id"], Resource.from_contents(body)))
    60	    for fname, body in schemas.items():
    61	        resources.append((fname, Resource.from_contents(body)))
    62	
    63	    registry = Registry().with_resources(resources)
    64	    return {
    65	        body["title"]: Draft202012Validator(body, registry=registry)
    66	        for body in schemas.values()
    67	        if "title" in body
    68	    }
    69	
    70	
    71	def _validate(envelope: dict, validators: dict, object_type: str) -> list[str]:
    72	    v = validators.get(object_type)
    73	    if not v:
    74	        return [f"no validator for {object_type!r}"]
    75	    errors = sorted(v.iter_errors(envelope), key=lambda e: e.path)
    76	    return [
    77	        f"{'/'.join(str(p) for p in err.absolute_path)}: {err.message}"
    78	        for err in errors
    79	    ]
    80	
    81	
    82	def _write_envelope(envelope: dict, dest: Path, dry_run: bool) -> None:
    83	    if dry_run:
    84	        return
    85	    dest.parent.mkdir(parents=True, exist_ok=True)
    86	    tmp = dest.with_suffix(dest.suffix + ".tmp")
    87	    with open(tmp, "w") as f:
    88	        json.dump(envelope, f, indent=2, sort_keys=True)
    89	    tmp.replace(dest)
    90	
    91	
    92	def _canon_dir(venture_root: Path) -> Path:
    93	    d = venture_root / ".canon"
    94	    d.mkdir(parents=True, exist_ok=True)
    95	    for sub in ("claims", "evidence", "decisions", "event_log", "policies"):
    96	        (d / sub).mkdir(parents=True, exist_ok=True)
    97	    return d
    98	
    99	
   100	def migrate(venture_root: Path, schema_dir: Path, dry_run: bool) -> int:
   101	    venture_root = Path(venture_root)
   102	    memory_venture = venture_root / "memory" / "venture"
   103	    if not memory_venture.is_dir():
   104	        print(f"no memory/venture/ under {venture_root}", file=sys.stderr)
   105	        return 2
   106	
   107	    canon_root = _canon_dir(venture_root)
   108	    validators = _load_schema_registry(schema_dir)
   109	
   110	    counts = {"claims": [0, 0], "evidence": [0, 0],
   111	              "decisions": [0, 0], "events": [0, 0], "policies": [0, 0]}
   112	
   113	    # Pre-pass: build probe_id → decision_kind map from decision headers.
   114	    # Used so parse_probe() only emits the probe→promotion closure event when
   115	    # the matching Decision has kind=="promote". Headers-only read, non-fatal.
   116	    decision_kind_for_probe: dict[str, str] = {}
   117	    for dp in sorted((memory_venture / "decisions").glob("*.md")):
   118	        if dp.name.upper() == "README.MD" or dp.name.startswith("TEMPLATE"):
   119	            continue
   120	        try:
   121	            dh = parse_header(dp.read_text())
   122	            pid = dh.get("probe_id")
   123	            dt_raw = dh.get("decision_type", "")
   124	            if pid and dt_raw:
   125	                decision_kind_for_probe[pid] = _DECISION_KIND_MAP.get(dt_raw, "")
   126	        except Exception:
   127	            pass  # non-fatal; the main decisions pass will report the error
   128	
   129	    # 1) Policy (quality-note)
   130	    pol = emit_policy_quality_note()
   131	    errs = _validate(pol, validators, "Policy")
   132	    if errs:
   133	        counts["policies"][1] += 1
   134	        print(f"[POLICY] {QUALITY_POLICY_ID}: {errs}", file=sys.stderr)
   135	    else:
   136	        counts["policies"][0] += 1
   137	        _write_envelope(
   138	            pol, canon_root / "policies" / f"{QUALITY_POLICY_ID}.json", dry_run,
   139	        )
   140	
   141	    # 2) Claims
   142	    for p in sorted((memory_venture / "assumptions").glob("*.md")):
   143	        if p.name.upper() in {"README.MD"} or p.name.startswith("TEMPLATE"):
   144	            continue
   145	        try:
   146	            env = parse_assumption(p)
   147	        except Exception as exc:
   148	            counts["claims"][1] += 1
   149	            print(f"[CLAIM-PARSE] {p.name}: {exc}", file=sys.stderr)
   150	            continue
   151	        errs = _validate(env, validators, "Claim")
   152	        if errs:
   153	            counts["claims"][1] += 1
   154	            print(f"[CLAIM] {env.get('id', p.name)}: {errs}", file=sys.stderr)
   155	            continue
   156	        counts["claims"][0] += 1
   157	        _write_envelope(env, canon_root / "claims" / f"{env['id']}.json", dry_run)
   158	
   159	    # 3) Probes → EventLogEntry
   160	    for p in sorted((memory_venture / "probes").glob("*.md")):
   161	        if p.name.upper() == "README.MD" or p.name.startswith("TEMPLATE"):
   162	            continue
   163	        try:
   164	            # Look up the matching Decision kind so parse_probe only emits
   165	            # the probe→promotion event for actual promote decisions.
   166	            ph = parse_header(p.read_text())
   167	            dk = decision_kind_for_probe.get(ph.get("probe_id", ""))
   168	            events = parse_probe(p, decision_kind=dk)
   169	        except Exception as exc:
   170	            counts["events"][1] += 1
   171	            print(f"[PROBE-PARSE] {p.name}: {exc}", file=sys.stderr)
   172	            continue
   173	        for env in events:
   174	            errs = _validate(env, validators, "EventLogEntry")
   175	            if errs:
   176	                counts["events"][1] += 1
   177	                print(f"[EVENT] {env.get('id', p.name)}: {errs}", file=sys.stderr)
   178	                continue
   179	            counts["events"][0] += 1
   180	            _write_envelope(
   181	                env, canon_root / "event_log" / f"{env['id']}.json", dry_run,
   182	            )
   183	
   184	    # 4) Evidence
   185	    for p in sorted((memory_venture / "evidence").glob("*.md")):
   186	        if p.name.upper() == "README.MD" or p.name.startswith("TEMPLATE"):
   187	            continue
   188	        try:
   189	            env = parse_evidence(p)
   190	        except Exception as exc:
   191	            counts["evidence"][1] += 1
   192	            print(f"[EVIDENCE-PARSE] {p.name}: {exc}", file=sys.stderr)
   193	            continue
   194	        errs = _validate(env, validators, "Evidence")
   195	        if errs:
   196	            counts["evidence"][1] += 1
   197	            print(f"[EVIDENCE] {env.get('id', p.name)}: {errs}", file=sys.stderr)
   198	            continue
   199	        counts["evidence"][0] += 1
   200	        _write_envelope(env, canon_root / "evidence" / f"{env['id']}.json", dry_run)
   201	
   202	    # 5) Decisions
   203	    for p in sorted((memory_venture / "decisions").glob("*.md")):
   204	        if p.name.upper() == "README.MD" or p.name.startswith("TEMPLATE"):
   205	            continue
   206	        try:
   207	            env = parse_decision(p)
   208	        except Exception as exc:
   209	            counts["decisions"][1] += 1
   210	            print(f"[DECISION-PARSE] {p.name}: {exc}", file=sys.stderr)
   211	            continue
   212	        errs = _validate(env, validators, "Decision")
   213	        if errs:
   214	            counts["decisions"][1] += 1
   215	            print(f"[DECISION] {env.get('id', p.name)}: {errs}", file=sys.stderr)
   216	            continue
   217	        counts["decisions"][0] += 1
   218	        _write_envelope(env, canon_root / "decisions" / f"{env['id']}.json", dry_run)
   219	
   220	    total_bad = sum(v[1] for v in counts.values())
   221	    mode = "dry-run" if dry_run else "write"
   222	    parts = ", ".join(
   223	        f"{k}: {v[0]} ok / {v[1]} bad" for k, v in counts.items()
   224	    )
   225	    print(f"[{mode}] {parts}")
   226	    return 0 if total_bad == 0 else 1
   227	
   228	
   229	def main() -> int:
   230	    ap = argparse.ArgumentParser(description=__doc__)
   231	    ap.add_argument(
   232	        "--venture", type=Path,
   233	        default=Path(
   234	            "/opt/workspace/projects/skillfoundry/skillfoundry-valuation-context"
   235	        ),
   236	    )
   237	    ap.add_argument("--schemas", type=Path, default=DEFAULT_SCHEMA_DIR)
   238	    ap.add_argument("--dry-run", action="store_true")
   239	    args = ap.parse_args()
   240	
   241	    try:
   242	        return migrate(args.venture, args.schemas, args.dry_run)
   243	    except Exception:
   244	        traceback.print_exc()
   245	        return 2
   246	
   247	
   248	if __name__ == "__main__":
   249	    sys.exit(main())

exec
/bin/bash -lc 'nl -ba src/skillfoundry_harness/discovery_adapter/emit.py' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
     1	"""Parse skillfoundry venture markdown → canon envelopes.
     2	
     3	All four object types (CriticalAssumption, Probe, Evidence, Decision) use the
     4	same header shape: a markdown H1 title followed by a bulleted list of
     5	`- ``key``: ``value``` pairs, with optional prose sections below. This
     6	adapter extracts the header dict and maps to canon envelopes per MAPPING.md.
     7	
     8	No I/O — the caller writes envelopes to `.canon/` and runs the validator.
     9	"""
    10	
    11	from __future__ import annotations
    12	
    13	import hashlib
    14	import re
    15	from datetime import datetime, timezone
    16	from pathlib import Path
    17	from typing import Any
    18	
    19	
    20	class AdapterParseError(ValueError):
    21	    """Raised when a markdown file contains a value the adapter cannot map
    22	    unambiguously to a canon enum. Callers should log this as a friction
    23	    event and skip the file rather than emitting a coerced envelope."""
    24	
    25	
    26	def _resolve_enum(raw: str, mapping: dict[str, str],
    27	                  field_name: str, source: "Path | str") -> str:
    28	    result = mapping.get(raw)
    29	    if result is None:
    30	        raise AdapterParseError(
    31	            f"{source}: unknown {field_name} value {raw!r}; "
    32	            f"valid values: {sorted(mapping)}"
    33	        )
    34	    return result
    35	
    36	
    37	SPEC_VERSION = "0.1.0"
    38	EMITTER = "L3:skillfoundry"
    39	LAYER = "L3"
    40	INSTANCE_ID = "skillfoundry-valuation-context"
    41	
    42	QUALITY_POLICY_ID = "skillfoundry.evidence_quality_note"
    43	QUALITY_POLICY_VERSION = "1"
    44	
    45	
    46	# --------------------------------------------------------------------------
    47	# Markdown header parser
    48	# --------------------------------------------------------------------------
    49	
    50	
    51	_HEADER_LINE = re.compile(
    52	    r"^\-\s+`(?P<key>[a-z_]+)`\s*:\s*`?(?P<val>[^`\n]*)`?\s*$"
    53	)
    54	_LIST_CONTINUATION = re.compile(r"^\s+\-\s+`?(?P<val>[^`\n]*)`?\s*$")
    55	
    56	
    57	def parse_header(md_text: str) -> dict[str, Any]:
    58	    """Extract `key: value` pairs from the markdown H1-adjacent bulleted list.
    59	
    60	    Supports list-valued fields (evidence_refs in decisions). Stops at the
    61	    first blank-after-list or the first H2 (`## `).
    62	
    63	    Returns a dict; unknown keys pass through.
    64	    """
    65	    lines = md_text.splitlines()
    66	    out: dict[str, Any] = {}
    67	    current_key: str | None = None
    68	    in_block = False
    69	
    70	    for line in lines:
    71	        # Start of header block: first bulleted key-value line
    72	        m = _HEADER_LINE.match(line)
    73	        if m:
    74	            in_block = True
    75	            current_key = m.group("key")
    76	            val = m.group("val").strip()
    77	            # Bare "(open)" / "(empty)" / etc. become None
    78	            if val in ("", "(open)", "(empty)", "(n/a)", "null"):
    79	                val = None
    80	            # Line with no value content (just the key and a colon on its own)
    81	            out[current_key] = val
    82	            continue
    83	
    84	        # Continuation inside a list-valued key
    85	        if in_block and current_key:
    86	            cm = _LIST_CONTINUATION.match(line)
    87	            if cm:
    88	                v = cm.group("val").strip()
    89	                if not isinstance(out.get(current_key), list):
    90	                    # Convert from singleton to list if needed
    91	                    prev = out[current_key]
    92	                    out[current_key] = [] if prev in (None, "", "(empty)") else [prev]
    93	                out[current_key].append(v)
    94	                continue
    95	
    96	        # Blank line during the block: keep going if the next line is a
    97	        # continuation or another header entry; break otherwise.
    98	        if in_block and line.strip() == "":
    99	            # Peek ahead isn't easy in a for-loop; just continue. The break
   100	            # is handled by the H2 check below.
   101	            continue
   102	
   103	        # End the block on H2
   104	        if in_block and line.startswith("## "):
   105	            break
   106	        if in_block and not line.startswith("-") and not line.startswith(" ") and line.strip() != "":
   107	            # First non-list non-blank non-H2 prose line ends the block.
   108	            break
   109	
   110	    return out
   111	
   112	
   113	# --------------------------------------------------------------------------
   114	# Envelope helpers
   115	# --------------------------------------------------------------------------
   116	
   117	
   118	def _iso(ts: str | datetime | None, default: str | None = None) -> str:
   119	    if ts is None and default is None:
   120	        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
   121	    if ts is None:
   122	        return default  # type: ignore[return-value]
   123	    if isinstance(ts, str):
   124	        try:
   125	            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
   126	        except ValueError:
   127	            return ts  # already in canonical form we can't reparse; trust
   128	    else:
   129	        dt = ts
   130	    if dt.tzinfo is None:
   131	        dt = dt.replace(tzinfo=timezone.utc)
   132	    return dt.isoformat().replace("+00:00", "Z")
   133	
   134	
   135	def _sha256_file(path: Path) -> str:
   136	    h = hashlib.sha256()
   137	    with open(path, "rb") as f:
   138	        for chunk in iter(lambda: f.read(65536), b""):
   139	            h.update(chunk)
   140	    return f"sha256:{h.hexdigest()}"
   141	
   142	
   143	def _sha256_str(s: str) -> str:
   144	    return f"sha256:{hashlib.sha256(s.encode('utf-8')).hexdigest()}"
   145	
   146	
   147	def _default_exposure() -> dict[str, Any]:
   148	    """Skillfoundry venture probes run with negligible operational exposure
   149	    pre-transaction. Capital-at-risk is bounded by the probe's build cost
   150	    (already sunk); external exposure is information, not capital."""
   151	    return {
   152	        "capital_at_risk": 0,
   153	        "reversibility": "reversible",
   154	        "correlation_tags": ["skillfoundry-valuation"],
   155	        "time_to_realization": "P14D",
   156	        "blast_radius": "local",
   157	    }
   158	
   159	
   160	def _common_envelope(object_type: str, id_: str, emitted_at: str,
   161	                     role_declared_at: str | None = None,
   162	                     binding: str = "binding") -> dict[str, Any]:
   163	    return {
   164	        "id": id_,
   165	        "spec_version": SPEC_VERSION,
   166	        "object_type": object_type,
   167	        "emitted_at": emitted_at,
   168	        "emitter": EMITTER,
   169	        "layer": LAYER,
   170	        "roles": [object_type],
   171	        "role_declared_at": role_declared_at or emitted_at,
   172	        "binding": binding,
   173	        "sources": [],
   174	        "instance_id": INSTANCE_ID,
   175	    }
   176	
   177	
   178	def _artifact_pointer(md_path: Path, uri_base: str | None = None) -> dict[str, Any]:
   179	    md_path = Path(md_path)
   180	    uri = uri_base or f"file://{md_path}"
   181	    return {
   182	        "uri": uri,
   183	        "content_hash": _sha256_file(md_path),
   184	        "version": str(int(md_path.stat().st_mtime)),
   185	        "media_type": "text/markdown",
   186	    }
   187	
   188	
   189	# --------------------------------------------------------------------------
   190	# CriticalAssumption → Claim
   191	# --------------------------------------------------------------------------
   192	
   193	
   194	def parse_assumption(md_path: Path | str) -> dict[str, Any]:
   195	    """skillfoundry CriticalAssumption markdown → canon Claim envelope.
   196	
   197	    Canon Claim has a single `statement`. Skillfoundry assumptions carry
   198	    three component claims (problem_claim, economic_claim, channel_claim)
   199	    which together form one buyer story. We use `problem_claim` as the
   200	    primary statement (it is the falsifiable commercial claim); the
   201	    economic and channel claims are preserved in the markdown artifact
   202	    via hash-bound ArtifactPointer.
   203	
   204	    The `falsification_rule` prose becomes the sole entry in
   205	    `falsification_criteria`.
   206	    """
   207	    md_path = Path(md_path)
   208	    header = parse_header(md_path.read_text())
   209	
   210	    if "assumption_id" not in header or "problem_claim" not in header:
   211	        raise ValueError(f"{md_path}: missing assumption_id or problem_claim")
   212	
   213	    emitted = _iso(header.get("created_at"))
   214	    role_at = emitted
   215	    envelope = _common_envelope(
   216	        "Claim", header["assumption_id"], emitted, role_at,
   217	    )
   218	    envelope["statement"] = header["problem_claim"]
   219	    envelope["falsification_criteria"] = [
   220	        header.get("falsification_rule", "(no falsification rule provided)")
   221	    ]
   222	    envelope["thresholds"] = {}
   223	    envelope["exposure"] = _default_exposure()
   224	    envelope["artifact"] = _artifact_pointer(md_path)
   225	    return envelope
   226	
   227	
   228	# --------------------------------------------------------------------------
   229	# Probe → EventLogEntry (phase_transition + methodology_log)
   230	# --------------------------------------------------------------------------
   231	
   232	
   233	def parse_probe(md_path: Path | str,
   234	                decision_kind: str | None = None) -> list[dict[str, Any]]:
   235	    """Probe markdown → list of EventLogEntry envelopes.
   236	
   237	    Emits:
   238	      1. phase_transition (draft → probe) at probe start
   239	      2. methodology_log with ArtifactPointer to the probe markdown
   240	      3. phase_transition (probe → promotion) ONLY when the caller passes
   241	         decision_kind="promote" for a closed probe
   242	
   243	    The L1 schema's phase_transition only models three phases: draft, probe,
   244	    promotion. Killed/pivoted/closed probes do not get a closure event — the
   245	    Decision envelope itself records the outcome. Passing decision_kind for a
   246	    non-promote close therefore emits nothing extra.
   247	
   248	    Returns a list (not single envelope) because a probe emits multiple events.
   249	    """
   250	    md_path = Path(md_path)
   251	    header = parse_header(md_path.read_text())
   252	
   253	    if "probe_id" not in header or "assumption_id" not in header:
   254	        raise ValueError(f"{md_path}: missing probe_id or assumption_id")
   255	
   256	    probe_id = header["probe_id"]
   257	    claim_id = header["assumption_id"]
   258	    started = _iso(header.get("started_at"))
   259	    ended_raw = header.get("ended_at")
   260	    ended = _iso(ended_raw) if ended_raw else None
   261	
   262	    artifact = _artifact_pointer(md_path)
   263	    events: list[dict[str, Any]] = []
   264	
   265	    # 1. phase_transition draft → probe
   266	    pt1 = _common_envelope(
   267	        "EventLogEntry", f"pt-{probe_id}-draft-probe", started, started,
   268	    )
   269	    pt1["event_kind"] = "phase_transition"
   270	    pt1["subject_id"] = claim_id
   271	    pt1["phase_transition"] = {
   272	        "claim_id": claim_id,
   273	        "from_phase": "draft",
   274	        "to_phase": "probe",
   275	    }
   276	    events.append(pt1)
   277	
   278	    # 2. methodology_log at probe entry (canon.md Phase Invariants require this)
   279	    ml = _common_envelope(
   280	        "EventLogEntry", f"ml-{probe_id}", started, started,
   281	    )
   282	    ml["event_kind"] = "methodology_log"
   283	    ml["subject_id"] = claim_id
   284	    ml["methodology_log"] = {
   285	        "artifact": artifact,
   286	        "summary": header.get("probe_type", "manual probe"),
   287	    }
   288	    events.append(ml)
   289	
   290	    # 3. phase_transition probe → promotion, only when caller confirms promote
   291	    status = header.get("status")
   292	    if status == "closed" and ended and decision_kind == "promote":
   293	        pt2 = _common_envelope(
   294	            "EventLogEntry", f"pt-{probe_id}-probe-promotion", ended, ended,
   295	        )
   296	        pt2["event_kind"] = "phase_transition"
   297	        pt2["subject_id"] = claim_id
   298	        pt2["phase_transition"] = {
   299	            "claim_id": claim_id,
   300	            "from_phase": "probe",
   301	            "to_phase": "promotion",
   302	        }
   303	        events.append(pt2)
   304	
   305	    return events
   306	
   307	
   308	# --------------------------------------------------------------------------
   309	# Evidence → Evidence
   310	# --------------------------------------------------------------------------
   311	
   312	
   313	_TIER_ALIASES = {
   314	    # Skillfoundry writes the same 4 strings canon uses natively.
   315	    "internal_operational": "internal_operational",
   316	    "external_conversation": "external_conversation",
   317	    "external_commitment": "external_commitment",
   318	    "external_transaction": "external_transaction",
   319	}
   320	
   321	
   322	_POLARITY_MAP = {
   323	    "supports_assumption": "supports",
   324	    "contradicts_assumption": "contradicts",
   325	    "neutral": "neutral",
   326	    # Looser values observed in real files — all map to neutral because they
   327	    # describe probe readiness/activation rather than assumption polarity.
   328	    "lane_activation_only": "neutral",
   329	    "lane_activation": "neutral",
   330	    "activation_only": "neutral",
   331	    "operational_readiness_only": "neutral",
   332	}
   333	
   334	
   335	def parse_evidence(md_path: Path | str) -> dict[str, Any]:
   336	    """skillfoundry Evidence markdown → canon Evidence envelope."""
   337	    md_path = Path(md_path)
   338	    header = parse_header(md_path.read_text())
   339	
   340	    for required in ("evidence_id", "assumption_id", "evidence_class"):
   341	        if required not in header:
   342	            raise ValueError(f"{md_path}: missing {required}")
   343	
   344	    emitted = _iso(header.get("observed_at"))
   345	    envelope = _common_envelope(
   346	        "Evidence", header["evidence_id"], emitted, emitted,
   347	    )
   348	    envelope["claim_id"] = header["assumption_id"]
   349	    envelope["evidence_type"] = header.get("source_type", "unspecified")
   350	
   351	    tier_raw = header["evidence_class"]
   352	    envelope["tier"] = _resolve_enum(tier_raw, _TIER_ALIASES, "evidence_class", md_path)
   353	
   354	    supports_raw = header.get("supports", "neutral")
   355	    envelope["polarity"] = _resolve_enum(supports_raw, _POLARITY_MAP, "supports", md_path)
   356	    envelope["observed_at"] = emitted
   357	    envelope["artifact"] = _artifact_pointer(md_path)
   358	    return envelope
   359	
   360	
   361	# --------------------------------------------------------------------------
   362	# Decision → Decision
   363	# --------------------------------------------------------------------------
   364	
   365	
   366	_DECISION_KIND_MAP = {
   367	    "continue": "continue",
   368	    "tighten": "continue",  # skillfoundry-specific variant; flagged in rationale
   369	    "pivot": "pivot",
   370	    "pause": "continue",  # non-terminal pause preserves the claim; rationale carries the nuance
   371	    "kill": "kill",
   372	    "promote": "promote",
   373	}
   374	
   375	
   376	def parse_decision(md_path: Path | str) -> dict[str, Any]:
   377	    """skillfoundry Decision markdown → canon Decision envelope.
   378	
   379	    Skillfoundry's `decision_type` enum is richer than canon's (tighten,
   380	    pause); the mapping folds them into the closest canon kind and
   381	    preserves the nuance in `rationale` with an explicit "[skillfoundry-
   382	    type=tighten]" prefix marker.
   383	    """
   384	    md_path = Path(md_path)
   385	    text = md_path.read_text()
   386	    header = parse_header(text)
   387	
   388	    for required in ("decision_id", "assumption_id", "decision_type", "timestamp"):
   389	        if required not in header:
   390	            raise ValueError(f"{md_path}: missing {required}")
   391	
   392	    emitted = _iso(header["timestamp"])
   393	    decision_type_raw = header["decision_type"]
   394	    kind = _resolve_enum(decision_type_raw, _DECISION_KIND_MAP, "decision_type", md_path)
   395	
   396	    envelope = _common_envelope(
   397	        "Decision", header["decision_id"], emitted, emitted,
   398	    )
   399	    envelope["kind"] = kind
   400	    envelope["candidate_claims"] = [header["assumption_id"]]
   401	    envelope["chosen_claim_id"] = header["assumption_id"]
   402	
   403	    ev_refs = header.get("evidence_refs")
   404	    if isinstance(ev_refs, str):
   405	        ev_refs = [ev_refs] if ev_refs else []
   406	    elif ev_refs is None:
   407	        ev_refs = []
   408	    envelope["cited_evidence"] = ev_refs
   409	
   410	    rationale = header.get("rationale", "(no rationale provided)")
   411	    if decision_type_raw != kind:
   412	        rationale = f"[skillfoundry-type={decision_type_raw}] {rationale}"
   413	    envelope["rationale"] = rationale
   414	
   415	    envelope["policies_in_force"] = [
   416	        {
   417	            "policy_id": QUALITY_POLICY_ID,
   418	            "version": QUALITY_POLICY_VERSION,
   419	            "class": "operational",
   420	        }
   421	    ]
   422	    envelope["exposure"] = _default_exposure()
   423	
   424	    if kind == "promote":
   425	        # skillfoundry decisions don't carry an explicit promotion_id;
   426	        # synthesize one from the decision id.
   427	        envelope["promotion_id"] = f"prom-{header['decision_id']}"
   428	
   429	    return envelope
   430	
   431	
   432	# --------------------------------------------------------------------------
   433	# Policy — quality-field note
   434	# --------------------------------------------------------------------------
   435	
   436	
   437	def emit_policy_quality_note(effective_from: str | datetime | None = None) -> dict[str, Any]:
   438	    """Policy capturing the semantics of skillfoundry's evidence_quality
   439	    field (weak|moderate|strong), which has no direct canon field.
   440	
   441	    canon.Evidence has `tier` (bindingness axis) but no quality axis. The
   442	    quality label is preserved in the markdown artifact via ArtifactPointer;
   443	    this Policy documents that interpretation so consumers can find it
   444	    mechanically.
   445	    """
   446	    ts = effective_from or datetime.now(timezone.utc)
   447	    emitted = _iso(ts) if not isinstance(ts, str) else ts
   448	
   449	    envelope = _common_envelope(
   450	        "Policy", QUALITY_POLICY_ID, emitted, emitted,
   451	    )
   452	    # Policy schema forbids instance_id
   453	    envelope.pop("instance_id", None)
   454	    envelope["class"] = "operational"
   455	    envelope["scope"] = f"L3:{INSTANCE_ID}"
   456	    envelope["field_path"] = "evidence.quality_label"
   457	    envelope["value"] = {
   458	        "location": "artifact body of each Evidence envelope",
   459	        "values": ["weak", "moderate", "strong"],
   460	        "note": (
   461	            "Skillfoundry markdown Evidence records carry an "
   462	            "`evidence_quality` label that canon does not model directly "
   463	            "(canon.Evidence has `tier` for bindingness, not for quality). "
   464	            "The label is preserved in the ArtifactPointer-referenced "
   465	            "markdown and can be extracted by re-parsing the artifact if "
   466	            "needed. Promoting quality to a first-class canon field "
   467	            "requires a canon spec bump (v0.2.0)."
   468	        ),
   469	    }
   470	    envelope["version"] = QUALITY_POLICY_VERSION
   471	    envelope["issuer"] = EMITTER
   472	    envelope["amendment_authority"] = [EMITTER, "human:evan"]
   473	    envelope["ratification_rule"] = {
   474	        "kind": "principal_signoff",
   475	        "signatories": ["human:evan"],
   476	    }
   477	    envelope["rollback_rule"] = {
   478	        "rules": [
   479	            {
   480	                "id": "canon_gains_quality_field",
   481	                "condition": (
   482	                    "canon.spec_version advances to include an Evidence.quality "
   483	                    "field, at which point this Policy's note is obsolete"
   484	                ),
   485	            }
   486	        ],
   487	        "precedence": ["canon_gains_quality_field"],
   488	    }
   489	    envelope["provenance"] = [
   490	        {"version": QUALITY_POLICY_VERSION, "effective_from": emitted}
   491	    ]
   492	    envelope["effective_from"] = emitted
   493	    envelope["effective_until"] = None
   494	    return envelope

exec
/bin/bash -lc 'nl -ba src/skillfoundry_harness/discovery_adapter/MAPPING.md' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
     1	# Skillfoundry → canon mapping (v1)
     2	
     3	This document explains the skillfoundry-valuation-context markdown → L1
     4	discovery-framework canon mapping implemented in `emit.py`.
     5	
     6	Canon spec: **0.1.0** (`/opt/workspace/projects/context-repository/spec/discovery-framework/`).
     7	
     8	## Object mappings
     9	
    10	### CriticalAssumption → Claim
    11	
    12	Skillfoundry assumptions carry three component claims
    13	(`problem_claim`, `economic_claim`, `channel_claim`). Canon Claim has a
    14	single `statement`. Mapping: **statement = problem_claim** (the falsifiable
    15	commercial claim). The other two are preserved in the markdown artifact via
    16	hash-bound ArtifactPointer — downstream consumers who need the full buyer
    17	story re-parse the markdown.
    18	
    19	| Markdown key | Canon Claim field | Transform |
    20	|---|---|---|
    21	| `assumption_id` | `id` | identity (prose slug) |
    22	| `problem_claim` | `statement` | identity |
    23	| `falsification_rule` | `falsification_criteria` | wrap as `[str]` |
    24	| `created_at` | `emitted_at`, `role_declared_at` | ISO normalize |
    25	| `status` | (not on Claim) | emitted as EventLogEntry.phase_transition |
    26	| `economic_claim`, `channel_claim`, `buyer_role`, `owner`, `next_probe_id` | (not mapped) | preserved in artifact |
    27	
    28	**Adapter-supplied canon fields:**
    29	`spec_version=0.1.0`, `object_type=Claim`, `emitter=L3:skillfoundry`,
    30	`layer=L3`, `roles=[Claim]`, `binding=binding`, `sources=[]`,
    31	`exposure=_default_exposure()`, `artifact=ArtifactPointer` (sha256 of file),
    32	`instance_id=skillfoundry-valuation-context`.
    33	
    34	### Probe → EventLogEntry (multiple)
    35	
    36	Skillfoundry probes are operational events, not canon objects. Each probe
    37	emits up to three canon EventLogEntry envelopes:
    38	
    39	1. `phase_transition` (draft → probe) at `started_at`
    40	2. `methodology_log` with ArtifactPointer to the probe markdown (per
    41	   canon.md Phase Invariants: "Methodology log entry required on entry to probe")
    42	3. `phase_transition` (probe → promotion) at `ended_at`, only when `status=closed`
    43	
    44	| Markdown key | Canon field | Notes |
    45	|---|---|---|
    46	| `probe_id` | event id prefix (`pt-<probe_id>-…`, `ml-<probe_id>`) | |
    47	| `assumption_id` | `phase_transition.claim_id` + `subject_id` | |
    48	| `started_at` | first event `emitted_at` + `role_declared_at` | |
    49	| `ended_at` | second-transition `emitted_at` (if closed) | |
    50	| `probe_type` | `methodology_log.summary` | free-form summary |
    51	
    52	Probes fields not mapped (`probe_type` enum, `artifact_class`,
    53	`offer_presented`, `target_persona`, `target_evidence_class`,
    54	`minimum_evidence_quality`, `success_rule`, `falsification_rule`, `owner`)
    55	live in the artifact body.
    56	
    57	**Outlier**: `probes/preflight-distribution-signal.md` uses a prose/bold
    58	format rather than the canonical backtick-key-value header and does NOT
    59	parse. Skillfoundry PM action item: reformat that file to match the
    60	canonical probe header shape used by
    61	`probes/launch-compliance-intelligence-manual-offer.md` and
    62	`probes/launchpad-lint-agenticmarket-live-listing.md`.
    63	
    64	### Evidence → Evidence
    65	
    66	Skillfoundry's `evidence_class` enum is **identical** to canon's `tier`
    67	enum — canon inherited the 4-tier hierarchy from skillfoundry's earlier
    68	work. Direct map.
    69	
    70	| Markdown key | Canon Evidence field | Transform |
    71	|---|---|---|
    72	| `evidence_id` | `id` | identity |
    73	| `assumption_id` | `claim_id` | identity |
    74	| `evidence_class` | `tier` | identity (enum alias table in `_TIER_ALIASES`) |
    75	| `source_type` | `evidence_type` | identity (domain-owned free-form string) |
    76	| `supports` | `polarity` | `supports_assumption→supports`, `contradicts_assumption→contradicts`, `lane_activation_only→neutral`, else `neutral` |
    77	| `observed_at` | `emitted_at`, `observed_at`, `role_declared_at` | ISO normalize |
    78	
    79	Fields preserved in artifact only: `evidence_quality` (weak|moderate|
    80	strong), `source_identity`, `summary`, `raw_pointer`, `confidence`.
    81	
    82	### Decision → Decision
    83	
    84	Skillfoundry's `decision_type` enum is richer than canon's; the mapping
    85	folds skillfoundry-specific types into the closest canon kind and
    86	prepends a `[skillfoundry-type=<raw>]` marker to `rationale` so the
    87	nuance is mechanically discoverable.
    88	
    89	| `decision_type` | canon `kind` |
    90	|---|---|
    91	| `continue` | `continue` |
    92	| `tighten` | `continue` (rationale flagged `[skillfoundry-type=tighten]`) |
    93	| `pivot` | `pivot` |
    94	| `pause` | `continue` (rationale flagged `[skillfoundry-type=pause]`) |
    95	| `kill` | `kill` |
    96	| `promote` | `promote` |
    97	
    98	| Markdown key | Canon Decision field | Transform |
    99	|---|---|---|
   100	| `decision_id` | `id` | identity |
   101	| `assumption_id` | `candidate_claims[0]`, `chosen_claim_id` | identity |
   102	| `decision_type` | `kind` | via table above |
   103	| `evidence_refs` | `cited_evidence` | list pass-through |
   104	| `rationale` | `rationale` | prepended with type-marker if lossy |
   105	| `timestamp` | `emitted_at`, `role_declared_at` | ISO normalize |
   106	
   107	Adapter-supplied: `policies_in_force` references the quality-note Policy
   108	(`skillfoundry.evidence_quality_note` v1); `exposure` uses the default
   109	envelope; `promotion_id` synthesized as `prom-<decision_id>` when
   110	`kind=promote`.
   111	
   112	## Policy: the quality-field note
   113	
   114	Canon has no `quality` field on Evidence; skillfoundry's
   115	`evidence_quality` (weak|moderate|strong) is preserved in the artifact
   116	only. The adapter emits a Policy envelope documenting this so future
   117	consumers find the semantic locus mechanically.
   118	
   119	Rollback condition: canon spec gains a first-class quality field (spec
   120	v0.2.0+), at which point this Policy is obsolete and the adapter is
   121	updated to emit `Evidence.quality` directly.
   122	
   123	## Things deliberately not mapped
   124	
   125	- Skillfoundry's **promotion workflow** (`src/skillfoundry_harness/promotion.py`,
   126	  367 LOC of cryptographic memory-promotion) — that's a separate subsystem
   127	  (canonical-memory commit/approve/apply), distinct from canon Promotion.
   128	  Not touched by this adapter.
   129	- The **bundle layer** (`bundles/*.json`) — cross-repo coherence contracts;
   130	  canon doesn't model these.
   131	- `next_probe_id` and probe lineage — canon has no first-class
   132	  "claim-to-claim next-probe" edge. Lineage stays in the markdown.
   133	
   134	## Open questions (surfaced, not resolved)
   135	
   136	- **Assumption-as-three-claims**. Emitting three canon Claims per
   137	  skillfoundry assumption (problem/economic/channel) is architecturally
   138	  cleaner but canon has no native parent-child Claim link. Current choice
   139	  (one Claim with `statement=problem_claim`) is defensible but lossy. If
   140	  canon gains `related_claims[]` in a future version, revisit.
   141	- **Canon Promotion**. When a skillfoundry decision has `kind=promote`,
   142	  should the adapter also emit a canon Promotion envelope? Canon's
   143	  Promotion requires `external_validation` and `ceiling_check`; skillfoundry
   144	  decisions today don't carry structured external-validation attestation.
   145	  Deferred; see ADR-0026.

codex
I have the adapter code and mapping doc. One more pass through the surrounding tests will tell me whether the risky assumptions are acknowledged anywhere or currently left implicit.
exec
/bin/bash -lc 'rg -n "discovery_adapter|parse_probe|parse_decision|parse_evidence|parse_assumption|emit_policy_quality_note" tests src' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
src/skillfoundry_harness/discovery_adapter/__init__.py:15:    parse_assumption(md_path)  -> canon Claim dict
src/skillfoundry_harness/discovery_adapter/__init__.py:16:    parse_probe(md_path)       -> (phase_transition, methodology_log) events
src/skillfoundry_harness/discovery_adapter/__init__.py:17:    parse_evidence(md_path)    -> canon Evidence dict
src/skillfoundry_harness/discovery_adapter/__init__.py:18:    parse_decision(md_path)    -> canon Decision dict
src/skillfoundry_harness/discovery_adapter/__init__.py:19:    emit_policy_quality_note() -> canon Policy capturing the quality-field note
src/skillfoundry_harness/discovery_adapter/__init__.py:28:    emit_policy_quality_note,
src/skillfoundry_harness/discovery_adapter/__init__.py:29:    parse_assumption,
src/skillfoundry_harness/discovery_adapter/__init__.py:30:    parse_decision,
src/skillfoundry_harness/discovery_adapter/__init__.py:31:    parse_evidence,
src/skillfoundry_harness/discovery_adapter/__init__.py:32:    parse_probe,
src/skillfoundry_harness/discovery_adapter/__init__.py:41:    "emit_policy_quality_note",
src/skillfoundry_harness/discovery_adapter/__init__.py:42:    "parse_assumption",
src/skillfoundry_harness/discovery_adapter/__init__.py:43:    "parse_decision",
src/skillfoundry_harness/discovery_adapter/__init__.py:44:    "parse_evidence",
src/skillfoundry_harness/discovery_adapter/__init__.py:45:    "parse_probe",
src/skillfoundry_harness/discovery_adapter/migrate.py:4:    python -m skillfoundry_harness.discovery_adapter.migrate \\
src/skillfoundry_harness/discovery_adapter/migrate.py:28:from skillfoundry_harness.discovery_adapter.emit import (
src/skillfoundry_harness/discovery_adapter/migrate.py:31:    emit_policy_quality_note,
src/skillfoundry_harness/discovery_adapter/migrate.py:32:    parse_assumption,
src/skillfoundry_harness/discovery_adapter/migrate.py:33:    parse_decision,
src/skillfoundry_harness/discovery_adapter/migrate.py:34:    parse_evidence,
src/skillfoundry_harness/discovery_adapter/migrate.py:36:    parse_probe,
src/skillfoundry_harness/discovery_adapter/migrate.py:114:    # Used so parse_probe() only emits the probe→promotion closure event when
src/skillfoundry_harness/discovery_adapter/migrate.py:130:    pol = emit_policy_quality_note()
src/skillfoundry_harness/discovery_adapter/migrate.py:146:            env = parse_assumption(p)
src/skillfoundry_harness/discovery_adapter/migrate.py:164:            # Look up the matching Decision kind so parse_probe only emits
src/skillfoundry_harness/discovery_adapter/migrate.py:168:            events = parse_probe(p, decision_kind=dk)
src/skillfoundry_harness/discovery_adapter/migrate.py:189:            env = parse_evidence(p)
src/skillfoundry_harness/discovery_adapter/migrate.py:207:            env = parse_decision(p)
tests/test_discovery_adapter.py:6:`python -m skillfoundry_harness.discovery_adapter.migrate --dry-run`;
tests/test_discovery_adapter.py:16:from skillfoundry_harness.discovery_adapter import (
tests/test_discovery_adapter.py:18:    emit_policy_quality_note,
tests/test_discovery_adapter.py:19:    parse_assumption,
tests/test_discovery_adapter.py:20:    parse_decision,
tests/test_discovery_adapter.py:21:    parse_evidence,
tests/test_discovery_adapter.py:22:    parse_probe,
tests/test_discovery_adapter.py:104:def test_parse_assumption(fixtures):
tests/test_discovery_adapter.py:105:    c = parse_assumption(fixtures / "assumption.md")
tests/test_discovery_adapter.py:119:def test_parse_probe_emits_three_events_when_closed(fixtures):
tests/test_discovery_adapter.py:121:    events = parse_probe(fixtures / "probe.md")
tests/test_discovery_adapter.py:130:def test_parse_probe_closed_no_decision_kind_emits_two_events(fixtures, tmp_path):
tests/test_discovery_adapter.py:139:    events = parse_probe(p)
tests/test_discovery_adapter.py:143:def test_parse_probe_closed_with_promote_emits_three_events(fixtures, tmp_path):
tests/test_discovery_adapter.py:150:    events = parse_probe(p, decision_kind="promote")
tests/test_discovery_adapter.py:156:def test_parse_probe_closed_with_kill_emits_two_events(fixtures, tmp_path):
tests/test_discovery_adapter.py:164:    events = parse_probe(p, decision_kind="kill")
tests/test_discovery_adapter.py:168:def test_parse_probe_closed_with_pivot_emits_two_events(fixtures, tmp_path):
tests/test_discovery_adapter.py:175:    events = parse_probe(p, decision_kind="pivot")
tests/test_discovery_adapter.py:179:def test_parse_evidence_polarity_and_tier(fixtures):
tests/test_discovery_adapter.py:180:    e = parse_evidence(fixtures / "evidence.md")
tests/test_discovery_adapter.py:188:def test_parse_evidence_lane_activation_neutral(fixtures, tmp_path):
tests/test_discovery_adapter.py:195:    e = parse_evidence(p)
tests/test_discovery_adapter.py:199:def test_parse_decision_tighten_maps_to_continue(fixtures):
tests/test_discovery_adapter.py:200:    d = parse_decision(fixtures / "decision.md")
tests/test_discovery_adapter.py:227:    d = parse_decision(p)
tests/test_discovery_adapter.py:234:    p = emit_policy_quality_note()
tests/test_discovery_adapter.py:255:        parse_evidence(p)
tests/test_discovery_adapter.py:266:        parse_evidence(p)
tests/test_discovery_adapter.py:277:        parse_decision(p)
tests/test_discovery_adapter.py:288:    e = parse_evidence(p)
src/skillfoundry_harness/discovery_adapter/emit.py:194:def parse_assumption(md_path: Path | str) -> dict[str, Any]:
src/skillfoundry_harness/discovery_adapter/emit.py:233:def parse_probe(md_path: Path | str,
src/skillfoundry_harness/discovery_adapter/emit.py:335:def parse_evidence(md_path: Path | str) -> dict[str, Any]:
src/skillfoundry_harness/discovery_adapter/emit.py:376:def parse_decision(md_path: Path | str) -> dict[str, Any]:
src/skillfoundry_harness/discovery_adapter/emit.py:437:def emit_policy_quality_note(effective_from: str | datetime | None = None) -> dict[str, Any]:

exec
/bin/bash -lc 'rg -n "phase_transition|promotion_id|evidence_quality|preflight-distribution-signal|tighten|pause" src tests' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
tests/test_discovery_adapter.py:52:- `minimum_evidence_quality`: `moderate`
tests/test_discovery_adapter.py:69:- `evidence_quality`: `moderate`
tests/test_discovery_adapter.py:86:- `decision_type`: `tighten`
tests/test_discovery_adapter.py:91:- `rationale`: `one positive signal is enough to tighten`
tests/test_discovery_adapter.py:120:    # Active probe: 2 events (phase_transition draft→probe + methodology_log)
tests/test_discovery_adapter.py:123:    assert events[0]["event_kind"] == "phase_transition"
tests/test_discovery_adapter.py:124:    assert events[0]["phase_transition"]["from_phase"] == "draft"
tests/test_discovery_adapter.py:125:    assert events[0]["phase_transition"]["to_phase"] == "probe"
tests/test_discovery_adapter.py:152:    assert events[-1]["phase_transition"]["from_phase"] == "probe"
tests/test_discovery_adapter.py:153:    assert events[-1]["phase_transition"]["to_phase"] == "promotion"
tests/test_discovery_adapter.py:157:    # Killed probe: Decision records the kill; no L1 phase_transition emitted.
tests/test_discovery_adapter.py:199:def test_parse_decision_tighten_maps_to_continue(fixtures):
tests/test_discovery_adapter.py:203:    assert d["rationale"].startswith("[skillfoundry-type=tighten]")
tests/test_discovery_adapter.py:213:        ("tighten", "continue", "[skillfoundry-type=tighten]"),
tests/test_discovery_adapter.py:215:        ("pause", "continue", "[skillfoundry-type=pause]"),
tests/test_discovery_adapter.py:222:        "- `decision_type`: `tighten`",
tests/test_discovery_adapter.py:271:        "- `decision_type`: `tighten`",
src/skillfoundry_harness/discovery_adapter/__init__.py:16:    parse_probe(md_path)       -> (phase_transition, methodology_log) events
src/skillfoundry_harness/discovery_adapter/emit.py:42:QUALITY_POLICY_ID = "skillfoundry.evidence_quality_note"
src/skillfoundry_harness/discovery_adapter/emit.py:229:# Probe → EventLogEntry (phase_transition + methodology_log)
src/skillfoundry_harness/discovery_adapter/emit.py:238:      1. phase_transition (draft → probe) at probe start
src/skillfoundry_harness/discovery_adapter/emit.py:240:      3. phase_transition (probe → promotion) ONLY when the caller passes
src/skillfoundry_harness/discovery_adapter/emit.py:243:    The L1 schema's phase_transition only models three phases: draft, probe,
src/skillfoundry_harness/discovery_adapter/emit.py:265:    # 1. phase_transition draft → probe
src/skillfoundry_harness/discovery_adapter/emit.py:269:    pt1["event_kind"] = "phase_transition"
src/skillfoundry_harness/discovery_adapter/emit.py:271:    pt1["phase_transition"] = {
src/skillfoundry_harness/discovery_adapter/emit.py:290:    # 3. phase_transition probe → promotion, only when caller confirms promote
src/skillfoundry_harness/discovery_adapter/emit.py:296:        pt2["event_kind"] = "phase_transition"
src/skillfoundry_harness/discovery_adapter/emit.py:298:        pt2["phase_transition"] = {
src/skillfoundry_harness/discovery_adapter/emit.py:368:    "tighten": "continue",  # skillfoundry-specific variant; flagged in rationale
src/skillfoundry_harness/discovery_adapter/emit.py:370:    "pause": "continue",  # non-terminal pause preserves the claim; rationale carries the nuance
src/skillfoundry_harness/discovery_adapter/emit.py:379:    Skillfoundry's `decision_type` enum is richer than canon's (tighten,
src/skillfoundry_harness/discovery_adapter/emit.py:380:    pause); the mapping folds them into the closest canon kind and
src/skillfoundry_harness/discovery_adapter/emit.py:382:    type=tighten]" prefix marker.
src/skillfoundry_harness/discovery_adapter/emit.py:425:        # skillfoundry decisions don't carry an explicit promotion_id;
src/skillfoundry_harness/discovery_adapter/emit.py:427:        envelope["promotion_id"] = f"prom-{header['decision_id']}"
src/skillfoundry_harness/discovery_adapter/emit.py:438:    """Policy capturing the semantics of skillfoundry's evidence_quality
src/skillfoundry_harness/discovery_adapter/emit.py:462:            "`evidence_quality` label that canon does not model directly "
src/skillfoundry_harness/discovery_adapter/MAPPING.md:25:| `status` | (not on Claim) | emitted as EventLogEntry.phase_transition |
src/skillfoundry_harness/discovery_adapter/MAPPING.md:39:1. `phase_transition` (draft → probe) at `started_at`
src/skillfoundry_harness/discovery_adapter/MAPPING.md:42:3. `phase_transition` (probe → promotion) at `ended_at`, only when `status=closed`
src/skillfoundry_harness/discovery_adapter/MAPPING.md:47:| `assumption_id` | `phase_transition.claim_id` + `subject_id` | |
src/skillfoundry_harness/discovery_adapter/MAPPING.md:54:`minimum_evidence_quality`, `success_rule`, `falsification_rule`, `owner`)
src/skillfoundry_harness/discovery_adapter/MAPPING.md:57:**Outlier**: `probes/preflight-distribution-signal.md` uses a prose/bold
src/skillfoundry_harness/discovery_adapter/MAPPING.md:79:Fields preserved in artifact only: `evidence_quality` (weak|moderate|
src/skillfoundry_harness/discovery_adapter/MAPPING.md:92:| `tighten` | `continue` (rationale flagged `[skillfoundry-type=tighten]`) |
src/skillfoundry_harness/discovery_adapter/MAPPING.md:94:| `pause` | `continue` (rationale flagged `[skillfoundry-type=pause]`) |
src/skillfoundry_harness/discovery_adapter/MAPPING.md:108:(`skillfoundry.evidence_quality_note` v1); `exposure` uses the default
src/skillfoundry_harness/discovery_adapter/MAPPING.md:109:envelope; `promotion_id` synthesized as `prom-<decision_id>` when
src/skillfoundry_harness/discovery_adapter/MAPPING.md:115:`evidence_quality` (weak|moderate|strong) is preserved in the artifact

exec
/bin/bash -lc 'nl -ba tests/test_discovery_adapter.py' in /opt/workspace/projects/skillfoundry/skillfoundry-harness
 succeeded in 0ms:
     1	"""Smoke tests for the skillfoundry discovery adapter.
     2	
     3	Each test writes a minimal markdown fixture to a tmp dir, calls the
     4	corresponding parse_* function, and asserts the resulting canon envelope
     5	has the expected core fields. Schema-level validation is exercised by
     6	`python -m skillfoundry_harness.discovery_adapter.migrate --dry-run`;
     7	these tests are lighter-weight shape checks.
     8	"""
     9	
    10	from __future__ import annotations
    11	
    12	from pathlib import Path
    13	
    14	import pytest
    15	
    16	from skillfoundry_harness.discovery_adapter import (
    17	    AdapterParseError,
    18	    emit_policy_quality_note,
    19	    parse_assumption,
    20	    parse_decision,
    21	    parse_evidence,
    22	    parse_probe,
    23	)
    24	
    25	
    26	ASSUMPTION_MD = """\
    27	# CriticalAssumption: demo
    28	
    29	- `assumption_id`: `demo`
    30	- `title`: `demo title`
    31	- `status`: `active`
    32	- `owner`: `skillfoundry`
    33	- `buyer_role`: `demo buyer`
    34	- `problem_claim`: `Demo buyers need a thing`
    35	- `economic_claim`: `They will pay`
    36	- `channel_claim`: `Direct email works`
    37	- `falsification_rule`: `If nobody engages, claim is wrong`
    38	- `next_probe_id`: `demo-probe`
    39	- `created_at`: `2026-04-10T00:00:00Z`
    40	- `updated_at`: `2026-04-10T00:00:00Z`
    41	"""
    42	
    43	
    44	PROBE_MD = """\
    45	# Probe: demo-probe
    46	
    47	- `probe_id`: `demo-probe`
    48	- `assumption_id`: `demo`
    49	- `probe_type`: `manual_offer`
    50	- `artifact_class`: `service_probe`
    51	- `target_evidence_class`: `external_conversation`
    52	- `minimum_evidence_quality`: `moderate`
    53	- `success_rule`: `any builder engages`
    54	- `falsification_rule`: `no builder engages after 14d`
    55	- `started_at`: `2026-04-10T00:00:00Z`
    56	- `ended_at`: `(open)`
    57	- `status`: `active`
    58	- `owner`: `skillfoundry`
    59	"""
    60	
    61	
    62	EVIDENCE_MD = """\
    63	# Evidence: 2026-04-12 first external reply
    64	
    65	- `evidence_id`: `2026-04-12-first-external-reply`
    66	- `assumption_id`: `demo`
    67	- `probe_id`: `demo-probe`
    68	- `evidence_class`: `external_conversation`
    69	- `evidence_quality`: `moderate`
    70	- `source_type`: `email_reply`
    71	- `source_identity`: `anon-builder-1`
    72	- `observed_at`: `2026-04-12T10:00:00Z`
    73	- `summary`: `Builder expressed interest`
    74	- `raw_pointer`: `memory/venture/evidence/raw/…`
    75	- `supports`: `supports_assumption`
    76	- `confidence`: `moderate`
    77	"""
    78	
    79	
    80	DECISION_MD = """\
    81	# Decision: 2026-04-13 continue demo
    82	
    83	- `decision_id`: `2026-04-13-continue-demo`
    84	- `assumption_id`: `demo`
    85	- `probe_id`: `demo-probe`
    86	- `decision_type`: `tighten`
    87	- `timestamp`: `2026-04-13T00:00:00Z`
    88	- `owner`: `skillfoundry`
    89	- `evidence_refs`:
    90	  - `2026-04-12-first-external-reply`
    91	- `rationale`: `one positive signal is enough to tighten`
    92	"""
    93	
    94	
    95	@pytest.fixture
    96	def fixtures(tmp_path: Path):
    97	    (tmp_path / "assumption.md").write_text(ASSUMPTION_MD)
    98	    (tmp_path / "probe.md").write_text(PROBE_MD)
    99	    (tmp_path / "evidence.md").write_text(EVIDENCE_MD)
   100	    (tmp_path / "decision.md").write_text(DECISION_MD)
   101	    return tmp_path
   102	
   103	
   104	def test_parse_assumption(fixtures):
   105	    c = parse_assumption(fixtures / "assumption.md")
   106	    assert c["object_type"] == "Claim"
   107	    assert c["id"] == "demo"
   108	    assert c["statement"] == "Demo buyers need a thing"
   109	    assert c["falsification_criteria"] == [
   110	        "If nobody engages, claim is wrong"
   111	    ]
   112	    assert c["emitter"] == "L3:skillfoundry"
   113	    assert c["binding"] == "binding"
   114	    assert c["exposure"]["capital_at_risk"] == 0
   115	    assert c["instance_id"] == "skillfoundry-valuation-context"
   116	    assert c["artifact"]["content_hash"].startswith("sha256:")
   117	
   118	
   119	def test_parse_probe_emits_three_events_when_closed(fixtures):
   120	    # Active probe: 2 events (phase_transition draft→probe + methodology_log)
   121	    events = parse_probe(fixtures / "probe.md")
   122	    assert len(events) == 2
   123	    assert events[0]["event_kind"] == "phase_transition"
   124	    assert events[0]["phase_transition"]["from_phase"] == "draft"
   125	    assert events[0]["phase_transition"]["to_phase"] == "probe"
   126	    assert events[1]["event_kind"] == "methodology_log"
   127	    assert events[1]["methodology_log"]["artifact"]["content_hash"].startswith("sha256:")
   128	
   129	
   130	def test_parse_probe_closed_no_decision_kind_emits_two_events(fixtures, tmp_path):
   131	    # Without a decision_kind, a closed probe emits no closure event.
   132	    # The Decision envelope records the outcome; L1 has no "killed" phase.
   133	    closed = PROBE_MD.replace(
   134	        "- `ended_at`: `(open)`\n- `status`: `active`",
   135	        "- `ended_at`: `2026-04-20T00:00:00Z`\n- `status`: `closed`",
   136	    )
   137	    p = tmp_path / "probe_closed.md"
   138	    p.write_text(closed)
   139	    events = parse_probe(p)
   140	    assert len(events) == 2
   141	
   142	
   143	def test_parse_probe_closed_with_promote_emits_three_events(fixtures, tmp_path):
   144	    closed = PROBE_MD.replace(
   145	        "- `ended_at`: `(open)`\n- `status`: `active`",
   146	        "- `ended_at`: `2026-04-20T00:00:00Z`\n- `status`: `closed`",
   147	    )
   148	    p = tmp_path / "probe_closed_promote.md"
   149	    p.write_text(closed)
   150	    events = parse_probe(p, decision_kind="promote")
   151	    assert len(events) == 3
   152	    assert events[-1]["phase_transition"]["from_phase"] == "probe"
   153	    assert events[-1]["phase_transition"]["to_phase"] == "promotion"
   154	
   155	
   156	def test_parse_probe_closed_with_kill_emits_two_events(fixtures, tmp_path):
   157	    # Killed probe: Decision records the kill; no L1 phase_transition emitted.
   158	    closed = PROBE_MD.replace(
   159	        "- `ended_at`: `(open)`\n- `status`: `active`",
   160	        "- `ended_at`: `2026-04-20T00:00:00Z`\n- `status`: `closed`",
   161	    )
   162	    p = tmp_path / "probe_closed_kill.md"
   163	    p.write_text(closed)
   164	    events = parse_probe(p, decision_kind="kill")
   165	    assert len(events) == 2
   166	
   167	
   168	def test_parse_probe_closed_with_pivot_emits_two_events(fixtures, tmp_path):
   169	    closed = PROBE_MD.replace(
   170	        "- `ended_at`: `(open)`\n- `status`: `active`",
   171	        "- `ended_at`: `2026-04-20T00:00:00Z`\n- `status`: `closed`",
   172	    )
   173	    p = tmp_path / "probe_closed_pivot.md"
   174	    p.write_text(closed)
   175	    events = parse_probe(p, decision_kind="pivot")
   176	    assert len(events) == 2
   177	
   178	
   179	def test_parse_evidence_polarity_and_tier(fixtures):
   180	    e = parse_evidence(fixtures / "evidence.md")
   181	    assert e["object_type"] == "Evidence"
   182	    assert e["tier"] == "external_conversation"
   183	    assert e["polarity"] == "supports"
   184	    assert e["claim_id"] == "demo"
   185	    assert e["evidence_type"] == "email_reply"
   186	
   187	
   188	def test_parse_evidence_lane_activation_neutral(fixtures, tmp_path):
   189	    alt = EVIDENCE_MD.replace(
   190	        "- `supports`: `supports_assumption`",
   191	        "- `supports`: `lane_activation_only`",
   192	    )
   193	    p = tmp_path / "evidence_activation.md"
   194	    p.write_text(alt)
   195	    e = parse_evidence(p)
   196	    assert e["polarity"] == "neutral"
   197	
   198	
   199	def test_parse_decision_tighten_maps_to_continue(fixtures):
   200	    d = parse_decision(fixtures / "decision.md")
   201	    assert d["object_type"] == "Decision"
   202	    assert d["kind"] == "continue"
   203	    assert d["rationale"].startswith("[skillfoundry-type=tighten]")
   204	    assert d["candidate_claims"] == ["demo"]
   205	    assert d["chosen_claim_id"] == "demo"
   206	    assert d["cited_evidence"] == ["2026-04-12-first-external-reply"]
   207	
   208	
   209	@pytest.mark.parametrize(
   210	    "decision_type,expected_kind,expected_marker",
   211	    [
   212	        ("continue", "continue", None),
   213	        ("tighten", "continue", "[skillfoundry-type=tighten]"),
   214	        ("pivot", "pivot", None),
   215	        ("pause", "continue", "[skillfoundry-type=pause]"),
   216	        ("kill", "kill", None),
   217	    ],
   218	)
   219	def test_decision_kind_mapping(tmp_path, decision_type, expected_kind,
   220	                               expected_marker):
   221	    md = DECISION_MD.replace(
   222	        "- `decision_type`: `tighten`",
   223	        f"- `decision_type`: `{decision_type}`",
   224	    )
   225	    p = tmp_path / "d.md"
   226	    p.write_text(md)
   227	    d = parse_decision(p)
   228	    assert d["kind"] == expected_kind
   229	    if expected_marker:
   230	        assert d["rationale"].startswith(expected_marker)
   231	
   232	
   233	def test_policy_shape():
   234	    p = emit_policy_quality_note()
   235	    assert p["object_type"] == "Policy"
   236	    assert p["class"] == "operational"
   237	    assert p["scope"] == "L3:skillfoundry-valuation-context"
   238	    assert "instance_id" not in p  # Policy schema forbids
   239	    assert p["value"]["values"] == ["weak", "moderate", "strong"]
   240	
   241	
   242	# --------------------------------------------------------------------------
   243	# Finding 2 — unknown enum values must raise AdapterParseError, not coerce
   244	# --------------------------------------------------------------------------
   245	
   246	
   247	def test_evidence_unknown_tier_raises(tmp_path):
   248	    bad = EVIDENCE_MD.replace(
   249	        "- `evidence_class`: `external_conversation`",
   250	        "- `evidence_class`: `commercial_signal`",
   251	    )
   252	    p = tmp_path / "evidence_bad_tier.md"
   253	    p.write_text(bad)
   254	    with pytest.raises(AdapterParseError, match="evidence_class"):
   255	        parse_evidence(p)
   256	
   257	
   258	def test_evidence_unknown_polarity_raises(tmp_path):
   259	    bad = EVIDENCE_MD.replace(
   260	        "- `supports`: `supports_assumption`",
   261	        "- `supports`: `strongly_supports`",
   262	    )
   263	    p = tmp_path / "evidence_bad_polarity.md"
   264	    p.write_text(bad)
   265	    with pytest.raises(AdapterParseError, match="supports"):
   266	        parse_evidence(p)
   267	
   268	
   269	def test_decision_unknown_type_raises(tmp_path):
   270	    bad = DECISION_MD.replace(
   271	        "- `decision_type`: `tighten`",
   272	        "- `decision_type`: `approved`",
   273	    )
   274	    p = tmp_path / "decision_bad_type.md"
   275	    p.write_text(bad)
   276	    with pytest.raises(AdapterParseError, match="decision_type"):
   277	        parse_decision(p)
   278	
   279	
   280	def test_known_lane_activation_polarity_still_maps(tmp_path):
   281	    # lane_activation_only is a known alias in _POLARITY_MAP; must not raise.
   282	    md = EVIDENCE_MD.replace(
   283	        "- `supports`: `supports_assumption`",
   284	        "- `supports`: `lane_activation_only`",
   285	    )
   286	    p = tmp_path / "evidence_lane.md"
   287	    p.write_text(md)
   288	    e = parse_evidence(p)
   289	    assert e["polarity"] == "neutral"

codex
1. **Most dangerous assumption**

`parse_assumption()` assumes one Skillfoundry assumption can be safely collapsed into one canon `Claim` by using only `problem_claim`, with `economic_claim` and `channel_claim` relegated to artifact-only recovery (`emit.py:197-202`, `emit.py:218-224`, `MAPPING.md:12-17`, `MAPPING.md:136-140`). If that is wrong, the entire downstream graph is anchored to an incomplete claim object: decisions, evidence, and promotions will look canonically valid while silently discarding two-thirds of the business thesis unless every consumer reparses markdown.

2. **Missing failure mode**

The design does not really handle routine authoring drift in markdown headers. The parser is format-fragile by construction (`emit.py:51-53`, `emit.py:103-108`), and the mapping doc already admits a real outlier probe file that does not parse (`MAPPING.md:57-62`). Worse, the migration pre-pass swallows decision-header parse failures and just omits the probe→promotion event (`migrate.py:120-127`, `migrate.py:164-168`), so a common formatting error yields partial `.canon` output with a missing lifecycle edge instead of a hard repository-contract failure.

3. **Boundary most likely to be collapsed in practice**

The nominal boundary between “parse one file” APIs and repository-level semantics is already leaking at probes. `parse_probe()` only emits the correct closure event if the caller injects `decision_kind` from a separate decision file (`__init__.py:15-19`, `emit.py:240-246`, `emit.py:290-303`). `migrate.py` compensates by doing a cross-directory join up front (`migrate.py:113-127`, `migrate.py:164-168`). In practice, callers will either get incomplete event histories or reimplement repo-aware joining logic, so this API boundary will collapse into a repository adapter anyway.

Overall verdict: the adapter is readable, but its stability is overstated. The current contract hides a lossy semantic collapse and a cross-file dependency that should be explicit invariants, not caller folklore.
tokens used
30,692
1. **Most dangerous assumption**

`parse_assumption()` assumes one Skillfoundry assumption can be safely collapsed into one canon `Claim` by using only `problem_claim`, with `economic_claim` and `channel_claim` relegated to artifact-only recovery (`emit.py:197-202`, `emit.py:218-224`, `MAPPING.md:12-17`, `MAPPING.md:136-140`). If that is wrong, the entire downstream graph is anchored to an incomplete claim object: decisions, evidence, and promotions will look canonically valid while silently discarding two-thirds of the business thesis unless every consumer reparses markdown.

2. **Missing failure mode**

The design does not really handle routine authoring drift in markdown headers. The parser is format-fragile by construction (`emit.py:51-53`, `emit.py:103-108`), and the mapping doc already admits a real outlier probe file that does not parse (`MAPPING.md:57-62`). Worse, the migration pre-pass swallows decision-header parse failures and just omits the probe→promotion event (`migrate.py:120-127`, `migrate.py:164-168`), so a common formatting error yields partial `.canon` output with a missing lifecycle edge instead of a hard repository-contract failure.

3. **Boundary most likely to be collapsed in practice**

The nominal boundary between “parse one file” APIs and repository-level semantics is already leaking at probes. `parse_probe()` only emits the correct closure event if the caller injects `decision_kind` from a separate decision file (`__init__.py:15-19`, `emit.py:240-246`, `emit.py:290-303`). `migrate.py` compensates by doing a cross-directory join up front (`migrate.py:113-127`, `migrate.py:164-168`). In practice, callers will either get incomplete event histories or reimplement repo-aware joining logic, so this API boundary will collapse into a repository adapter anyway.

Overall verdict: the adapter is readable, but its stability is overstated. The current contract hides a lossy semantic collapse and a cross-file dependency that should be explicit invariants, not caller folklore.
