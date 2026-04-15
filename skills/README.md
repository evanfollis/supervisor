# Skills

Shared capabilities for the supervisor agent. Written agent-agnostically so
both Claude Code and Codex can consume them.

## Structure

One directory per skill:

```
skills/
  <skill-name>/
    SKILL.md        — when to use, what it does, invocation
    <scripts/>      — any shell/python helpers the skill relies on
    <templates/>    — prompt templates, file templates
```

## SKILL.md format

```
---
name: <skill-name>
description: <one-sentence description used for skill discovery>
applies_to: supervisor   # or: project-pm, any-agent
---

# <Skill name>

## When to use
<concrete trigger conditions>

## What it does
<the mechanism — what files it reads, what it produces>

## Invocation
<exact command(s) or prompt fragment(s)>

## Agent notes
- Claude Code: <anything harness-specific>
- Codex: <anything harness-specific>
```

## Registration

Claude and Codex each look for skills in their own directories
(`~/.claude/skills/` and `~/.codex/skills/`). To register a skill from this
repo into both, symlink it:

```
ln -sf /opt/workspace/supervisor/skills/<name> ~/.claude/skills/<name>
ln -sf /opt/workspace/supervisor/skills/<name> ~/.codex/skills/<name>
```

See `playbooks/install-skills.md` for the full procedure once written.

## Don't put project-specific skills here

Skills that only make sense for one project (atlas evidence ingest, skillfoundry
hypothesis scoring, etc.) belong in that project's own repo, not here. This
directory is for skills the supervisor or a project-PM agent would use —
cross-cutting, orchestration-level capabilities.
