#!/usr/bin/env python3
"""Reduce Apache access logs to the feedback aggregate the dashboard reads.

The feedback widget (transport = "beacon") requests /feedback.gif?r=<rating>
with the page in the Referer header. Apache writes those requests to its
access log like any other; this script turns them into feedback.json:

    python tools/feedback_log.py /var/log/apache2/access.log -o feedback.json

By default it reads exactly the files given and writes a fresh aggregate, so
running it over the same logs twice is idempotent. Pass --merge to add to an
existing --out instead (for feeding only newly rotated logs). Rotated .gz
files are handled. With no file arguments it reads stdin, so it can sit behind
a Jenkins shell step or a pipe.

Referer hosts are an allow-list (default docs.dyalog.com and localhost): a
request whose Referer is present but foreign is treated as bot/spam and
dropped. A request with no Referer falls back to the page in the `p` query
parameter. IP addresses are ignored; only page, rating and time are kept.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

DEFAULT_HOSTS = ("docs.dyalog.com", "localhost")
DEFAULT_OUT = Path("feedback.json")

QUOTED = re.compile(r'"([^"]*)"')
VERSION_PREFIX = re.compile(r"^/\d+\.\d+/")


def normalize_page(path: str) -> str:
    """Canonical page path: leading slash, version prefix stripped."""
    if not path.startswith("/"):
        path = "/" + path
    return VERSION_PREFIX.sub("/", path)


def parse_line(line: str, hosts: set[str]) -> tuple[str, str] | None:
    """Return (page, rating) for a feedback.gif request, or None."""
    if "feedback.gif" not in line:
        return None
    quoted = QUOTED.findall(line)
    target = None
    for token in quoted:
        if "feedback.gif" in token:
            parts = token.split()
            if len(parts) >= 2:
                target = parts[1]
            break
    if target is None:
        return None
    query = parse_qs(urlsplit(target).query)
    rating = (query.get("r") or [""])[0]
    referer = next((t for t in quoted if t.startswith("http")), "")
    page = ""
    if referer:
        ref = urlsplit(referer)
        if hosts and ref.hostname not in hosts:
            return None
        page = ref.path
    if not page:
        page = (query.get("p") or [""])[0]
        if not page:
            return None
    if not rating:
        return None
    return normalize_page(page), rating


def _open(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open(encoding="utf-8", errors="replace")


def load_aggregate(path: Path) -> dict[str, dict[str, int]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            page: {str(r): int(n) for r, n in votes.items()}
            for page, votes in data.get("pages", {}).items()
        }
    except (json.JSONDecodeError, ValueError, AttributeError):
        return {}


def write_aggregate(
    path: Path, pages: dict[str, dict[str, int]], sources: list[str]
) -> int:
    total = sum(n for votes in pages.values() for n in votes.values())
    ordered = {page: dict(sorted(votes.items())) for page, votes in sorted(pages.items())}
    data = {
        "total": total,
        "pages": ordered,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "sources": sources,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return total


def _lines(paths: list[Path]):
    if not paths:
        yield from sys.stdin
        return
    for path in paths:
        with _open(path) as fh:
            yield from fh


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="*", type=Path, help="access logs (default: stdin)")
    parser.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--host",
        action="append",
        default=[],
        metavar="HOST",
        help="allowed Referer host, repeatable (default: docs.dyalog.com, localhost)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="add to an existing --out instead of replacing it",
    )
    args = parser.parse_args()

    hosts = set(args.host) or set(DEFAULT_HOSTS)
    pages = load_aggregate(args.out) if args.merge else {}
    reading = [str(p) for p in args.logs] or ["<stdin>"]
    matched = 0
    total_lines = 0
    for line in _lines(args.logs):
        total_lines += 1
        result = parse_line(line, hosts)
        if result is None:
            continue
        page, rating = result
        votes = pages.setdefault(page, {})
        votes[rating] = votes.get(rating, 0) + 1
        matched += 1

    total = write_aggregate(args.out, pages, reading)
    print(
        f"{matched} feedback request(s) in {total_lines} line(s) "
        f"from {', '.join(reading)} -> {args.out} (total {total})",
        flush=True,
    )


if __name__ == "__main__":
    main()
