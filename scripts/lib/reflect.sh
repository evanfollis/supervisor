#!/usr/bin/env bash
# Per-project 12h reflection driver.
# Builds a deterministic primary-object snapshot, invokes a subscription model
# with read-only tools, and captures the returned advisory reflection. Full
# invocation transcripts are retained privately off the hot path. The model
# cannot write project state; synthesis owns any later promotion.
#
# Usage: reflect.sh <project-name> <project-dir>
#   reflect.sh command /opt/workspace/projects/command
#
# Short-circuits if there's been no activity in the last 12h.

set -euo pipefail
umask 077

PROJECT="${1:?project name required}"
PROJECT_DIR="${2:?project dir required}"
PROMPT_TEMPLATE_OVERRIDE="${3:-}"
LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
META_DIR="$WORKSPACE_META_DIR"
ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
INVOCATION_ID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
INVOCATION_SHORT="${INVOCATION_ID%%-*}"
OUTPUT_FILE="$META_DIR/${PROJECT}-reflection-${ISO_NOW}-${INVOCATION_SHORT}.md"
RAW_REFLECTION_DIR="$META_DIR/reflections/raw"
RAW_REFLECTION_FILE="$RAW_REFLECTION_DIR/${PROJECT}-reflection-${ISO_NOW}-${INVOCATION_SHORT}.md"
EVIDENCE_FILE="${RAW_REFLECTION_FILE%.md}.evidence.json"
INVOCATION_DIR="$META_DIR/reflection-invocations/$PROJECT/${ISO_NOW}-${INVOCATION_ID}"
PROMPT_FILE="$INVOCATION_DIR/prompt.md"
RESULT_JSON="$INVOCATION_DIR/result.json"
STDERR_LOG="$INVOCATION_DIR/stderr.log"
SNAPSHOT_FILE="$INVOCATION_DIR/primary-object-snapshot.json"
INVOCATION_MANIFEST="$INVOCATION_DIR/manifest.json"
TRANSCRIPT_ARCHIVE="$INVOCATION_DIR/transcript.jsonl.gz"
CANDIDATE_FILE="$INVOCATION_DIR/reflection.candidate.md"
CANDIDATE_EVIDENCE_FILE="$INVOCATION_DIR/reflection.candidate.evidence.json"
SYNTHESIS_PROJECTION_CANDIDATE="$INVOCATION_DIR/synthesis-projection.candidate.md"
STABILITY_REPORT="$INVOCATION_DIR/project-stability.json"
PROMPTEVAL_RUNTIME="${PROMPTEVAL_RUNTIME:-$WORKSPACE_ROOT/runtime/prompteval}"
TRANSCRIPT_SOURCE="$PROMPTEVAL_RUNTIME/.transcripts/$INVOCATION_ID.jsonl"
export PROMPTEVAL_RUNTIME

emit_reflection_failure_telemetry() {
  local reason="$1"
  local exit_code="$2"

  mkdir -p "$WORKSPACE_TELEMETRY_DIR" 2>/dev/null || return 0
  printf '{"project":"%s","source":"%s.reflect","eventType":"failure","level":"error","sourceType":"system","timestamp":%s,"note":"reflection failed: %s","ref":"%s","details":{"reason":"%s","exitCode":%d,"outputFile":"%s"}}\n' \
    "$PROJECT" "$PROJECT" "$(date -u +%s%3N)" "$reason" "$OUTPUT_FILE" "$reason" "$exit_code" "$OUTPUT_FILE" \
    >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null || true
}

