# Decisions

Append-only architectural decision records for the supervisor agent and the
workspace it manages.

## Format

One file per decision. Filename: `NNNN-slug.md` (zero-padded 4-digit number, lowercase-kebab slug).

```
# ADR-NNNN: <title>
Date: YYYY-MM-DD
Status: proposed | accepted | superseded-by-NNNN

## Context
What prompted this decision. Evidence, constraints, prior art.

## Decision
The actual choice. One paragraph or a short bulleted list. No fluff.

## Consequences
What this enables, what it forecloses. Especially: what becomes harder.

## Alternatives considered
What else was on the table and why it lost.
```

## Rules

- **Append-only.** Never edit an accepted ADR except to change its status to `superseded-by-NNNN`. If the facts change, write a new ADR that supersedes the old one.
- **One decision per file.** Don't pile unrelated choices into one doc.
- **Numbered sequentially.** No gaps, no reservations.
- **Cite sources.** If a decision rests on evidence, link to the file/commit/reflection.

## When to write one

Write an ADR when any of these applies:

- A choice crosses project boundaries (affects more than one repo)
- A choice changes a contract declared in `/opt/projects/CLAUDE.md` or in `context-repository/`
- A choice introduces or retires a shared substrate (reflection loop, session supervision, server-maintenance job, etc.)
- A choice rejects a path the user or a reviewer advocated for — record the reasoning for future instances

Don't write an ADR for routine implementation choices. Those go in commit messages.
