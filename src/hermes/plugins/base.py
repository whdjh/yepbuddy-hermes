from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from hermes.storage import JsonlStore


@dataclass(frozen=True)
class RoleRequest:
    role: str
    chat_id: int
    message_thread_id: int | None
    user_id: int
    text: str
    message_id: int


@dataclass(frozen=True)
class RoleResponse:
    text: str


class RolePlugin(Protocol):
    name: str

    async def handle(self, request: RoleRequest, store: JsonlStore) -> RoleResponse:
        ...
