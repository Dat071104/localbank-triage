from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PolicyDocument:
    path: Path
    metadata: dict[str, object]
    body: str


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise ValueError("Policy file must start with YAML frontmatter")

    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("Policy file must contain closing frontmatter delimiter")

    raw_frontmatter = parts[1].strip()
    body = parts[2].strip()
    metadata: dict[str, object] = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip():
            continue
        key, _, raw_value = line.partition(":")
        if not key or not _:
            raise ValueError(f"Invalid frontmatter line: {line}")
        value = raw_value.strip()
        if value.startswith("["):
            metadata[key.strip()] = json.loads(value)
        elif value.startswith('"') and value.endswith('"'):
            metadata[key.strip()] = value[1:-1]
        else:
            metadata[key.strip()] = value
    return metadata, body


def load_policy(path: Path) -> PolicyDocument:
    metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return PolicyDocument(path=path, metadata=metadata, body=body)


def load_policies(root: Path) -> list[PolicyDocument]:
    return [load_policy(path) for path in sorted(root.rglob("*.md"))]
