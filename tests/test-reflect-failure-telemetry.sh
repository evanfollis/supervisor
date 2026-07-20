#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

WORKSPACE_ROOT="$ROOT/workspace"
PROJECT_DIR="$WORKSPACE_ROOT/projects/demo"
BIN_DIR="$ROOT/bin"

mkdir -p "$PROJECT_DIR" "$BIN_DIR" "$WORKSPACE_ROOT/runtime/.telemetry"
git -C "$PROJECT_DIR" init -b main >/dev/null
git -C "$PROJECT_DIR" config user.email test@example.com
git -C "$PROJECT_DIR" config user.name Test
printf 'public = true\n' > "$PROJECT_DIR/security.conf"
git -C "$PROJECT_DIR" add security.conf
git -C "$PROJECT_DIR" commit -m fixture >/dev/null
printf '{"project":"demo","source":"test","eventType":"info","level":"info","sourceType":"system","timestamp":1}\n' \
  > "$WORKSPACE_ROOT/runtime/.telemetry/events.jsonl"
EVENT_FILE="$WORKSPACE_ROOT/runtime/.telemetry/events.jsonl"

set +e
WORKSPACE_LAYOUT=split \
WORKSPACE_ROOT="$WORKSPACE_ROOT" \
WORKSPACE_META_DIR="$WORKSPACE_ROOT/runtime/.meta" \
WORKSPACE_HANDOFF_DIR="$WORKSPACE_ROOT/runtime/.handoff" \
WORKSPACE_TELEMETRY_DIR="$WORKSPACE_ROOT/runtime/.telemetry" \
PATH="$BIN_DIR:$PATH" \
  /opt/workspace/supervisor/scripts/lib/reflect.sh demo "$PROJECT_DIR" missing-reflect-prompt.md \
  > "$ROOT/stdout-missing-prompt" 2> "$ROOT/stderr-missing-prompt"
status=$?
set -e

if [[ "$status" -ne 1 ]]; then
  echo "expected reflect.sh to exit 1 for missing prompt, got $status" >&2
  cat "$ROOT/stdout-missing-prompt" >&2
  cat "$ROOT/stderr-missing-prompt" >&2
  exit 1
fi

grep -q '"reason":"prompt_template_not_found"' "$EVENT_FILE"
grep -q '"exitCode":1' "$EVENT_FILE"

set +e
WORKSPACE_LAYOUT=split \
WORKSPACE_ROOT="$WORKSPACE_ROOT" \
WORKSPACE_META_DIR="$WORKSPACE_ROOT/runtime/.meta" \
WORKSPACE_HANDOFF_DIR="$WORKSPACE_ROOT/runtime/.handoff" \
WORKSPACE_TELEMETRY_DIR="$WORKSPACE_ROOT/runtime/.telemetry" \
PATH="$BIN_DIR:$PATH" \
  /opt/workspace/supervisor/scripts/lib/reflect.sh missing "$WORKSPACE_ROOT/projects/missing" \
  > "$ROOT/stdout-missing-project" 2> "$ROOT/stderr-missing-project"
status=$?
set -e

if [[ "$status" -ne 1 ]]; then
  echo "expected reflect.sh to exit 1 for missing project dir, got $status" >&2
  cat "$ROOT/stdout-missing-project" >&2
  cat "$ROOT/stderr-missing-project" >&2
  exit 1
fi

grep -q '"source":"missing.reflect"' "$EVENT_FILE"
grep -q '"reason":"project_dir_not_found"' "$EVENT_FILE"

cat > "$BIN_DIR/claude" <<'EOF'
#!/usr/bin/env bash
echo "fake claude: invocation failed"
exit 7
EOF
chmod +x "$BIN_DIR/claude"
cat > "$BIN_DIR/codex" <<'EOF'
#!/usr/bin/env bash
echo "codex must not run after a non-capacity Claude failure" >&2
exit 9
EOF
chmod +x "$BIN_DIR/codex"

set +e
WORKSPACE_LAYOUT=split \
WORKSPACE_ROOT="$WORKSPACE_ROOT" \
WORKSPACE_META_DIR="$WORKSPACE_ROOT/runtime/.meta" \
WORKSPACE_HANDOFF_DIR="$WORKSPACE_ROOT/runtime/.handoff" \
WORKSPACE_TELEMETRY_DIR="$WORKSPACE_ROOT/runtime/.telemetry" \
PATH="$BIN_DIR:$PATH" \
  /opt/workspace/supervisor/scripts/lib/reflect.sh demo "$PROJECT_DIR" \
  > "$ROOT/stdout-failed" 2> "$ROOT/stderr-failed"
status=$?
set -e

if [[ "$status" -ne 1 ]]; then
  echo "expected reflection invocation to fail closed with exit 1, got $status" >&2
  cat "$ROOT/stdout-failed" >&2
  cat "$ROOT/stderr-failed" >&2
  exit 1
