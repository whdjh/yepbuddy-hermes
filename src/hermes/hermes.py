from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlencode


@dataclass(frozen=True)
class HermesContext:
    user_id: int | None
    chat_id: int | None
    message_thread_id: int | None


@dataclass(frozen=True)
class BrainTokens:
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None
    token_type: str = "Bearer"


class OpenAIBrain(Protocol):
    async def ask(self, prompt: str) -> str:
        ...


class TokenStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> BrainTokens | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return BrainTokens(
            access_token=str(data["access_token"]),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            token_type=str(data.get("token_type") or "Bearer"),
        )

    def write(self, tokens: BrainTokens) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fp:
            json.dump(asdict(tokens), fp, ensure_ascii=False, indent=2)
            fp.write("\n")


def ping_text(context: HermesContext) -> str:
    return (
        "Hermes가 안드로이드 서버에서 실행 중입니다.\n"
        f"user_id: {context.user_id}\n"
        f"chat_id: {context.chat_id}\n"
        f"message_thread_id: {context.message_thread_id}"
    )


def whoami_text(context: HermesContext) -> str:
    return (
        f"user_id: {context.user_id}\n"
        f"chat_id: {context.chat_id}\n"
        f"message_thread_id: {context.message_thread_id}"
    )


def build_authorization_url(
    *,
    auth_url: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
) -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
        }
    )
    return f"{auth_url}?{query}"


def auth_url_text(*, auth_url: str, client_id: str, redirect_uri: str, scope: str) -> str:
    missing = [
        name
        for name, value in {
            "OPENAI_AUTH_URL": auth_url,
            "OPENAI_CLIENT_ID": client_id,
            "OPENAI_REDIRECT_URI": redirect_uri,
        }.items()
        if not value
    ]
    if missing:
        return "OpenAI OAuth 설정이 비어 있습니다: " + ", ".join(missing)

    url = build_authorization_url(
        auth_url=auth_url,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state="hermes",
    )
    return (
        "아래 URL을 텔레그램용 핸드폰 브라우저에서 여세요.\n"
        f"{url}\n\n"
        "로그인 후 받은 code를 /authcode <code> 형식으로 보내세요."
    )


async def ask_text(brain: OpenAIBrain | None, prompt: str) -> str:
    prompt = prompt.strip()
    if not prompt:
        return "/ask 뒤에 OpenAI에게 보낼 문장을 붙여 주세요. 예: /ask 오늘 할 일을 정리해줘"
    if brain is None:
        return "OpenAI OAuth 토큰이 없습니다. 먼저 /auth 후 /authcode <code>를 완료하세요."
    return await brain.ask(prompt)