if [[ -n "$PROMPT_TEMPLATE_OVERRIDE" ]]; then
  # Allow either absolute path or a basename resolved under LIB_DIR.
  if [[ "$PROMPT_TEMPLATE_OVERRIDE" == /* ]]; then
    PROMPT_TEMPLATE="$PROMPT_TEMPLATE_OVERRIDE"
  else
    PROMPT_TEMPLATE="$LIB_DIR/$PROMPT_TEMPLATE_OVERRIDE"
  fi
else
  PROMPT_TEMPLATE="$LIB_DIR/reflect-prompt.md"
fi
if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "reflect: prompt template not found: $PROMPT_TEMPLATE" >&2
  emit_reflection_failure_telemetry "prompt_template_not_found" 1
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "reflect: project dir not found: $PROJECT_DIR" >&2
  emit_reflection_failure_telemetry "project_dir_not_found" 1
  exit 1
fi

mkdir -p "$META_DIR"
mkdir -p "$INVOCATION_DIR"
chmod 700 "$INVOCATION_DIR"
mkdir -p "$RAW_REFLECTION_DIR"
chmod 700 "$RAW_REFLECTION_DIR"
WORKSPACE_SESSION_MEMORY_DIR="/root/.claude/projects/-$(echo "$WORKSPACE_ROOT" | sed 's|^/||; s|/|-|g')/memory"

# Claude Code's per-cwd JSONL directory. Encoding: slashes → hyphens, prefix "-".
# e.g. /opt/workspace/projects/atlas → -opt-workspace-projects-atlas
SESSION_DIR="/root/.claude/projects/-$(echo "$PROJECT_DIR" | sed 's|^/||; s|/|-|g')"

# Pre-flight activity check — avoid spawning Claude if nothing happened.
COMMIT_COUNT=0
if [[ -d "$PROJECT_DIR/.git" ]]; then
  COMMIT_COUNT=$(git -C "$PROJECT_DIR" log --since="12 hours ago" --oneline 2>/dev/null | wc -l || echo 0)
fi

TELEMETRY_COUNT=0
if [[ -f "$WORKSPACE_TELEMETRY_DIR/events.jsonl" ]]; then
  # Rough filter: events whose JSON mentions the project name in the last ~12h slice of the file.
  # (Per-project telemetry filtering is best-effort; the Claude session does the authoritative read.)
  TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null | grep -c -F "\"$PROJECT\"" || true)
fi

# Session JSONL activity: count transcript files modified in the last 12h.
JSONL_RECENT=0
if [[ -d "$SESSION_DIR" ]]; then
  JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' -newermt "12 hours ago" 2>/dev/null | wc -l)
fi

if [[ "$COMMIT_COUNT" -eq 0 && "$TELEMETRY_COUNT" -eq 0 && "$JSONL_RECENT" -eq 0 ]]; then
  printf '# Reflection skipped — no activity in window ending %s\n' "$ISO_NOW" > "$OUTPUT_FILE"
  echo "reflect[$PROJECT]: short-circuit (no commits, no telemetry, no session activity)"
  exit 0
fi

# Freeze the model's observable git state and exact primary-object identities
# before interpretation. The model receives Read/Glob/Grep only; it does not
# need a shell to inspect history or calculate witness hashes.
python3 "$LIB_DIR/reflection-snapshot.py" \
  --project "$PROJECT" \
  --project-dir "$PROJECT_DIR" \
  --output "$SNAPSHOT_FILE" \
  --explicit-file "$WORKSPACE_TELEMETRY_DIR/events.jsonl" \
  --explicit-file "$PROJECT_DIR/CONTEXT.md" \
  --explicit-file "$PROJECT_DIR/CURRENT_STATE.md" \
  --explicit-file "$PROJECT_DIR/CLAUDE.md" \
  --explicit-file "$WORKSPACE_ROOT_CLAUDE_MD" \
  --explicit-file "$WORKSPACE_SESSION_MEMORY_DIR/MEMORY.md" \
  --session-dir "$SESSION_DIR" \
  --prior-reflection-dir "$WORKSPACE_META_DIR" \
  --hours 12

# Render the prompt with substitutions.
PROMPT="$(sed \
  -e "s|{{PROJECT}}|$PROJECT|g" \
  -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
  -e "s|{{OUTPUT_FILE}}|$OUTPUT_FILE|g" \
  -e "s|{{ISO_NOW}}|$ISO_NOW|g" \
  -e "s|{{SESSION_DIR}}|$SESSION_DIR|g" \
  -e "s|{{WORKSPACE_TELEMETRY_FILE}}|$WORKSPACE_TELEMETRY_DIR/events.jsonl|g" \
  -e "s|{{WORKSPACE_META_DIR}}|$WORKSPACE_META_DIR|g" \
  -e "s|{{WORKSPACE_ROOT_CLAUDE_MD}}|$WORKSPACE_ROOT_CLAUDE_MD|g" \
  -e "s|{{WORKSPACE_HANDOFF_DIR}}|$WORKSPACE_HANDOFF_DIR|g" \
  -e "s|{{WORKSPACE_SESSION_MEMORY_DIR}}|$WORKSPACE_SESSION_MEMORY_DIR|g" \
  -e "s|{{REFLECTION_SNAPSHOT}}|$SNAPSHOT_FILE|g" \
  "$PROMPT_TEMPLATE")"
printf '%s\n' "$PROMPT" > "$PROMPT_FILE"

cd "$PROJECT_DIR"

# Package manager cache paths: headless sessions run under a systemd unit where
# ~/.npm and ~/.cache may be on a read-only mount. Redirect to writable runtime
# paths so npm/pip never fail with EROFS.
export NPM_CONFIG_CACHE="${NPM_CONFIG_CACHE:-/opt/workspace/runtime/.npm-cache}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-/opt/workspace/runtime/.pip-cache}"
mkdir -p "$NPM_CONFIG_CACHE" "$PIP_CACHE_DIR"

# The invocation helper uses subscription CLIs only. Capacity failures fall
# through from Claude to Codex; semantic failures remain fail-closed. Its full
# raw input/output/stderr transcript is written by the shared telemetry path.
set +e
python3 "$LIB_DIR/reflection-invoke.py" \
  --prompt-file "$PROMPT_FILE" \
  --project "$PROJECT" \
  --project-dir "$PROJECT_DIR" \
  --model claude-sonnet-4-6 \
  --effort medium \
  --invocation-id "$INVOCATION_ID" \
  > "$RESULT_JSON" 2> "$STDERR_LOG"
MODEL_STATUS=$?
set -e

if [[ "$MODEL_STATUS" -ne 0 ]]; then
  echo "reflect[$PROJECT]: ERROR — subscription model invocation failed with exit code $MODEL_STATUS" >&2
  emit_reflection_failure_telemetry "model_invocation_failed" "$MODEL_STATUS"
  exit "$MODEL_STATUS"
fi

if ! python3 "$LIB_DIR/reflection-capture.py" \
    --result "$RESULT_JSON" \
    --reflection "$CANDIDATE_FILE" \
    --transcript-source "$TRANSCRIPT_SOURCE" \
    --transcript-archive "$TRANSCRIPT_ARCHIVE" \
    --manifest "$INVOCATION_MANIFEST" \
    --stderr "$STDERR_LOG" \
    --session-id "$INVOCATION_ID" \
    --provider unknown \
    --model unknown \
    --effort medium; then
  echo "reflect[$PROJECT]: ERROR — model result could not be finalized" >&2
  emit_reflection_failure_telemetry "result_capture_failed" 2
  exit 2
fi

# A reflection is a snapshot interpretation. If the project moved while the
# model was reading, preserve the raw invocation but withhold publication; the
# result no longer describes one coherent primary-object state.
if ! python3 "$LIB_DIR/reflection-stability.py" \
    --snapshot "$SNAPSHOT_FILE" \
    --project-dir "$PROJECT_DIR" \
    --output "$STABILITY_REPORT"; then
  echo "reflect[$PROJECT]: project changed during reflection; publication withheld" >&2
  emit_reflection_failure_telemetry "project_changed_during_reflection" 6
  exit 6
fi

# Attest exact object identity before publication. An unsupported proposal
# remains a valid reflection result, but it is labeled UNVERIFIED and therefore
# cannot silently masquerade as evidence-bearing downstream input. Failed
# attestation leaves only a private candidate under the invocation directory;
# it never enters the reflection glob consumed by synthesis.
if ! python3 "$LIB_DIR/reflection-evidence.py" \
    "$CANDIDATE_FILE" \
    --sidecar "$CANDIDATE_EVIDENCE_FILE"; then
  echo "reflect[$PROJECT]: ERROR — primary-object attestation failed" >&2
  emit_reflection_failure_telemetry "evidence_attestation_failed" 4
  exit 4
fi

# Publish the sidecar first and the reflection last. Therefore any interrupted
# publication leaves at worst an orphan sidecar, never an unattested official
# reflection. Both source files are on the same runtime filesystem, so each
# rename is atomic.
if ! mv -- "$CANDIDATE_EVIDENCE_FILE" "$EVIDENCE_FILE"; then
  emit_reflection_failure_telemetry "evidence_publication_failed" 5
  exit 5
fi
if ! mv -- "$CANDIDATE_FILE" "$RAW_REFLECTION_FILE"; then
  emit_reflection_failure_telemetry "raw_reflection_publication_failed" 5
  exit 5
fi

# Only now may the invocation manifest claim final artifact paths. A failed
# rename therefore cannot leave a false publication record.
if ! python3 "$LIB_DIR/reflection-evidence.py" \
    "$RAW_REFLECTION_FILE" \
    --sidecar "$EVIDENCE_FILE" \
    --artifact-path "$RAW_REFLECTION_FILE" \
    --artifact-sidecar-path "$EVIDENCE_FILE" \
    --finalize-manifest "$INVOCATION_MANIFEST"; then
  emit_reflection_failure_telemetry "evidence_manifest_finalization_failed" 5
  exit 5
fi

# Every typed security claim enters a quarantined review signal. Exact object
# matching affects the evidence label, not the unvalidated severity or event
# level. This preserves potentially genuine unmatched findings without letting
# model self-labeling create an operational error state.
mapfile -t SECURITY_REVIEW_COUNTS < <(python3 - "$EVIDENCE_FILE" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
print(int(value.get("critical_security_count") or 0))
print(int(value.get("critical_security_object_matched_count") or 0))
print(int(value.get("unverified_security_count") or 0))
PY
)
SECURITY_REVIEW_COUNT="${SECURITY_REVIEW_COUNTS[0]:-0}"
MATCHED_CRITICAL_SECURITY="${SECURITY_REVIEW_COUNTS[1]:-0}"
UNVERIFIED_CRITICAL_SECURITY="${SECURITY_REVIEW_COUNTS[2]:-0}"
if [[ "$SECURITY_REVIEW_COUNT" -gt 0 ]]; then
  printf '{"project":"%s","source":"%s.reflect","eventType":"reflection.security_review_requested","level":"warn","sourceType":"system","timestamp":%s,"note":"typed reflection security claim requires independent review","ref":"%s","details":{"count":%d,"objectMatchedCount":%d,"unverifiedCount":%d,"evidenceFile":"%s","invocationManifest":"%s","severityJudgmentValidated":false,"executable":false}}\n' \
    "$PROJECT" "$PROJECT" "$(date -u +%s%3N)" "$RAW_REFLECTION_FILE" \
    "$SECURITY_REVIEW_COUNT" "$MATCHED_CRITICAL_SECURITY" \
    "$UNVERIFIED_CRITICAL_SECURITY" "$EVIDENCE_FILE" "$INVOCATION_MANIFEST" \
    >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null || true
fi

# Synthesis consumes a separate projection with proposal content removed.
# Full proposals remain in the raw reflection and private transcript for
# empirical study, but cannot flow into the executable handoff loop by glob.
if ! python3 "$LIB_DIR/reflection_synthesis_view.py" \
    --reflection "$RAW_REFLECTION_FILE" \
    --evidence "$EVIDENCE_FILE" \
    --manifest "$INVOCATION_MANIFEST" \
    --output "$SYNTHESIS_PROJECTION_CANDIDATE" \
    --artifact-path "$OUTPUT_FILE"; then
  echo "reflect[$PROJECT]: synthesis projection failed; raw reflection retained" >&2
  emit_reflection_failure_telemetry "synthesis_projection_failed" 7
  exit 7
fi
if ! mv -- "$SYNTHESIS_PROJECTION_CANDIDATE" "$OUTPUT_FILE"; then
  emit_reflection_failure_telemetry "synthesis_projection_publication_failed" 7
  exit 7
fi
if ! python3 "$LIB_DIR/reflection_synthesis_view.py" \
    --reflection "$RAW_REFLECTION_FILE" \
    --evidence "$EVIDENCE_FILE" \
    --manifest "$INVOCATION_MANIFEST" \
    --output "$OUTPUT_FILE" \
    --finalize-manifest; then
  rm -f -- "$OUTPUT_FILE"
  emit_reflection_failure_telemetry "synthesis_manifest_finalization_failed" 7
  exit 7
fi
echo "reflect[$PROJECT]: raw reflection -> $RAW_REFLECTION_FILE"
echo "reflect[$PROJECT]: synthesis projection -> $OUTPUT_FILE"
echo "reflect[$PROJECT]: evidence attestation -> $EVIDENCE_FILE"

SUPPRESSED_QUESTION_LINES="$(python3 - "$INVOCATION_MANIFEST" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
print(int((value.get("normalization") or {}).get("question_lines_suppressed") or 0))
PY
)"
if [[ "$SUPPRESSED_QUESTION_LINES" -gt 0 ]]; then
  echo "reflect[$PROJECT]: normalized $SUPPRESSED_QUESTION_LINES model-routed question line(s) out of the advisory projection" >&2
  printf '{"project":"%s","source":"%s.reflect","eventType":"info","level":"warn","sourceType":"system","timestamp":%s,"note":"reflection normalization suppressed model-routed question lines","ref":"%s","details":{"questionLinesSuppressed":%d,"invocationManifest":"%s"}}\n' \
    "$PROJECT" "$PROJECT" "$(date -u +%s%3N)" "$OUTPUT_FILE" \
    "$SUPPRESSED_QUESTION_LINES" "$INVOCATION_MANIFEST" \
    >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null || true
fi

mapfile -t REFLECTOR_STATE < <(python3 - "$INVOCATION_MANIFEST" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
print(value.get("provider") or "unknown")
print(value.get("model") or "unknown")
print(value.get("effort") or "unknown")
PY
)
REFLECTOR_PROVIDER="${REFLECTOR_STATE[0]:-unknown}"
REFLECTOR_MODEL="${REFLECTOR_STATE[1]:-unknown}"
REFLECTOR_EFFORT="${REFLECTOR_STATE[2]:-unknown}"

# Record the model state of the reflector and the model mix of source
# assistant messages in the same 12h window. This is a derivative sidecar;
# capture failure is visible but deliberately non-blocking.
PROVENANCE_FILE="${RAW_REFLECTION_FILE%.md}.provenance.json"
if ! python3 "$LIB_DIR/reflection-provenance.py" \
    --trace-file "$WORKSPACE_TELEMETRY_DIR/session-trace.jsonl" \
    --project-dir "$PROJECT_DIR" \
    --hours 12 \
    --reflector-provider "$REFLECTOR_PROVIDER" \
    --reflector-model "$REFLECTOR_MODEL" \
    --reflector-effort "$REFLECTOR_EFFORT" \
    --reflector-invocation-manifest "$INVOCATION_MANIFEST" \
    --output "$PROVENANCE_FILE"; then
  echo "reflect[$PROJECT]: WARNING — model provenance sidecar failed" >&2
  mkdir -p "$WORKSPACE_TELEMETRY_DIR" 2>/dev/null || true
  printf '{"project":"%s","source":"%s.reflect","eventType":"failure","level":"warn","sourceType":"system","timestamp":%s,"details":{"reason":"model_provenance_sidecar_failed","reflection":"%s"}}\n' \
    "$PROJECT" "$PROJECT" "$(date -u +%s%3N)" "$OUTPUT_FILE" \
    >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null || true
else
  echo "reflect[$PROJECT]: model provenance -> $PROVENANCE_FILE"
fi
