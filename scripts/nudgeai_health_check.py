"""NudgeAI local hardening health check.

This script is intentionally conservative: it performs static repo checks and
best-effort local runtime checks without exposing private Calendar, Drive,
location, health, or token contents.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BACKEND_HEALTH_URL = "http://localhost:8001/health"
REQUIRED_FILES = [
    "simple_api_server.py",
    "frontend/package.json",
    "frontend/vite.config.js",
    ".env.example",
    ".gitignore",
    "scripts/privacy_check.py",
    "docs/LOCAL_INTEGRATION_RUNBOOK.md",
    "docs/NUDGEAI_HERMES_INTEGRATION_PLAN.md",
]
PRIVATE_PATTERNS = [
    ".env",
    "api/env.local",
    "token.json",
    "drive_token.json",
    "calendar_events.json",
    "drive_documents.json",
    "drive_documents_rag.json",
    "data_sync/calendar_sync.json",
    "data_sync/drive_sync.json",
    "data_sync/sync_summary.json",
]


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def check_required_files(errors: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).exists():
            errors.append(f"missing required file: {rel_path}")


def check_vite_proxy(errors: list[str]) -> None:
    config = ROOT / "frontend" / "vite.config.js"
    if not config.exists():
        return
    text = config.read_text(encoding="utf-8", errors="replace")
    if "http://localhost:8001" not in text:
        errors.append("frontend/vite.config.js does not proxy /api to http://localhost:8001")


def check_privacy_guard(errors: list[str], warnings: list[str]) -> None:
    result = run([sys.executable, "scripts/privacy_check.py"])
    if result.returncode != 0:
        errors.append("scripts/privacy_check.py failed")
        if result.stdout.strip():
            warnings.append(result.stdout.strip())
        if result.stderr.strip():
            warnings.append(result.stderr.strip())
    elif result.stdout.strip():
        warnings.append(result.stdout.strip())


def check_git_tracking(errors: list[str]) -> None:
    result = run(["git", "ls-files", *PRIVATE_PATTERNS])
    if result.returncode != 0:
        errors.append("git ls-files failed while checking private artifacts")
        return
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    if tracked:
        errors.append("private artifacts are tracked by git: " + ", ".join(tracked))


def check_backend_health(warnings: list[str]) -> None:
    try:
        with urlopen(BACKEND_HEALTH_URL, timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("status") != "healthy":
            warnings.append(f"backend responded but status is not healthy: {payload}")
    except (OSError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        warnings.append(
            "backend health endpoint unavailable; start with "
            "`python simple_api_server.py` when runtime checks are needed "
            f"({exc.__class__.__name__})"
        )


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    check_required_files(errors)
    check_vite_proxy(errors)
    check_privacy_guard(errors, warnings)
    check_git_tracking(errors)
    check_backend_health(warnings)

    report = {
        "status": "failed" if errors else "passed",
        "repo": str(ROOT),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
