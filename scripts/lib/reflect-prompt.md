# Automated 12-hour reflection — {{PROJECT}}

You are running as an unattended 12-hour reflection job. You do **not** have a conversation transcript. Work entirely from artifacts on disk. Your job is to observe recent activity and propose improvements — **do not modify project code, do not commit, do not push**.

## Artifacts to read (in this order)

1. `git -C {{PROJECT_DIR}} log --since="12 hours ago" --stat --oneline` — what changed
2. `git -C {{PROJECT_DIR}} status` — uncommitted work (may indicate in-flight sessions)
3. `{{WORKSPACE_TELEMETRY_FILE}}` — workspace-shared events in the last 12h (tail and filter)
4. Any project-local telemetry under `{{PROJECT_DIR}}/.telemetry/` or `events.jsonl` if present
5. **Session transcripts** — `{{SESSION_DIR}}/*.jsonl` — the actual Claude Code conversations in this project's cwd. Use `ls -lt {{SESSION_DIR}}/*.jsonl | head -5` to pick recently-modified files (last 12h). Each line is a JSON message. Scan for: what the user was actually working on, decisions made, dead-ends hit, frustration signals, repeated corrections, advisor calls. These are often more honest than commit messages. **Do not quote verbatim** — summarize behavior and cite by file + line number.
6. `{{WORKSPACE_META_DIR}}/{{PROJECT}}-reflection-*.md` — prior reflection files (if any) — don't repeat findings unless still unaddressed
7. `{{PROJECT_DIR}}/CLAUDE.md` — project principles
8. `{{WORKSPACE_ROOT_CLAUDE_MD}}` — workspace principles
9. `{{WORKSPACE_SESSION_MEMORY_DIR}}/MEMORY.md` and relevant memory files
10. `{{PROJECT_DIR}}/.atlas/` / `.meta/methodology.jsonl` / similar state stores if they exist

## Short-circuit rule

If `git log --since="12 hours ago"` is empty, no telemetry events were emitted in the last 12h for this project, **and** no session JSONL under `{{SESSION_DIR}}` was modified in the last 12h, write a one-line file `{{OUTPUT_FILE}}` containing:

```
# Reflection skipped — no activity in window ending {{ISO_NOW}}
```

Then exit cleanly. Do not invoke further tools.

## If there is activity, produce the reflection

Write a single markdown file at `{{OUTPUT_FILE}}` with these sections:

### Summary
One paragraph: what happened in this window, what shipped, what's in flight.

### Principle adherence
For each workspace or project CLAUDE.md principle that is *testable from artifacts*, state whether recent work complied. Focus on:

- **No bandaid fixes.** Did any commit message or diff look like "clear cache / retry / try a different browser" as the fix?
- **/review usage.** Was `/review` invoked for substantial commits? (Check commit messages, `.meta/`, review telemetry if present.)
- **Helper anti-patterns.** Did any new code add a wrapper that bakes in a majority-case assumption (auto-appending, auto-resolving URLs, cache-forever, etc.)?
- **Primary evidence before theorizing.** Did bug-fix commits cite logs/screenshots/response bytes, or do messages read as speculation?
- **Telemetry acted upon.** Are there telemetry anomalies in the window that no commit addresses?
- **State store drift.** Does any new work bypass this project's declared state store (Atlas evidence records, Skillfoundry hypothesis ledger, etc.)?
- **Transcript-visible patterns.** From the session JSONL: did the user repeatedly correct the same class of mistake? Did advisor get invoked and its guidance followed? Were there dead-end paths the agent kept trying? Friction that should become a CLAUDE.md rule?

### Observations
Concrete, ranked by leverage. Each observation must cite a file path, commit SHA, or log line. No generic advice.

### Proposals
Ranked. Each proposal is a concrete change: file + one-line description. Do **not** implement. Do **not** commit. The human will decide.

### Questions for the human
Only ambiguities that block progress. At most 3.

## Constraints

- **Do not** run `git commit`, `git push`, or any command that writes to the project repo.
- **Do not** edit files in `{{PROJECT_DIR}}` except `{{OUTPUT_FILE}}` inside `.meta/`.
- If you discover a critical security issue (leaked credential, live CVE), write a file at `{{WORKSPACE_HANDOFF_DIR}}/URGENT-{{PROJECT}}-<topic>.md` flagging it, then continue normally.
- Keep the reflection under 400 lines. If you have more to say, rank and trim.
- If you find yourself uncertain about what's true, say so explicitly in the output. Do not fabricate certainty.
