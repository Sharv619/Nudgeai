"""Check that private local NudgeAI artifacts are not tracked by git."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


FORBIDDEN_TRACKED = [
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


def run_git_ls_files(paths: list[str]) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("ERROR: failed to run git ls-files.", file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        return set(paths)
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    tracked = run_git_ls_files(FORBIDDEN_TRACKED)
    existing = [path for path in FORBIDDEN_TRACKED if Path(path).exists()]

    if existing:
        print("Warning: private local artifacts exist on disk:")
        for path in existing:
            status = "TRACKED" if path in tracked else "ignored/untracked"
            print(f"  - {path} ({status})")

    if tracked:
        print("ERROR: forbidden private artifacts are tracked by git:")
        for path in sorted(tracked):
            print(f"  - {path}")
        print()
        print("Remove tracked copies without deleting local files, for example:")
        print("  git rm --cached <path>")
        print("Rotate credentials if secrets or OAuth tokens were ever committed.")
        return 1

    print("Privacy check passed: no forbidden private artifacts are tracked by git.")
    if existing:
        print("Local private artifacts may remain on disk if ignored and kept out of commits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
