#!/usr/bin/env python3
"""Render markdown files under /opt/workspace/runtime/research/ to HTML for
the private inbox surface. Called by the systemd unit on demand.

Usage: inbox-render.py [--once]
    Renders every .md under RESEARCH_ROOT into a sibling .html. Writes an
    index.html at the inbox nonce root linking every rendered doc.

This is tonight's stopgap while command.synaplex.ai grows a proper /artifacts
route. Do not treat as architecture.
"""
from __future__ import annotations
import os
import sys
import html
from pathlib import Path
from markdown_it import MarkdownIt

RESEARCH_ROOT = Path("/opt/workspace/runtime/research")
INBOX_ROOT = Path("/opt/workspace/runtime/inbox")

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
       max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.55;
       color: #222; background: #fafafa; }
h1, h2, h3, h4 { line-height: 1.25; }
h1 { border-bottom: 2px solid #ccc; padding-bottom: .3em; }
h2 { border-bottom: 1px solid #ddd; padding-bottom: .2em; margin-top: 2.4em; }
h3 { margin-top: 2em; }
code { background: #eee; padding: .1em .3em; border-radius: 3px; font-size: 90%; }
pre { background: #f0f0f0; padding: 1em; overflow-x: auto; border-radius: 4px; }
pre code { background: none; padding: 0; }
a { color: #0550ae; }
blockquote { border-left: 4px solid #ccc; margin: 0; padding: 0 1em; color: #555; }
table { border-collapse: collapse; }
table td, table th { border: 1px solid #ccc; padding: .4em .8em; }
hr { border: 0; border-top: 1px solid #ddd; margin: 2em 0; }
.meta { color: #888; font-size: .9em; margin-bottom: 2em; }
"""

TEMPLATE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head><body>
<div class="meta">synaplex scouting inbox · private nonce path · noindex</div>
{body}
</body></html>
"""


def md_to_html_body(md_text: str) -> str:
    md = MarkdownIt("gfm-like", {"html": False, "linkify": False, "typographer": True})
    return md.render(md_text)


def derive_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines()[:50]:
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped.startswith("title:"):
            return stripped.split(":", 1)[1].strip()
    return fallback


def render_file(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    title = derive_title(text, md_path.stem)
    body = md_to_html_body(text)
    html_path = md_path.with_suffix(".html")
    html_path.write_text(
        TEMPLATE.format(title=html.escape(title), css=CSS, body=body),
        encoding="utf-8",
    )
    return html_path


def find_nonce_dir() -> Path | None:
    nonce_file = INBOX_ROOT / ".current-nonce"
    if not nonce_file.exists():
        return None
    nonce = nonce_file.read_text().strip()
    candidate = INBOX_ROOT / "_inbox" / nonce
    return candidate if candidate.is_dir() else None


def write_index(nonce_dir: Path, rendered: list[Path]) -> None:
    links = []
    for html_path in sorted(rendered):
        # HTML files live under RESEARCH_ROOT; the nonce dir has a 'research' symlink to it.
        rel = Path("research") / html_path.relative_to(RESEARCH_ROOT)
        md_rel = rel.with_suffix(".md")
        title = derive_title(html_path.with_suffix(".md").read_text(encoding="utf-8"), html_path.stem)
        links.append(f'<li><a href="{rel}">{html.escape(title)}</a> · <a href="{md_rel}" style="color:#888">md</a></li>')
    body = (
        "<h1>synaplex scouting inbox</h1>"
        '<p class="meta">Private inbox. Rendered HTML + raw markdown for each artifact. '
        "Regenerate with <code>systemctl restart inbox-render</code> or the render script directly.</p>"
        "<ul>" + "\n".join(links) + "</ul>"
    )
    (nonce_dir / "index.html").write_text(
        TEMPLATE.format(title="synaplex scouting inbox", css=CSS, body=body),
        encoding="utf-8",
    )


def main() -> int:
    nonce_dir = find_nonce_dir()
    if not nonce_dir:
        print(f"inbox-render: no nonce directory at {INBOX_ROOT}/.current-nonce", file=sys.stderr)
        return 1
    rendered: list[Path] = []
    for md_path in RESEARCH_ROOT.rglob("*.md"):
        html_path = render_file(md_path)
        rendered.append(html_path)
        print(f"rendered {md_path} -> {html_path}")
    write_index(nonce_dir, rendered)
    print(f"inbox ready at {nonce_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
