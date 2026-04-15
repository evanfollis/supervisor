"""
GitHub webhook listener for auto-deploying mentor on push to main.
Listens on port 9000, triggered by GitHub push events.
"""
import hashlib
import hmac
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_SECRET = None  # Set to verify GitHub signatures, or leave None to skip
DEPLOY_COMMANDS = {
    "mentor": [
        "cd /opt/mentor && git pull origin main",
        "cd /opt/mentor && docker compose up --build -d",
    ],
}

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        if WEBHOOK_SECRET:
            sig = self.headers.get("X-Hub-Signature-256", "")
            expected = "sha256=" + hmac.new(
                WEBHOOK_SECRET.encode(), body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig, expected):
                self.send_response(403)
                self.end_headers()
                return

        payload = json.loads(body)
        ref = payload.get("ref", "")
        repo_name = payload.get("repository", {}).get("name", "")

        if ref == "refs/heads/main" and repo_name in DEPLOY_COMMANDS:
            print(f"Deploying {repo_name}...")
            for cmd in DEPLOY_COMMANDS[repo_name]:
                subprocess.run(cmd, shell=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Deployed")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ignored")

    def log_message(self, format, *args):
        print(f"[webhook] {args[0]}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9000), WebhookHandler)
    print("Webhook listener on :9000")
    server.serve_forever()
