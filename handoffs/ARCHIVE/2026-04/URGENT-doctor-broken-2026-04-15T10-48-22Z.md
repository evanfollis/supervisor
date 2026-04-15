# URGENT: workspace.sh doctor is broken

**Created by**: supervisor tick 2026-04-15T10:48:22Z  
**Priority**: HIGH — every future tick reports a false FAIL

## Problem

`workspace.sh doctor` fails immediately:

```
/opt/workspace/workspace.sh: line 10: /opt/workspace/scripts/lib/workspace-paths.sh: No such file or directory
```

`workspace.sh` computes `LIB_DIR` as `$(dirname "$0")/scripts/lib` = `/opt/workspace/scripts/lib`.  
But `workspace-paths.sh` lives at `/opt/workspace/supervisor/scripts/lib/workspace-paths.sh`.

The file exists; the sourced path is wrong.

## Fix (one line in `workspace.sh`)

Change line 10 from:
```bash
source "$LIB_DIR/workspace-paths.sh"
```
to reference the correct absolute path, e.g.:
```bash
source "$(cd "$(dirname "$0")/supervisor/scripts/lib" && pwd)/workspace-paths.sh"
```
Or update `LIB_DIR` to point to `supervisor/scripts/lib`.

**Note**: `workspace.sh` is Tier C for the unattended tick. Only the attended session may edit it.

## Impact

Until fixed, the tick's health-check step (step 4) always fails with a fatal error. The tick cannot detect genuine system degradation. See FR-0008.
