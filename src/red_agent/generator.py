from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Dict

from common.config import Settings
from common.llm_client import LLMClient
from common.profile import Profile
from .scenarios import Scenario


@dataclass
class PhishingExample:
    scenario: str
    difficulty: str
    subject: str
    body: str
    summary: str
    red_flags: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class PhishingGenerator:
    """Generate structured phishing emails for training purposes."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = LLMClient(settings)
        self.system_prompt = (
            "You are a cybersecurity training assistant that fabricates phishing "
            "emails for red-team simulations. Always mark clearly that the email is "
            "for training and highlight red flags."
        )

    def generate(
        self, scenario: Scenario, difficulty: str, profile: Profile | None = None
    ) -> PhishingExample:
        profile_block = (
            profile.to_prompt_block()
            if profile
            else "N/A (keep tone neutral and generic)."
        )
        user_prompt = (
            f"Scenario: {scenario.description}\n"
            f"Difficulty: {difficulty}\n"
            "Profile cues (use only as background; do not invent new facts):\n"
            f"{profile_block}\n"
            "Respond ONLY with valid JSON matching this schema:\n"
            '{\"subject\": \"short subject line for the training email\", '
            '"body\": \"[TRAINING SIMULATION - DO NOT FORWARD]\\n...email...\", '
            '"summary\": \"one sentence\", '
            '"red_flags\": "- reason 1\\n- reason 2\"}\n'
            "Do not include any text before or after the JSON. "
            "Body must resemble a realistic phishing email."
        )
        raw_response = self.client.complete(self.system_prompt, user_prompt)
        cleaned = self._strip_code_fence(raw_response)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Generator returned invalid JSON: {raw_response}") from exc

        return PhishingExample(
            scenario=scenario.name,
            difficulty=difficulty,
            subject=parsed.get("subject", "Training simulation"),
            body=parsed.get("body", ""),
            summary=parsed.get("summary", "Automatically generated for training."),
            red_flags=parsed.get("red_flags", "See training email for details."),
        )

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return stripped
