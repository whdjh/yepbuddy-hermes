from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hermes.plugins import RolePlugin
from hermes.storage import JsonStore


@dataclass(frozen=True)
class Route:
    role: str
    plugin: RolePlugin


class TopicRouter:
    def __init__(
        self,
        plugins: dict[str, RolePlugin],
        routes: dict[int, str] | None = None,
        default_role: str | None = None,
    ) -> None:
        self._plugins = plugins
        self._routes = routes or {}
        self._default_role = default_role

    @classmethod
    def from_file(cls, path: Path, plugins: dict[str, RolePlugin]) -> "TopicRouter":
        data = JsonStore(path).read()
        if data is None:
            return cls(plugins)

        raw_routes = data.get("routes", {})
        if not isinstance(raw_routes, dict):
            raise ValueError(f"{path}의 'routes' 필드는 객체여야 합니다.")

        routes: dict[int, str] = {}
        for raw_thread_id, raw_role in raw_routes.items():
            try:
                thread_id = int(raw_thread_id)
            except ValueError as exc:
                raise ValueError(f"{path}의 route key는 숫자 message_thread_id여야 합니다: {raw_thread_id}") from exc
            if not isinstance(raw_role, str):
                raise ValueError(f"{path}에서 {raw_thread_id}의 route 값은 role 이름이어야 합니다.")
            if raw_role not in plugins:
                raise ValueError(f"{path}에서 알 수 없는 role을 참조합니다: {raw_role}")
            routes[thread_id] = raw_role

        default_role = data.get("default_role")
        if default_role is not None:
            if not isinstance(default_role, str):
                raise ValueError(f"{path}의 'default_role' 필드는 문자열이어야 합니다.")
            if default_role not in plugins:
                raise ValueError(f"{path}의 default_role이 알 수 없는 role을 참조합니다: {default_role}")

        return cls(plugins=plugins, routes=routes, default_role=default_role)

    def resolve(self, message_thread_id: int | None) -> Route | None:
        role = self._routes.get(message_thread_id) if message_thread_id is not None else None
        if role is None:
            role = self._default_role
        if role is None:
            return None
        return Route(role=role, plugin=self._plugins[role])

    def roles(self) -> tuple[str, ...]:
        return tuple(sorted(self._plugins))

    def route_lines(self) -> list[str]:
        lines = [f"{thread_id}: {role}" for thread_id, role in sorted(self._routes.items())]
        if self._default_role:
            lines.append(f"기본값: {self._default_role}")
        return lines
