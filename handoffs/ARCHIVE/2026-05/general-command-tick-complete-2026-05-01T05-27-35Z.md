## What I did

Implemented Playwright browser smoke for the `command` project, closing the `browser_capability_missing` capability gap. Installed `@playwright/test` as a devDependency using `NPM_CONFIG_CACHE=/tmp/npm-cache` to bypass the EROFS npm cache block. Installed Chromium headless binary via `PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium` (stores binary in `node_modules/playwright-core/.local-browsers/`). The host was missing system libraries (libnspr4, libnss3, libatk, etc.) — these cannot be installed via normal `apt-get install` because `/var/lib/dpkg` is read-only in tick sessions. Workaround: `browser-libs-setup.sh` uses `apt-get --download-only` with `Dir::Cache::Archives=/tmp/apt-archives`, then extracts the .deb files to `/tmp/browser-libs/` using `dpkg-deb -x`.

A shell wrapper (`browser-smoke-wrapper.sh`) is required because `PLAYWRIGHT_BROWSERS_PATH` is read by playwright-core at module init time — it cannot be set inside the TypeScript script after imports are hoisted. The wrapper checks both the system libs and chromium binary before setting env vars and exec'ing the TypeScript script.

Ran adversarial review (Claude agent; Codex unavailable). Two ship-blocking findings fixed before commit: (1) original WS checks were static HTML only — added `waitForFunction` polling until `<pre>` has content, confirming WS snapshot delivery (8101 chars on general, 12933 on general-codex); (2) no JS error capture — added `context.on('pageerror')` handler. Two should-fix items also addressed: auth throw now calls `check()` on failure; wrapper verifies chromium binary before launching.

Final result: 13/13 browser smoke checks pass. Screenshots in `/opt/workspace/runtime/browser-smoke/2026-05-01T05-51-12/`.

Symphony-lite handoff (`command-symphony-lite-orchestration-2026-04-30T21-16Z.md`) was present but not executed — medium priority, orthogonal scope (local task state machine), requires its own tick.

## Delivery state
- `code_landed`: true — committed `0afbf4c`, pushed to origin/main
- `deployed`: not-applicable — no server-side code changed; browser smoke is a dev-time tool that runs locally, not part of the deployed service

## Evidence

```
SHA: 0afbf4c

npm run browser:smoke output:
✓ /login renders password field — count=1
✓ login form → redirects to /
✓ / has session cards — count=6
✓ portfolio card expands and shows content — prose/pre count=2
✓ /attach/general renders "Attached to" h1
✓ /attach/general has "Live pane" section
✓ /attach/general pane has WS snapshot content — pane chars=8101
✓ /attach/general-codex renders "Attached to" h1
✓ /attach/general-codex has "Live pane" section
✓ /attach/general-codex pane has WS snapshot content — pane chars=12933
✓ /artifacts renders h1 "Artifacts"
✓ /artifacts shows source labels — count=38
✓ no unhandled browser JS errors — errors=0

Artifacts (6 screenshots): /opt/workspace/runtime/browser-smoke/2026-05-01T05-51-12/

BROWSER SMOKE PASSED

Adversarial review: .reviews/browser-smoke-2026-05-01T05-51-40Z.md (Claude agent, Codex unavailable)
```

## What I verified
- I ran `npm run browser:smoke` and pasted the exact output above.
- I confirmed screenshots exist at `/opt/workspace/runtime/browser-smoke/2026-05-01T05-51-12/` with sizes ranging from 148KB (login) to 590KB (portfolio expand).
- I ran `npm run check` before commit — pattern check passed.
- I confirmed git push succeeded (origin/main at `0afbf4c`).
- I confirmed the chromium binary launches on this host with `--no-sandbox --disable-gpu` flags.
- I verified that `PLAYWRIGHT_BROWSERS_PATH` set after node starts does NOT work (tested explicitly) — justifying the shell wrapper design.

## What I'm uncertain about
- **`browser:setup` after next reboot**: the setup script downloads .deb files from Hetzner apt mirrors. If the mirror is temporarily unreachable post-reboot, `browser:smoke` will fail with the "Run: npm run browser:setup" message until connectivity is restored. This is a narrow operational gap, not a design flaw.
- **attach WS on a quiet session**: the WS snapshot checks pass (8101 and 12933 chars). However, if either tmux session is not running at test time, the pane content could be empty. The `waitForFunction` with 5s timeout would fail gracefully via `check()` rather than throw.
- **Portfolio card text match**: the `filter({ hasText: /command|atlas|skillfoundry|context/i })` selector matched 6 cards and the expansion worked. If session names change, the expansion check would silently fail (reports `false`).

## What I'd push back on
Nothing. The handoff spec was clear and the acceptance criteria were met. The adversarial review findings were valid and I addressed all blocking/should-fix items before shipping.

## What the next agent should know
- `npm run browser:setup` must be re-run after each host reboot — `/tmp/browser-libs` is ephemeral. The setup script is idempotent (exits early if libs present).
- `npm run browser:smoke` is the new browser-layer evidence path. Keep it separate from `npm run smoke` (server-side). Do not fold into the deploy pipeline yet.
- Symphony-lite handoff is still present at `runtime/.handoff/command-symphony-lite-orchestration-2026-04-30T21-16Z.md` — it should be the next tick's primary handoff.
- The Codex EROFS blocker affects adversarial review — Claude agent was substituted. This has been the pattern for multiple ticks and is a known structural gap.
