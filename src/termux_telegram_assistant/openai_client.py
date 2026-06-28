from __future__ import annotations

from dataclasses import dataclass

from openai import AsyncOpenAI


@dataclass(frozen=True)
class OpenAITextClient:
    api_key: str
    model: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "_client", AsyncOpenAI(api_key=self.api_key))

    async def respond(self, instructions: str, user_input: str) -> str:
        response = await self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_input,
        )
        return response.output_text
