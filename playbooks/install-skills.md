# Playbook: Install a supervisor skill into Claude and Codex

**Trigger**: a new skill has been added under `/opt/workspace/supervisor/skills/<name>/`
and needs to be discoverable by the running agents.

**Owner**: supervisor

**Preconditions**:
- Skill directory exists at `/opt/workspace/supervisor/skills/<name>/`
- Skill has a valid `SKILL.md` with frontmatter (see `skills/README.md`)
- `~/.claude/skills/` and `~/.codex/skills/` directories exist (create if not)

**Outputs**:
- Symlink `~/.claude/skills/<name>` → `/opt/workspace/supervisor/skills/<name>`
- Symlink `~/.codex/skills/<name>` → `/opt/workspace/supervisor/skills/<name>`

## Steps

1. **Confirm the skill directory is well-formed.**
   ```
   ls /opt/workspace/supervisor/skills/<name>/SKILL.md
   head -10 /opt/workspace/supervisor/skills/<name>/SKILL.md
   ```
   **Verify**: `SKILL.md` exists and has `name:`, `description:`, `applies_to:`
   frontmatter.

2. **Ensure agent skill dirs exist.**
   ```
   mkdir -p ~/.claude/skills ~/.codex/skills
   ```
   **Verify**: both directories listable.

3. **Install the symlinks.**
   ```
   ln -sfn /opt/workspace/supervisor/skills/<name> ~/.claude/skills/<name>
   ln -sfn /opt/workspace/supervisor/skills/<name> ~/.codex/skills/<name>
   ```
   `-n` prevents re-linking inside an existing target if one already exists.

   **Verify**: `readlink ~/.claude/skills/<name>` and
   `readlink ~/.codex/skills/<name>` both resolve to the supervisor path.

4. **Smoke-test discovery.**
   - Claude: run a session in any project and type `/skills` — the new skill
     should appear.
   - Codex: run `codex --list-skills` (or the equivalent for current Codex
     version) from the project dir.

   **Verify**: skill appears in both agents' lists.

## Rollback / uninstall

```
rm ~/.claude/skills/<name> ~/.codex/skills/<name>
```

Both are symlinks — removing them does not affect the skill source.

## Notes

- Skills are repo-tracked; symlinks are per-host. Provisioning a new machine
  requires rerunning this playbook for each skill.
- If Claude or Codex changes its skill-discovery path, update `skills/README.md`
  and this playbook rather than duplicating skills under new paths.
