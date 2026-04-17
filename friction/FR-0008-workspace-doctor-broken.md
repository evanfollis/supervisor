---
type: friction
id: FR-0008
slug: workspace-doctor-broken
date: 2026-04-15
severity: high
status: resolved
---

# FR-0008: workspace.sh doctor fails — workspace-paths.sh path mismatch

## What happened

Running `workspace.sh doctor` during the 2026-04-15T10:48 supervisor tick produced an immediate fatal error:

```
/opt/workspace/workspace.sh: line 10: /opt/workspace/scripts/lib/workspace-paths.sh: No such file or directory
```

`workspace.sh` constructs `LIB_DIR` as `$(dirname "$0")/scripts/lib` = `/opt/workspace/scripts/lib`. But `workspace-paths.sh` lives at `/opt/workspace/supervisor/scripts/lib/workspace-paths.sh`. The file exists; the path in `workspace.sh` is wrong.

## Why it matters

`workspace.sh doctor` is the canonical health-check entrypoint for the supervisor tick (ADR-0014 step 4). A broken doctor means every tick reports a false FAIL and cannot surface genuine system degradation. The tick cannot distinguish "doctor is broken" from "workspace is degraded" — both look the same.

This also means the doctor has been broken since at least the topology migration that moved files to `/opt/workspace/supervisor/scripts/lib/`, and no tick has caught it because the tick itself was only recently deployed (ADR-0014, 2026-04-15T03:55).

## Rule signal

`workspace.sh` is Tier C (forbidden to the unattended tick) but is workspace infrastructure that the attended supervisor session may edit. The attended session should update line 10 of `workspace.sh` to use the correct path. The fix is one line.

**Why:** The supervised tick relies on doctor for health signal. A consistently broken doctor makes the tick's health-check step meaningless.
