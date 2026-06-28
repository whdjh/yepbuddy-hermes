from __future__ import annotations

from dataclasses import dataclass

from .base import RoleRequest, RoleResponse
from hermes.storage import JsonlStore


@dataclass(frozen=True)
class StubRolePlugin:
    name: str
    purpose: str

    async def handle(self, request: RoleRequest, store: JsonlStore) -> RoleResponse:
        store.append(
            "role_events",
            {
                "role": self.name,
                "chat_id": request.chat_id,
                "message_thread_id": request.message_thread_id,
                "user_id": request.user_id,
                "message_id": request.message_id,
                "text": request.text,
                "mode": "stub",
            },
        )
        return RoleResponse(
            text=(
                f"[{self.name}] stub 응답입니다.\n"
                f"역할: {self.purpose}\n"
                "현재는 입력을 안드로이드 서버 JSONL에 기록하고 같은 topic으로 응답합니다."
            )
        )


def default_plugins() -> dict[str, StubRolePlugin]:
    plugins = [
        StubRolePlugin("app_promo", "아이디어와 배포 메모 정리"),
        StubRolePlugin("health_research", "건강/논문 리서치 메모 정리"),
        StubRolePlugin("ai_research", "Hermes 두뇌 테스트와 리서치 정리"),
        StubRolePlugin("study_summary", "공부 기록과 요약 노트 생성"),
        StubRolePlugin("ops_log", "Hermes 운영 로그와 시스템 상태 기록"),
    ]
    return {plugin.name: plugin for plugin in plugins}
