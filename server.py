"""Zero-framework local server with live research for any available NSE ticker."""
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

from refresh import research

ROOT = Path(__file__).parent / "dist"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/research":
            return super().do_GET()
        symbol = parse_qs(parsed.query).get("symbol", [""])[0].upper().strip()
        if not re.fullmatch(r"[A-Z0-9&-]{1,20}", symbol):
            return self.send_json({"error": "Enter a valid NSE ticker."}, 400)
        try:
            result = research(requests.Session(), symbol)
            return self.send_json(result)
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            return self.send_json({"error": str(exc)}, 502)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("FINN at http://localhost:8008")
    ThreadingHTTPServer(("127.0.0.1", 8008), Handler).serve_forever()
