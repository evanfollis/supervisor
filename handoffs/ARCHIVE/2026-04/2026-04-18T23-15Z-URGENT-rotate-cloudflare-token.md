---
priority: URGENT
to: executive / principal
from: executive session 847b6afa-1693-46c8-948d-af85a892017a
date: 2026-04-18T23:~15Z
re: Burned Cloudflare API token — rotation required
---

# URGENT — rotate leaked Cloudflare API token

## What happened

On 2026-04-18T12:32:24Z the principal pasted a Cloudflare API token
(`cfut_cAt4F3J…9994b`) into session `40788ae9` as part of a 5-numbered-answer
reply to earlier questions. The token has now sat plaintext in
`/root/.claude/projects/-opt-workspace/40788ae9-1924-485e-b63d-e2d80f8b125c.jsonl`
for 11+ hours.

That file is readable by every session on this host AND is ingested by the
12h reflection jobs (which produce `.meta/*-reflection-*.md` files and spawn
subprocesses that see the full transcript). The token is effectively public
to the entire agent stack.

## What the principal needs to do (60 seconds)

1. Cloudflare dashboard → My Profile → API Tokens
2. Find the token starting with `cfut_cAt4F3J` — **Roll** (or Delete + Create
   New with equivalent scopes: Cloudflare Pages, DNS for synaplex.ai,
   Workers if needed).
3. Copy the new token. **Do NOT paste it in chat.**
4. From a local shell on the server:
   ```
   install -m 0600 /dev/stdin /opt/workspace/runtime/.secrets/cloudflare_api_token
   <paste token>
   <Ctrl-D>
   ```
5. Reply in chat: "token rotated" (no value).

## What agent sessions must NOT do until rotation completes

- Do NOT install `wrangler` and attempt a deploy with the old token. That
  would upgrade a leaked-credential near-miss to a live-use incident.
- Do NOT copy the old token to `.secrets/` or anywhere else. It's compromised.

## After rotation

- Executive will install `wrangler`, read the rotated token from
  `.secrets/cloudflare_api_token`, and execute the three pending deploys
  (preflight landing, LCI intake on CF Pages, blog posts on CF Pages).
- The old token remains in the JSONL transcript forever (append-only). That's
  why rotation is the only safe move.

## Structural follow-up

- ADR-0025 (proposed) introduces a credential-shaped-string detector that
  would emit this handoff automatically on the turn the paste happens, rather
  than 11 hours later.
- `/opt/workspace/CLAUDE.md` policy delta (per ADR-0025): credentials never
  go in chat; they go from clipboard directly to `runtime/.secrets/<name>`.

See FR-0032 for the full failure-class writeup.
