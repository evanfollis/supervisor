# FR-0040: FR-candidates aging without promotion

Captured: 2026-04-30T02:49Z
Source: reflection (2026-04-30T02:27Z §FR-CANDIDATE-D); reflection pattern
Status: open

## What happened

Three consecutive reflection windows (2026-04-29T02:26Z, 2026-04-29T14:26Z, 2026-04-30T02:27Z)
identified the same two FR candidates (S3-P2 invocation failure, synthesis_reviewed emission
gap) and labeled them "unwritten candidates for next attended session." Neither was promoted
to a real FR-NNNN record across those three windows.

The attended-session drought (~180h as of 2026-04-30T02:27Z) is the proximate cause: Tier-A
friction records require a tick or attended session to commit them to main, and ticks have
been writing to unmerged branches. But the higher-order failure is that the reflection
output contract says "surface candidates," while there is no corresponding mechanism to
ensure candidates become records.

## Why it matters

An FR-candidate sitting unwritten in 3 reflection files is invisible to the governance
stack. The idea-ledger, active-issues, and disposition machinery only track records — not
candidates embedded in prose. Three windows of a candidate without promotion means the
structural problem it describes goes unaddressed longer than it should.

The reflection system is supposed to be a work queue, not a diagnostic archive. When
candidates age without promotion, that purpose is lost.

## Root cause / failure class

No formal gate exists between "FR-candidate identified in reflection" and "FR-NNNN file
written to friction/." The gap is filled by attended sessions (which see the reflection
and act) or by ticks (which can write Tier-A FR files). During an attended-session drought,
if tick branches aren't merging to main, candidates accumulate without resolution.

## Fix required

This is a symptom of the attended-session drought and the ghost-state tick-branch pattern
(FR-0038). When those are fixed, this class should resolve automatically.

A structural improvement: reflection should write FR-NNNN stubs for candidates it has
identified 2+ times, even without full root-cause analysis. A stub is better than a
prose candidate that disappears in the next reflection.

## Remaining work

- Land FR-0038 and FR-0039 (done this tick via direct main commit)
- Resolve attended-session drought (principal must attach)
- Consider adding a "reflection writes FR stubs for 2nd-window candidates" policy
