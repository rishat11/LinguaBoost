"""Best-effort pip install when the host runs from /app/src without installing deps (e.g. some PaaS)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def ensure_runtime_deps() -> None:
    if os.environ.get("LINGUABOOST_SKIP_DEPS_BOOTSTRAP", "").lower() in ("1", "true", "yes"):
        return
    try:
        import fastapi  # noqa: F401
        return
    except ImportError:
        pass

    here = Path(__file__).resolve()
    root: Path | None = None
    for p in (here, *here.parents):
        if (p / "requirements.txt").is_file() and (p / "pyproject.toml").is_file():
            root = p
            break
    if root is None:
        return

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "-r",
            str(root / "requirements.txt"),
        ],
        cwd=root,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            str(root),
            "--no-deps",
        ],
        cwd=root,
        check=True,
    )
