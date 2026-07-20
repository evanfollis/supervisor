# Adversarial review — test-surface witness

- Commit: `ae8057025a0accd8f2ffcb32becdd3ce8b9e41be`
- Reviewer: Codex subscription CLI, `gpt-5.5`, read-only sandbox
- Review rounds: 3
- Disposition: findings accepted and corrected before publication

## Findings and corrections

1. **Static AST discovery could be mistaken for runner collection.** The first
   draft counted test-shaped functions without proving that the repository's
   runner would execute them. The design was changed to witness the runner's
   explicit `TESTS` contract.
2. **Importing tests or invoking a repo-owned collector would execute untrusted
   code in the deploy credential boundary.** The executable collector modes
   were removed. The shipped witness is passive: it parses files but never
   imports or executes repository code.
3. **A hand-maintained runner list could silently omit a new test.** The final
   checker rejects every `test_*` function absent from `TESTS`, and a regression
   test proves that orphan functions fail before manifest comparison.
4. **Opaque fingerprints invite mechanical approval.** The manifest now stores
   exact file and case identities. Failure output names additions and removals,
   so the review diff exposes the semantic inventory change directly.

## Preserved raw record

Full transcripts remain in the private runtime evidence store:

- `test-collection-witness-adversarial-review-raw-2026-07-20T10-36-00Z.txt`
  — SHA-256 `ab90ff5861b74228e65e09128f0c886a99897bfb5c4d97947ca58ff401f0f1ae`
- `test-collection-witness-adversarial-review-raw-2026-07-20T10-41-00Z.txt`
  — SHA-256 `6e3d8558edd93bb3b09108e6d5dc3107eac143b032d3a8ce3347844389b2f1af`
- `test-collection-witness-adversarial-review-raw-2026-07-20T10-46-00Z.txt`
  — SHA-256 `668a17d9e04df13fae4cd7f96b6f8a6f214c5b8f942654a9ef616103aa371957`

The checked-in receipt deliberately excludes private runtime paths and full
transcript bodies; hashes preserve linkage without projecting internal records.
