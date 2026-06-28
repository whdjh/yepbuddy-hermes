from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonlStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def append(self, name: str, record: dict[str, Any]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        path = self.data_dir / f"{name}.jsonl"
        enriched = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        with path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(enriched, ensure_ascii=False, separators=(",", ":")) + "\n")


class JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        if not isinstance(data, dict):
            raise ValueError(f"{self.path}에는 JSON 객체가 들어 있어야 합니다.")
        return data
