#!/usr/bin/env python3
"""Private static file server for the synaplex scouting inbox.

Subclass of SimpleHTTPRequestHandler that refuses automatic directory
listings (never leaks the nonce). Serves explicit index.html files inside
the nonce directory but returns 404 for any directory without one.
"""
from __future__ import annotations
import http.server
import os
import sys

ROOT = "/opt/workspace/runtime/inbox"
PORT = 8088
BIND = "127.0.0.1"


class NoListingHandler(http.server.SimpleHTTPRequestHandler):
    def list_directory(self, path):  # noqa: N802
        # Refuse to generate automatic listings. Do not leak dir contents.
        self.send_error(404, "File not found")
        return None

    def log_message(self, format, *args):  # noqa: A002
        # Keep logs short so systemd journal doesn't flood
        sys.stderr.write(f"inbox {self.address_string()} {format % args}\n")


def main() -> int:
    os.chdir(ROOT)
    handler = NoListingHandler
    with http.server.ThreadingHTTPServer((BIND, PORT), handler) as httpd:
        print(f"inbox-server: serving {ROOT} at http://{BIND}:{PORT}", file=sys.stderr)
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
