from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Dict

from common.config import Settings
from common.llm_client import LLMClient


@dataclass
class ClassificationResult:
    label: str
    explanation: str
    confidence: float


class PhishingClassifier:
    """Minimal blue-agent classifier built on top of the shared LLM client."""

    def __init__(self, settings: Settings) -> None:
        self.client = LLMClient(settings)
        self.system_prompt = (
            "You are a cyber defense assistant. Given an email, decide if it is "
            "phishing or benign and explain the decision in 2 bullet points."
        )

    def classify(self, email_body: str) -> ClassificationResult:
        user_prompt = (
            "Email:\n"
            f"{email_body}\n\n"
            "Respond with JSON like "
            '{"label": "phishing|benign", "confidence": 0-1, "explanation": "..."}'
        )
        raw_response = self.client.complete(self.system_prompt, user_prompt)
        cleaned = self._strip_code_fence(raw_response)
        try:
            parsed: Dict = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"LLM returned invalid JSON: {raw_response}") from exc
        return ClassificationResult(
            label=parsed.get("label", "unknown"),
            explanation=parsed.get("explanation", ""),
            confidence=float(parsed.get("confidence", 0.0)),
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
