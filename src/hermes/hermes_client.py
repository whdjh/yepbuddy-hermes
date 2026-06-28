from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from hermes.hermes import HermesTokens


def _post_json(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "accept": "application/json",
            **headers,
        },
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Hermes API 응답이 JSON 객체가 아닙니다.")
    return data


def _post_form(url: str, body: dict[str, str]) -> dict[str, Any]:
    request = Request(
        url,
        data=urlencode(body).encode("utf-8"),
        headers={
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Hermes OAuth 응답이 JSON 객체가 아닙니다.")
    return data


@dataclass(frozen=True)
class HermesOAuthClient:
    token_url: str
    client_id: str
    client_secret: str | None
    redirect_uri: str

    async def exchange_code(self, code: str) -> HermesTokens:
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        if self.client_secret:
            body["client_secret"] = self.client_secret

        data = await asyncio.to_thread(_post_form, self.token_url, body)
        access_token = data.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise RuntimeError("Hermes OAuth 응답에 access_token이 없습니다.")

        refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in")
        token_type = data.get("token_type") or "Bearer"
        return HermesTokens(
            access_token=access_token,
            refresh_token=refresh_token if isinstance(refresh_token, str) else None,
            expires_in=expires_in if isinstance(expires_in, int) else None,
            token_type=str(token_type),
        )


@dataclass(frozen=True)
class HermesBrainClient:
    api_base_url: str
    chat_path: str
    model: str
    tokens: HermesTokens

    async def ask(self, prompt: str) -> str:
        url = self.api_base_url.rstrip("/") + "/" + self.chat_path.lstrip("/")
        data = await asyncio.to_thread(
            _post_json,
            url,
            {"authorization": f"{self.tokens.token_type} {self.tokens.access_token}"},
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        return _extract_text(data)


def _extract_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    text = data.get("text")
    if isinstance(text, str) and text:
        return text

    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content:
                    return content
            content = first.get("text")
            if isinstance(content, str) and content:
                return content

    raise RuntimeError("Hermes API 응답에서 텍스트를 찾지 못했습니다.")
