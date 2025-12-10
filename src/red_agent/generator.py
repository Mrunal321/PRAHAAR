from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict

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
        parsed = self._parse_json_safely(raw_response, scenario, difficulty)

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

    def _parse_json_safely(
        self, raw_response: str, scenario: Scenario, difficulty: str
    ) -> Dict[str, Any]:
        cleaned = self._strip_code_fence(raw_response)
        if cleaned:
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                start = cleaned.find("{")
                end = cleaned.rfind("}")
                if start != -1 and end != -1 and end > start:
                    snippet = cleaned[start : end + 1]
                    try:
                        return json.loads(snippet)
                    except json.JSONDecodeError:
                        pass
        # Fallback: return a safe placeholder so the pipeline does not crash
        return {
            "subject": f"[Training] {scenario.name} ({difficulty})",
            "body": (
                "[TRAINING SIMULATION - DO NOT FORWARD]\n"
                f"This placeholder was used because the LLM response was invalid for scenario "
                f"{scenario.name} at difficulty {difficulty}. Please regenerate."
            ),
            "summary": "Placeholder email due to LLM parse failure.",
            "red_flags": "- Placeholder generated because JSON parsing failed.",
        }
