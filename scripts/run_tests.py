from __future__ import annotations

import subprocess
import sys
from shutil import which
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PYTEST_TARGETS = [
    ("contracts", REPO_ROOT, ["tests"]),
    ("auth-service", REPO_ROOT / "services" / "auth-service", ["tests"]),
    ("classifier-service", REPO_ROOT / "services" / "classifier-service", ["tests"]),
    ("urgency-service", REPO_ROOT / "services" / "urgency-service", ["tests"]),
    ("rag-service", REPO_ROOT / "services" / "rag-service", ["tests"]),
    ("llm-service", REPO_ROOT / "services" / "llm-service", ["tests"]),
    ("api-gateway", REPO_ROOT / "services" / "api-gateway", ["tests"]),
    ("worker-service", REPO_ROOT / "services" / "worker-service", ["tests"]),
]

COMMAND_TARGETS = [
    ("frontend-lint", REPO_ROOT / "frontend-app", ["npm", "run", "lint"]),
    ("frontend-unit", REPO_ROOT / "frontend-app", ["npm", "run", "test"]),
    ("frontend-e2e", REPO_ROOT / "frontend-app", ["npm", "run", "test:e2e"]),
    ("frontend-build", REPO_ROOT / "frontend-app", ["npm", "run", "build"]),
]


def run_target(name: str, cwd: Path, args: list[str]) -> int:
    command = [sys.executable, "-m", "pytest", *args, "-q"]
    print(f"\n== {name}: {' '.join(command)} ==")
    completed = subprocess.run(command, cwd=str(cwd), check=False)
    return completed.returncode


def run_command_target(name: str, cwd: Path, command: Sequence[str]) -> int:
    resolved = list(command)
    executable = which(resolved[0])
    if executable:
        resolved[0] = executable
    print(f"\n== {name}: {' '.join(command)} ==")
    completed = subprocess.run(resolved, cwd=str(cwd), check=False)
    return completed.returncode


def main() -> int:
    failures: list[str] = []
    for name, cwd, args in PYTEST_TARGETS:
        if run_target(name, cwd, args) != 0:
            failures.append(name)
    for name, cwd, command in COMMAND_TARGETS:
        if not cwd.exists():
            print(f"\nSKIPPED {name}: {cwd} does not exist.")
            continue
        if run_command_target(name, cwd, command) != 0:
            failures.append(name)
    if failures:
        print(f"\nFAILED test targets: {', '.join(failures)}")
        return 1
    print("\nAll isolated LocalBank test targets passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
