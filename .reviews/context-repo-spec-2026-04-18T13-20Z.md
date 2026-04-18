Reading additional input from stdin...
OpenAI Codex v0.120.0 (research preview)
--------
workdir: /opt/workspace/supervisor
model: gpt-5.4
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019da0ba-8747-7c11-9eec-2aa26d40c53c
--------
user
Adversarial review of /opt/workspace/projects/context-repository/docs/agent-context-repo-pattern.md.

You are a skeptical reviewer. Read the target file carefully. Then produce a review with exactly these three sections:

1. **Most dangerous assumption** — the claim that if wrong, produces the largest blast radius.
2. **Missing failure mode** — what the design does not account for that is likely to happen in practice.
3. **Boundary most likely to be collapsed in practice** — where the nominal separation will erode under real use.

Cite specific line numbers. Be terse and concrete. End with a 1-2 sentence overall verdict. Under 500 words total. Do not edit any files.
codex
I’m treating this as an executive review task, not an implementation task. I’ll attest capabilities, then read the target document closely and produce the three-point adversarial review with cited lines only.
exec
/bin/bash -lc 'nl -ba /opt/workspace/projects/context-repository/docs/agent-context-repo-pattern.md' in /opt/workspace/supervisor
 succeeded in 0ms:
     1	---
     2	name: Agent Context Repository Pattern
     3	description: Canonical spec for how agents maintain file-based persistent context — five invariants, required mechanics, future work
     4	type: spec
     5	updated: 2026-04-18
     6	---
     7	
     8	# Agent Context Repository Pattern
     9	
    10	This document specifies the canonical pattern for agent context repositories.
    11	Any agent maintaining a scoped context repo should treat this as the reference.
    12	
    13	---
    14	
    15	## What is an agent context repository?
    16	
    17	A file-based record of current domain state that an agent reads at session start
    18	and updates at session end. It is not a log. It is not an abstract schema layer.
    19	It is the agent's working memory made durable — the thing that makes the next
    20	session possible without starting cold.
    21	
    22	Each agent on the workspace maintains their own. No centralized aggregation.
    23	No hub. Each agent owns their domain.
    24	
    25	---
    26	
    27	## The five invariants
    28	
    29	### 1. Small front door
    30	
    31	A single entry-point file — `CURRENT_STATE.md` or `CONTEXT.md` — that any fresh
    32	agent can read in under two minutes and orient completely.
    33	
    34	**What this means concretely:**
    35	- The file fits in a single screen. No scrolling required to get the picture.
    36	- It answers: what is this repo/domain, what is currently in progress, what is
    37	  broken, what should the next agent read first.
    38	- No hunting. A cold agent reads one file and knows where to start.
    39	
    40	**The test:** After writing it, pretend you've never seen this repo. Read only
    41	the front door. Do you know what to do? If not, the front door has failed.
    42	
    43	### 2. Progressive disclosure
    44	
    45	Behind the front door, more detailed files for specific concerns. The front door
    46	is complete enough to start; depth is available when detail matters.
    47	
    48	**What this means concretely:**
    49	- The front door contains pointers, not full content. "See `docs/foo.md` for
    50	  the full spec" is correct. Inlining the full spec is not.
    51	- Depth files are organized by concern (e.g., `docs/`, `decisions/`), not by
    52	  date or session number.
    53	- The front door's pointers stay current. A pointer to a deleted file is worse
    54	  than no pointer.
    55	
    56	**What does NOT go here:** Don't create depth for depth's sake. If one file
    57	covers the domain adequately, one file is correct. Progressive disclosure is
    58	for when complexity genuinely requires it.
    59	
    60	### 3. Overwritten, not appended
    61	
    62	These are state files. When things change, the file changes. Git history carries
    63	the evolution; commit messages carry why.
    64	
    65	**What this means concretely:**
    66	- `CURRENT_STATE.md` describes current reality. Past reality lives in git log.
    67	- Do not add "Update 2026-04-16: ..." entries to state files. Update the state.
    68	- Do not maintain a session log within a state file. Write the current state.
    69	- Commit messages explain why the state changed. The file contains only what is
    70	  currently true.
    71	
    72	**Why this matters:** An append-only file grows stale at its top. Readers must
    73	read the whole file and mentally subtract old entries. Overwrite semantics mean
    74	the file is always accurate at the head.
    75	
    76	**The test:** Is the file's content true right now, or is it a log of things
    77	that were true at various points? If the latter, it's append-only and broken.
    78	
    79	### 4. Default behavior, not accessory
    80	
    81	The agent reads their context repo at the start of every session. The agent
    82	updates it before ending. This is not optional and not a reminder — it is the
    83	operating ritual.
    84	
    85	**Session start:**
    86	- Read the front door. Every session. Even if you think you know the state.
    87	- Read any pointed-to files relevant to the current task.
    88	- If something in the front door is stale, correct it before starting work.
    89	
    90	**Session end:**
    91	- Update the front door: what changed, what is now broken, what bit you,
    92	  what the next agent should read first.
    93	- Commit the update with a message explaining why the state changed.
    94	- Do not skip this step. A stale front door is indistinguishable from no
    95	  front door.
    96	
    97	**The test:** If an agent only updates the context repo when reminded, the
    98	system has failed. If the front door is more than one session stale, the agent
    99	is not using the pattern.
   100	
   101	### 5. Agent-owned design
   102	
   103	Each agent designs their own structure within these invariants. The pattern
   104	provides constraints, not a template. Two agents' context repos will look
   105	different. That is correct.
   106	
   107	**What this means concretely:**
   108	- Choose your own file names, sections, and organization.
   109	- If `CURRENT_STATE.md` serves you, use it. If `CONTEXT.md` is clearer for
   110	  your domain, use that. (The tick system checks both.)
   111	- Add depth files that match your domain's actual complexity — not what you
   112	  think a "proper" structure should look like.
   113	- Change the structure when it stops serving you. The invariants are permanent;
   114	  the implementation is not.
   115	
   116	**What NOT to do:** Don't copy another agent's structure because it looks right.
   117	Design for your domain. Don't add sections because they seem professional. Add
   118	them when you need them.
   119	
   120	---
   121	
   122	## Required mechanics
   123	
   124	The five invariants above are the philosophy. The mechanics below are *how*
   125	the philosophy gets delivered. Without them, the pattern reduces to "discipline
   126	to remember the invariants" — and discipline fails. The mechanics exist so
   127	that agents can cold-orient, skim for relevance, and have load-bearing files
   128	surfaced without explicit searching.
   129	
   130	These mechanics are required in every context repo. The reference implementation
   131	(this repo) must ship them. If it doesn't, fix it — not the spec.
   132	
   133	### M1. YAML frontmatter on every Markdown file
   134	
   135	Every `.md` file in a context repo carries a YAML frontmatter block at the top:
   136	
   137	```markdown
   138	---
   139	name: <short human-readable title>
   140	description: <one-line purpose; used by index.md and as navigation signal>
   141	type: <front-door | spec | directive | reference | decision | plan | finding | workflow | proposal | index | ...>
   142	updated: <YYYY-MM-DD>
   143	---
   144	```
   145	
   146	**Why:** Without frontmatter, a cold agent listing the filetree sees names only.
   147	Grep is the only discovery path. With frontmatter, descriptions surface via the
   148	generated index (M2) and make the filetree genuinely navigational.
   149	
   150	**Required fields:** `name`, `description`, `type`, `updated`. The `type` enum
   151	is loose — start with the values above, add repo-local types when a new class
   152	genuinely repeats. Don't over-schematize.
   153	
   154	**Optional fields:** repos may add their own (e.g., `status`, `owner`, `tags`).
   155	Don't gate on optional fields — a minimum-viable frontmatter is the four required
   156	fields and nothing else.
   157	
   158	### M2. Auto-generated `index.md` at repo root
   159	
   160	Each context repo has an `index.md` auto-generated from frontmatter:
   161	
   162	- Rebuilt by a script in `scripts/` (e.g., `build-index.sh`) that walks the
   163	  repo, extracts frontmatter, and writes a table of path + name + description
   164	  + type + updated.
   165	- Regenerated after any file add, remove, retitle, or frontmatter change.
   166	- Lists files *missing* frontmatter under a visible "Unindexed" section so
   167	  the gap is self-surfacing rather than silent.
   168	
   169	**Why:** The filetree in `ls` output is not the navigation surface; `index.md`
   170	is. A cold agent reads `CURRENT_STATE.md` for orientation, then `index.md` for
   171	navigation, then opens specific files. Three files to get from cold to working.
   172	
   173	**Authority:** `index.md` is generated, not hand-maintained. If the script
   174	doesn't produce the file you want, fix the script, not the output.
   175	
   176	### M3. `CLAUDE.md`-declared always-load list
   177	
   178	Each context repo's `CLAUDE.md` carries a `context-always-load:` block naming
   179	the files that must be read at session start:
   180	
   181	```yaml
   182	context-always-load:
   183	  - CURRENT_STATE.md
   184	  - index.md
   185	  - docs/<repo-specific-spec>.md
   186	```
   187	
   188	**Why:** `CLAUDE.md` is the Claude Code native always-loaded surface (auto-injected
   189	into the system prompt when present in the cwd). The inspiration's `system/`
   190	pinning concept maps to this: `CLAUDE.md` declares what *additional* files the
   191	agent must read before answering about this domain. An enforcement layer (see
   192	below) can read this declaration and inject the files automatically.
   193	
   194	**Length discipline:** keep the always-load list short. If it balloons, the
   195	front door has failed to summarize — fix the front door, not the list. Rule
   196	of thumb: 3-5 files is normal, 10+ is a signal that progressive disclosure has
   197	collapsed.
   198	
   199	### M4. Session-start read is enforced, not discretionary
   200	
   201	Discipline-only session-start reads fail. The workspace needs a mechanism that
   202	either:
   203	
   204	- injects the always-load files at session start (SessionStart hook), or
   205	- hard-fails a session that attempts substantive work before reading them, or
   206	- provides a `workspace.sh context` wrapper that must be invoked first.
   207	
   208	The specific mechanism is a workspace-level ADR
   209	(`supervisor/decisions/0021-session-start-context-repo-read-enforcement.md`).
   210	Until that ADR is accepted, agents must honor the always-load list manually —
   211	but the spec considers manual compliance a transitional state, not a target.
   212	
   213	### M5. Session-end update is enforced, not discretionary
   214	
   215	Symmetric to M4. The front door must be updated at session end or the ritual
   216	fails. Enforcement options parallel M4 (hook, gate, wrapper). The same ADR
   217	covers both.
   218	
   219	---
   220	
   221	## Future work (proposed, not active)
   222	
   223	- **Writer/retriever separation** — `docs/writer-retriever-separation-proposal.md`
   224	  describes a formalization where context-repo writes come only from a dedicated
   225	  writer path (reflection/synthesis pipeline), and the foreground agent operates
   226	  in retrieval-only mode. Status: proposed.
   227	
   228	---
   229	
   230	## What belongs in the front door
   231	
   232	- What the repo/domain is (one paragraph)
   233	- Current operational state (running, in-progress, broken, blocked)
   234	- What's actively in progress (with pointers to handoffs or specs)
   235	- What's currently broken or degraded
   236	- What the next agent must read first
   237	- Pointers to relevant depth files
   238	
   239	**Length target:** Fits in a single screen. If it's longer, something that
   240	belongs in a depth file is in the front door.
   241	
   242	---
   243	
   244	## What belongs behind the front door
   245	
   246	- Detailed specs for active work
   247	- Decision records for non-obvious choices
   248	- Domain-specific reference material the agent consults repeatedly
   249	- Context that is stable and deep (doesn't change every session)
   250	
   251	---
   252	
   253	## What does NOT belong in an agent context repository
   254	
   255	- **Raw logs and transcripts.** Session JSONL, append-only event logs, raw
   256	  command output. These belong in runtime directories, not the context repo.
   257	- **Abstract schemas and governance frameworks.** Type systems, object models,
   258	  and architecture governance are separate concerns. A context repo is state,
   259	  not specification.
   260	- **Personal data or credentials.** Scoped operational state only.
   261	- **Operational state for other agents' domains.** Each agent owns their domain.
   262	  If something affects another agent, write a handoff — don't absorb their
   263	  domain into your context repo.
   264	- **Speculative future content.** Document what is currently true. Don't document
   265	  what might be true if certain work gets done. If the work gets done, update
   266	  the state then.
   267	
   268	---
   269	
   270	## Front door naming convention
   271	
   272	The workspace tick system looks for `CONTEXT.md` first, then `CURRENT_STATE.md`.
   273	Either name works; the tick will inject whichever exists into the scheduled
   274	session's context window.
   275	
   276	Use `CURRENT_STATE.md` unless you have a specific reason to prefer `CONTEXT.md`.
   277	If you want a different name entirely, declare it in your `CLAUDE.md`:
   278	
   279	```
   280	context-front-door: STATUS.md
   281	```
   282	
   283	The important thing is consistency: use one name, commit to it, and keep
   284	the tick system in sync.
   285	
   286	---
   287	
   288	## Implementation guide
   289	
   290	A new agent setting up their context repo for the first time:
   291	
   292	1. Create `CURRENT_STATE.md` in the repo root. Answer: what is this domain,
   293	   what is currently in progress, what is broken, where should I start.
   294	2. Commit it. It is immediately useful even if rough.
   295	3. Update it at the end of every session. This is the only mandatory
   296	   maintenance.
   297	4. Add depth files only when complexity genuinely requires them. Link to them
   298	   from the front door.
   299	5. Evolve the structure when it stops working. There is no correct final form.
   300	
   301	**The minimum viable context repo is a single well-maintained file.** Start
   302	there. Only add structure when you feel the absence of it.
   303	
   304	---
   305	
   306	## This repo as reference implementation
   307	
   308	This repo (`context-repository`) is itself an instance of this pattern. Its
   309	front door is `CURRENT_STATE.md`. This document is depth, linked from the front
   310	door. The repo's own structure should demonstrate what the spec describes — not
   311	just describe it.
   312	
   313	If you find a tension between this spec and how this repo is actually organized,
   314	the repo is wrong and needs to change, not the spec.

exec
/bin/bash -lc './workspace.sh capabilities' in /opt/workspace
 succeeded in 0ms:
/opt/workspace/supervisor/scripts/lib/capability-attestation.sh: line 13: /opt/workspace/.capability-probe-2: Read-only file system
/opt/workspace/supervisor/scripts/lib/capability-attestation.sh: line 13: /opt/workspace/supervisor/.capability-probe-2: Read-only file system
/opt/workspace/supervisor/scripts/lib/capability-attestation.sh: line 13: /opt/workspace/runtime/.capability-probe-2: Read-only file system
/opt/workspace/supervisor/scripts/lib/capability-attestation.sh: line 13: /opt/workspace/projects/.capability-probe-2: Read-only file system
- posture: `workspace-root`
- effective role: `executive+supervisor (attached)`
- workspace write: `no`
- supervisor write: `no`
- runtime write: `no`
- project mutation: `no`
- host tmux control: `blocked`
- host systemd control: `blocked`
- network egress: `restricted`
- operator available: `no`

codex
I’ve got the document. The main pressure point is not the invariants themselves; it’s the assumption that enforcement and tooling will make them real instead of just aspirational.
codex
1. **Most dangerous assumption** — The design assumes session-start/session-end enforcement will actually exist and be reliable enough to make the ritual load-bearing rather than aspirational (lines 199-217), and further assumes `CLAUDE.md` is a viable universal declaration surface for that enforcement (lines 176-192). If that is wrong, every repo gets the appearance of durable working memory while silently drifting stale, which is worse than having no context repo because agents will trust bad state.

2. **Missing failure mode** — It does not account for concurrent writers. The spec requires every session to read at start and overwrite at end (lines 81-99, 213-217), but says nothing about two sessions reading the same front door and then racing to write back incompatible “current reality.” In practice, the last writer wins, earlier updates disappear, and the file still looks authoritative.

3. **Boundary most likely to be collapsed in practice** — The claimed separation between “agent-owned design” and fixed workspace mechanics will erode immediately. The document says each agent should design its own structure within loose invariants (lines 101-118), but then mandates repo-wide frontmatter, generated `index.md`, `CLAUDE.md` always-load blocks, and workspace-level enforcement hooks/wrappers (lines 133-217). Real behavior will converge on “whatever the tooling supports,” so local design freedom is mostly nominal.

Overall verdict: the core instinct is right, but the spec overestimates how much reliability can be delegated to future enforcement and underestimates multi-session contention. As written, it is more likely to produce confidently stale state than genuinely durable context.
tokens used
95,753
1. **Most dangerous assumption** — The design assumes session-start/session-end enforcement will actually exist and be reliable enough to make the ritual load-bearing rather than aspirational (lines 199-217), and further assumes `CLAUDE.md` is a viable universal declaration surface for that enforcement (lines 176-192). If that is wrong, every repo gets the appearance of durable working memory while silently drifting stale, which is worse than having no context repo because agents will trust bad state.

2. **Missing failure mode** — It does not account for concurrent writers. The spec requires every session to read at start and overwrite at end (lines 81-99, 213-217), but says nothing about two sessions reading the same front door and then racing to write back incompatible “current reality.” In practice, the last writer wins, earlier updates disappear, and the file still looks authoritative.

3. **Boundary most likely to be collapsed in practice** — The claimed separation between “agent-owned design” and fixed workspace mechanics will erode immediately. The document says each agent should design its own structure within loose invariants (lines 101-118), but then mandates repo-wide frontmatter, generated `index.md`, `CLAUDE.md` always-load blocks, and workspace-level enforcement hooks/wrappers (lines 133-217). Real behavior will converge on “whatever the tooling supports,” so local design freedom is mostly nominal.

Overall verdict: the core instinct is right, but the spec overestimates how much reliability can be delegated to future enforcement and underestimates multi-session contention. As written, it is more likely to produce confidently stale state than genuinely durable context.
