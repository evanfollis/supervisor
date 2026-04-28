---
id: FR-0039
title: Synthesis stub propagation — synthesize.sh emits 67-byte stubs when output exceeds limit
status: Open
created: 2026-04-28
severity: high
---

# FR-0039: Synthesis stub propagation

## Pattern

The synthesis script (`scripts/lib/synthesize.sh`) occasionally produces 67-byte "stub" output files instead of substantive synthesis. These stubs get written as `LATEST_SYNTHESIS`, making the meta-loop output appear present but contain no actual cross-cutting proposals. Two of three synthesis cycles between Apr 26-28 produced stubs.

## Root cause

The synthesis script invokes a Claude session to read reflections and produce a synthesis document. When the invocation fails or returns truncated output, the script writes whatever it received (potentially just a stub/error header) without a size gate. A 67-byte output is clearly not a valid synthesis but is accepted as-is.

## Evidence

- Events: `{"note":"tick complete on main: ... LATEST_SYNTHESIS stub 4th cycle..."}` (14:24Z reflection)
- Cross-cutting synthesis 2026-04-28T15:28Z confirmed: "Two of three intervening synthesis runs produced 67-byte stubs"
- Fix proposed: `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` in INBOX (36h old)
- Current state: LATEST_SYNTHESIS is 17KB (valid synthesis from 15:28Z), but fix is needed to prevent recurrence

## Fix path

5-line bash size gate in `scripts/lib/synthesize.sh`: if output < N bytes, abort and emit `synthesis_stub_detected` event instead of writing corrupt LATEST_SYNTHESIS. The proposal in INBOX specifies the exact code change. Requires operator/attended session to edit `scripts/lib/` (Tier-C from tick sandbox).

## Impact

Synthesis is the primary cross-cutting analysis surface. 2-of-3 stub cycles means the meta-loop produced no actionable output for 24h. INBOX proposals don't land because the synthesis loop that validates them is intermittently broken.
