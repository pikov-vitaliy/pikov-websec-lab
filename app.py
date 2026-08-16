"""Compatibility launcher for the application-factory based backend."""

from __future__ import annotations

import os
import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pikov_websec_lab import create_app  # noqa: E402


def main() -> None:
    app = create_app()
    host = os.environ.get("HOST") or "127.0.0.1"
    port = int(os.environ.get("PORT") or 8080)
    debug = (os.environ.get("DEBUG") or "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
