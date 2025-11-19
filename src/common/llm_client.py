from __future__ import annotations

from typing import List

from openai import OpenAI

from .config import Settings


class LLMClient:
    """Thin wrapper around the OpenAI client (or compatible API)."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_output_tokens: int = 700,
    ) -> str:
        """Send a chat completion request and return the text content."""

        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.chat.completions.create(
            model=self.settings.model,
            max_completion_tokens=max_output_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        choices: List = response.choices
        if not choices:
            raise RuntimeError("LLM returned no choices")
        return choices[0].message.content or ""
