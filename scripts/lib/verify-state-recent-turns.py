#!/usr/bin/env python3
"""Emit the 'Recent principal statements' section of verified-state.md.

Split from verify-state.sh to avoid heredoc/backtick-escaping bugs.
"""
import json
import os
from datetime import datetime, timedelta, timezone

CUTOFF = datetime.now(timezone.utc) - timedelta(hours=48)
BASE = '/root/.claude/projects/-opt-workspace'

SKIP_PREFIXES = (
    'Tick observation',
    'Workspace synthesis',
    'You are the workspace',
    'You are the principal-facing',
    'This session is being continued',
    '# Tick',
    '# Workspace',
    '<command-name>',
    '<system-reminder>',
)


def main():
    msgs = []
    if not os.path.isdir(BASE):
        print("_(JSONL directory unavailable)_")
        return

    for fn in sorted(os.listdir(BASE)):
        if not fn.endswith('.jsonl'):
            continue
        try:
            fh = open(f'{BASE}/{fn}', errors='replace')
        except OSError:
            continue
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('type') != 'user':
                continue
            m = d.get('message', {})
            if not isinstance(m, dict):
                continue
            c = m.get('content')
            if isinstance(c, list):
                c = ' '.join(b.get('text', '') for b in c if isinstance(b, dict))
            if not isinstance(c, str) or not c.strip():
                continue
            stripped = c.strip()
            if any(stripped.startswith(p) for p in SKIP_PREFIXES):
                continue
            if stripped.lower().startswith('respond with exactly'):
                continue
            if 'tool_use' in stripped[:40]:
                continue
            ts = d.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if dt < CUTOFF:
                    continue
            except Exception:
                continue
            msgs.append((ts, stripped.replace('\n', ' ')[:160]))

    if not msgs:
        print("_(no principal turns in last 48h)_")
        return

    for ts, text in sorted(msgs)[-20:]:
        print(f"- `{ts[:19]}Z` — {text}")


if __name__ == '__main__':
    main()
