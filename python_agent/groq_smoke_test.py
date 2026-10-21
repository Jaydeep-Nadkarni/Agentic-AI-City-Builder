"""Send one safe, short request to Groq using environment-based credentials."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from llm_client import GroqClient, GroqClientError


def load_project_env() -> None:
    """Load simple KEY=VALUE entries from the local config/.env file."""
    env_path = Path(__file__).resolve().parents[1] / "config" / ".env"
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name or name in os.environ:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[name] = value


def main() -> int:
    load_project_env()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(
            "GROQ_API_KEY is not set. Set it in the current terminal session "
            "and run this script again.",
            file=sys.stderr,
        )
        return 2

    try:
        response = GroqClient(api_key).complete(
            "Reply with exactly: Groq smoke test passed."
        )
    except GroqClientError as exc:
        print(f"Groq smoke test failed: {exc}", file=sys.stderr)
        return 1

    print("Groq smoke test response:")
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
