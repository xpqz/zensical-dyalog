#!/usr/bin/env python3
"""Local stub collector for the documentation feedback widget.

Demo only. Receives the POSTs that the custom analytics partial sends when
transport = "collector", appends them to a JSONL file and serves the shared
dashboard. To exercise the widget end to end:

    python tools/feedback_stub.py
    open http://localhost:8765/          # live dashboard, refreshes every 5s
    curl http://localhost:8765/summary   # raw JSON

and set [project.extra.analytics] transport = "collector" with property
pointing at http://127.0.0.1:8765/feedback. Production uses the access-log
path (transport = "beacon", tools/feedback_log.py) and no server at all;
this stub exists so the widget and dashboard can be demonstrated live.
"""

from __future__ import annotations

import argparse
import json
import socket
import threading
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

DEFAULT_OUT = Path(__file__).with_name("feedback.local.jsonl")
DASHBOARD_PATH = Path(__file__).with_name("feedback_dashboard.html")


class Handler(BaseHTTPRequestHandler):
    out: Path
    counts: Counter

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _end(self, status: int, body: bytes = b"", ctype: str = "text/plain") -> None:
        self.send_response(status)
        self._cors()
        if body:
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._end(204)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace")
        fields = {k: v[0] for k, v in parse_qs(raw).items()}
        record = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "path": self.path,
            "page": fields.get("page", ""),
            "rating": fields.get("rating", ""),
            "referer": self.headers.get("Referer", ""),
        }
        with self.out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        self.counts[(record["page"], record["rating"])] += 1
        print(f"{record['rating']:>2}  {record['page']}", flush=True)
        self._end(204)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path in ("/", "/dashboard"):
            body = DASHBOARD_PATH.read_bytes()
            self._end(200, body, "text/html; charset=utf-8")
            return
        if path != "/summary":
            self._end(404, b"not found")
            return
        pages: dict[str, dict[str, int]] = {}
        for (page, rating), n in sorted(self.counts.items()):
            pages.setdefault(page, {})[rating] = n
        body = json.dumps(
            {"total": sum(self.counts.values()), "pages": pages}, indent=2
        ).encode()
        self._end(200, body, "application/json")

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass  # quiet the default access log


def _make_server(
    host: str, port: int, handler: type[BaseHTTPRequestHandler]
) -> ThreadingHTTPServer:
    if ":" in host:

        class V6Server(ThreadingHTTPServer):
            address_family = socket.AF_INET6

        return V6Server((host, port), handler)
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    Handler.out = args.out
    Handler.counts = Counter()
    if args.out.exists():
        for line in args.out.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            Handler.counts[(rec.get("page", ""), rec.get("rating", ""))] += 1

    # A bare "localhost" resolves to both 127.0.0.1 and ::1, and a browser may
    # pick either. A beacon is fire-and-forget, so a refused connection is
    # silent -- bind both loopbacks rather than rely on the browser's fallback.
    hosts = ["127.0.0.1", "::1"] if args.host == "localhost" else [args.host]
    servers = []
    for host in hosts:
        try:
            servers.append(_make_server(host, args.port, Handler))
        except OSError as exc:
            print(f"could not bind {host}:{args.port}: {exc}", flush=True)
    if not servers:
        raise SystemExit("no listener could be started")

    for server in servers:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    where = ", ".join(
        f"http://{'[' + h + ']' if ':' in h else h}:{args.port}/" for h in hosts
    )
    print(f"feedback stub on {where} -> {args.out}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
