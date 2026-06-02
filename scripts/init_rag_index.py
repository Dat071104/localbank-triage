from __future__ import annotations

import argparse
import json
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description="Index LocalBank policy KB through the RAG service")
    parser.add_argument("--url", default="http://127.0.0.1:8003", help="RAG service base URL")
    args = parser.parse_args()
    request = urllib.request.Request(f"{args.url.rstrip('/')}/rag/index", method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
