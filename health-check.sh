#!/usr/bin/env bash
# Legacy entrypoint kept for compatibility. Delegates to the richer snapshot job,
# which also refreshes /opt/workspace/runtime/.health-status.txt for the dashboard.

set -euo pipefail

/opt/workspace/supervisor/scripts/lib/server-health-snapshot.sh >/dev/null
