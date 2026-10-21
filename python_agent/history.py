"""JSONL history store with an in-memory fallback."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class History:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path) if path else None
        self.entries: list[dict[str, Any]] = []
    def append(self, event: dict[str, Any]) -> None:
        self.entries.append(dict(event))
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.entries[-limit:]

