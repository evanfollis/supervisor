# FR-0039: Synthesis stub propagation — LATEST_SYNTHESIS pointer updated with sub-100-byte stubs

Captured: 2026-04-28T04:50Z (first detection); confirmed 3rd consecutive cycle 2026-04-28T08:50Z
Source: supervisor-tick observation
Status: open

## What happened

`synthesize.sh` runs every 12h and is supposed to produce a rich cross-cutting synthesis file.
On at least 3 consecutive runs (2026-04-27T15:27Z, 2026-04-28T03:25Z, and possibly others),
the output was a 67-byte stub. `synthesize.sh` unconditionally updates `LATEST_SYNTHESIS` to
point at the new file regardless of its size, propagating the corrupt pointer to all sessions.

## Why it matters

- Sessions reading `LATEST_SYNTHESIS` receive a stub with no actionable content
- Synthesis translator generates "carry-forward" proposals from nothing, cluttering INBOX
- The dispatch obligation (24h) cannot be met because there's nothing to dispatch
- The meta-loop's primary output channel is degraded for multi-cycle windows

## Root cause hypothesis

The `synthesize.sh` script produces empty or near-empty output when:
(a) the Claude invocation times out or is rate-limited
(b) the input reflection files are empty or below a size threshold
(c) the script exits early due to an error condition but still writes a stub file

The size gate is absent: the script does not check whether the output meets a minimum
size threshold before updating `LATEST_SYNTHESIS`.

## Proposed fix (from synthesis proposal, 5th cycle)

Add to `synthesize.sh` after writing the output file:

```bash
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
if [ "$OUTPUT_SIZE" -lt 500 ]; then
  echo "synthesize: WARNING — output is ${OUTPUT_SIZE} bytes (< 500), not updating LATEST_SYNTHESIS" >&2
  exit 0
fi
# proceed to update LATEST_SYNTHESIS pointer
```

This is a scripts/lib/ change (Tier C from tick sandbox). Attended session must implement.

## Status tracking

- 2026-04-28T04:50Z: FR first claimed as created (ghost)
- 2026-04-28T08:50Z: FR materialized on disk; proposal-synthesis-output-gate in INBOX (5th cycle)
