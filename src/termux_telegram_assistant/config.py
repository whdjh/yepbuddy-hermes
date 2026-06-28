from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _parse_user_ids(raw: str | None) -> frozenset[int]:
    if not raw:
        return frozenset()

    user_ids: set[int] = set()
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        try:
            user_ids.add(int(value))
        except ValueError as exc:
            raise ValueError(f"ALLOWED_USER_IDS에 숫자가 아닌 값이 있습니다: {value}") from exc
    return frozenset(user_ids)


def _path_from_env(name: str, default: str) -> Path:
    raw = os.getenv(name, default)
    path = Path(raw).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str | None
    openai_model: str
    allowed_user_ids: frozenset[int]
    topic_routes_path: Path
    data_dir: Path
    log_level: str
    reply_max_chars: int

    @property
    def has_allowed_users(self) -> bool:
        return bool(self.allowed_user_ids)


def load_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 필요합니다. .env.example을 .env로 복사한 뒤 로컬에서 값을 채우십시오.")

    try:
        reply_max_chars = int(os.getenv("REPLY_MAX_CHARS", "3500"))
    except ValueError as exc:
        raise ValueError("REPLY_MAX_CHARS는 정수여야 합니다.") from exc

    return Settings(
        telegram_bot_token=token,
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5").strip(),
        allowed_user_ids=_parse_user_ids(os.getenv("ALLOWED_USER_IDS")),
        topic_routes_path=_path_from_env("TOPIC_ROUTES_PATH", "config/topic_routes.json"),
        data_dir=_path_from_env("DATA_DIR", "data"),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        reply_max_chars=reply_max_chars,
    )