fi

grep -q '"reason":"model_invocation_failed"' "$EVENT_FILE"
grep -q '"exitCode":1' "$EVENT_FILE"

# A subscription-capacity failure must fall through to the sibling provider,
# produce a read-only reflection, and retain the complete private transcript.
cat > "$BIN_DIR/claude" <<'EOF'
#!/usr/bin/env bash
echo "usage limit reached" >&2
exit 75
EOF
cat > "$BIN_DIR/codex" <<'EOF'
#!/usr/bin/env bash
PROMPT="$(cat)"
python3 - "$PROMPT" <<'PY'
import json, re, sys
prompt = sys.argv[1]
snapshot_match = re.search(r"1\. `([^`]+)`", prompt)
assert snapshot_match, "snapshot path missing from reflection prompt"
snapshot = json.load(open(snapshot_match.group(1), encoding="utf-8"))
primary = next(item for item in snapshot["objects"] if item.get("source") == "project")
stale_witness = primary["witness"].rsplit("=", 1)[0] + "=" + "0" * 64
reflection = f"""### Summary

The fixture emitted one telemetry event and no code changes were observed.

### Principle adherence

Primary evidence was inspected; other principles were not measurable in this window.

### Observations

- [CRITICAL-SECURITY] The fixture marks a public service boundary.
  - Primary evidence: `{stale_witness}`
  - Remaining uncertainty: The object identity does not validate severity.

### Proposals

No proposals in this window.

### Questions for the human

None.
"""
print(json.dumps({"type":"thread.started","thread_id":"codex-test"}))
print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":reflection}}))
print(json.dumps({"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":20}}))
PY
EOF
chmod +x "$BIN_DIR/claude" "$BIN_DIR/codex"

WORKSPACE_LAYOUT=split \
WORKSPACE_ROOT="$WORKSPACE_ROOT" \
WORKSPACE_META_DIR="$WORKSPACE_ROOT/runtime/.meta" \
WORKSPACE_HANDOFF_DIR="$WORKSPACE_ROOT/runtime/.handoff" \
WORKSPACE_TELEMETRY_DIR="$WORKSPACE_ROOT/runtime/.telemetry" \
PROMPTEVAL_RUNTIME="$WORKSPACE_ROOT/runtime/prompteval" \
PATH="$BIN_DIR:$PATH" \
  /opt/workspace/supervisor/scripts/lib/reflect.sh demo "$PROJECT_DIR" \
  > "$ROOT/stdout-fallback" 2> "$ROOT/stderr-fallback"

REFLECTION="$(find "$WORKSPACE_ROOT/runtime/.meta" -maxdepth 1 -name 'demo-reflection-*.md' | head -1)"
test -n "$REFLECTION"
grep -q '^# Typed reflection evidence projection$' "$REFLECTION"
if grep -q 'SECURITY]' "$REFLECTION"; then
  echo "synthesis projection leaked a quarantined security claim" >&2
  exit 1
fi
if grep -q '^### Proposals$' "$REFLECTION"; then
  echo "synthesis projection leaked the raw Proposals section" >&2
  exit 1
fi
RAW_REFLECTION="$(find "$WORKSPACE_ROOT/runtime/.meta/reflections/raw" -maxdepth 1 -name 'demo-reflection-*.md' | head -1)"
test -n "$RAW_REFLECTION"
grep -q 'UNVERIFIED-SECURITY' "$RAW_REFLECTION"
EVIDENCE="${RAW_REFLECTION%.md}.evidence.json"
python3 - "$EVIDENCE" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
assert value["proposal_count"] == 0
assert value["critical_security_object_matched_count"] == 0
assert value["unverified_security_count"] == 1
PY
grep -q '"eventType":"reflection.security_review_requested"' "$EVENT_FILE"
grep -q '"level":"warn"' "$EVENT_FILE"
grep -q '"unverifiedCount":1' "$EVENT_FILE"
grep -q '"severityJudgmentValidated":false' "$EVENT_FILE"
MANIFEST="$(find "$WORKSPACE_ROOT/runtime/.meta/reflection-invocations/demo" -name manifest.json | head -1)"
python3 - "$MANIFEST" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
assert value["provider"] == "openai"
assert value["provider_session_id"] == "codex-test"
assert value["transcript"]["status"] == "archived"
assert value["transcript"]["hot_path_cleared"] is True
assert value["reflection"]["path"].endswith(".md")
assert value["primary_object_attestation"]["primary_object_matched_count"] == 0
assert value["primary_object_attestation"]["critical_security_object_matched_count"] == 0
assert value["primary_object_attestation"]["unverified_security_count"] == 1
assert value["synthesis_projection"]["path"].endswith(".md")
assert value["synthesis_projection"]["proposal_content_included"] is False
assert value["synthesis_projection"]["raw_narrative_content_included"] is False
PY

echo "reflect failure telemetry test passed"
