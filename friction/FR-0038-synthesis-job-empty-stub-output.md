---
id: FR-0038
slug: synthesis-job-empty-stub-output
status: open
created: 2026-04-25
discovered-by: supervisor-tick-2026-04-25T18-47-34Z
---

# FR-0038: Synthesis job produces 67-byte empty stubs

## Symptom

`workspace-synthesize.sh` ran on 2026-04-25T03:27Z and 15:28Z and produced
67-byte output files containing only the path to the synthesis artifact —
no actual content. The downstream `synthesis-translator.sh` interpreted the
stub as a real synthesis and filed INBOX proposals based on empty content.

## Impact

Two successive synthesis cycles silently produced no cross-cutting analysis
while appearing to succeed. Translator wrote suspect INBOX proposals. The
LATEST_SYNTHESIS pointer referenced a corrupt stub.

## Root cause (hypothesis)

`synthesize.sh` output capture path (`tee` or redirect) failed silently when
the Claude session exited without producing the expected output structure.
The script wrote the path/header to the output file but the session content
never appended.

## Status

Proposal `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` in INBOX
proposes a size gate fix. Not yet implemented. The synthesis job appears to
have recovered (recent synthesis files have substantive content) but no
structural guard was added to prevent recurrence.
