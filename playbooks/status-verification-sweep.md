# Playbook: status-verification sweep

**When**: before the executive emits any principal-facing status, run-list,
recommendation to provision paid services, setup walkthrough, credential
request, or reversal of a principal statement.

**Why**: recorded failure class (FR-0032). Sessions repeatedly ask the
principal for work they've already done, recommend paid services already
provisioned, or reverse principal statements — all because they read stale
narrative surfaces instead of primary state.

**Budget**: under 10 seconds. This is not optional work.

## Step 1 — Refresh the verified-state snapshot

```bash
/opt/workspace/supervisor/scripts/lib/verify-state.sh
```

Writes to `supervisor/system/verified-state.md`. The script queries:
- Host (`uname -r`, `/boot/vmlinuz-*`, uptime, df, free)
- All workspace systemd units (`is-active`, start time)
- All known public URLs (`curl -s -o /dev/null -w "%{http_code}"`)
- Supervisor git HEAD and dirty-tree status
- INBOX + general handoffs
- Aged tick branches
- Last 48h of principal user turns from JSONL (auto-filtered)

Takes ~5 seconds.

## Step 2 — Read the snapshot, not the narrative surfaces

Read `system/verified-state.md` for state claims. **Do not** base
state claims on:

- `active-issues.md` — this is curated pressure, not state. It drifts.
- Tick report narrative.
- Handoff text older than 24h.
- Synthesis observations.
- Your own prior messages in the current session.

If `active-issues.md` contradicts `verified-state.md`, the verified
snapshot wins and `active-issues.md` is wrong. Fix `active-issues.md`
in the same turn.

## Step 3 — Scan recent principal turns before asserting something is open

The snapshot's "Recent principal statements" section is your second primary
source. Before writing any of the following, check that section:

- "Evan needs to decide X" → did Evan already answer in the last 48h?
- "Evan needs to provide credential Y" → is the secret already at
  `runtime/.secrets/<y>`? Did Evan paste it in chat (rotate if so)?
- "Service Z is not deployed" → did Evan say otherwise in a user turn?
- "We should provision paid service W" → is W already in
  `paid-services.md`? Has Evan mentioned it in recent chat?

When in doubt, `grep` the JSONL directly:

```bash
grep -hoE '("content":"[^"]{20,}|"text":"[^"]{20,})' \
  /root/.claude/projects/-opt-workspace/*.jsonl 2>/dev/null \
  | sort -u | grep -iE '<topic>'
```

Principal statements are primary; everything else is derivative.

## Step 4 — Emit with receipts, not summaries

Each principal-facing claim must carry a one-line receipt tracing back to
primary evidence:

- ✅ "Kernel reboot pending — `uname -r` shows 6.8.0-107, `/boot/vmlinuz-6.8.0-110` installed (verified-state.md §Host)"
- ❌ "Kernel reboot pending per active-issues.md"

- ✅ "launchpad-lint live on both Hetzner (systemd `launchpad-lint.service` active since 2026-04-17T09:18:26Z; `curl skillfoundry.synaplex.ai/products/launchpad-lint/` = 200) and agenticmarket Render (principal statement 2026-04-18T12:47Z)"
- ❌ "launchpad-lint deployed"

## Step 5 — If something wasn't verified, say so

If a claim couldn't be verified via primary source, the response must name
the uncertainty explicitly. Do not guess, do not infer from stale
narrative. "I don't know whether X is live; `curl` returned 000 and no
systemd unit matches" is a valid answer. A confident wrong answer costs
the principal time and money.

## Common re-run triggers

- Session has been open >15 min; snapshot may be stale.
- Principal statement in chat that contradicts current state.
- Host was rebooted.
- A deploy was made.
- A paid service was provisioned or cancelled.

Running the script again is cheap. Running on stale state produces the
FR-0032 failure class.

## Related

- `supervisor/AGENT.md` §Primary-verification gate — the blocking rule.
- `supervisor/friction/FR-0032-principal-input-dropped-or-reversed.md` — why this playbook exists.
- `supervisor/system/verified-state.md` — the snapshot you must read.
- `supervisor/system/paid-services.md` — paid-service asset register.
- Memory: `feedback_verify_deploy_state_first.md`,
  `feedback_capture_principal_decisions_in_turn.md`,
  `feedback_no_credentials_in_chat.md`.
