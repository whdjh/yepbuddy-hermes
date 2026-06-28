from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HarnessContext:
    user_id: int | None
    chat_id: int | None
    message_thread_id: int | None


class TextClient(Protocol):
    async def respond(self, instructions: str, user_input: str) -> str:
        ...


def ping_text(context: HarnessContext) -> str:
    return (
        "안드로이드 서버 Telegram OpenAI 하네스가 연결되어 있습니다.\n"
        f"user_id: {context.user_id}\n"
        f"chat_id: {context.chat_id}\n"
        f"message_thread_id: {context.message_thread_id}"
    )


def whoami_text(context: HarnessContext) -> str:
    return (
        f"user_id: {context.user_id}\n"
        f"chat_id: {context.chat_id}\n"
        f"message_thread_id: {context.message_thread_id}"
    )


async def ai_text(client: TextClient | None, prompt: str) -> str:
    prompt = prompt.strip()
    if not prompt:
        return "/ai 뒤에 OpenAI로 보낼 문장을 붙여 주세요. 예: /ai 한 문장으로 연결 확인해줘"
    if client is None:
        return "OPENAI_API_KEY가 설정되지 않았습니다. 안드로이드 서버 Termux의 .env를 확인하세요."

    return await client.respond(
        instructions=(
            "너는 안드로이드 서버 Termux에서 실행 중인 Telegram OpenAI 연결 확인 하네스다. "
            "사용자 요청에 짧고 명확하게 답하고, 연결 확인 목적을 벗어난 긴 작업은 하지 않는다."
        ),
        user_input=prompt,
    )
