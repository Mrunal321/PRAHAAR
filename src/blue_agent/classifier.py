from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Dict
from json import JSONDecodeError

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
        parsed = self._parse_json_safely(raw_response)
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

    @staticmethod
    def _parse_json_safely(raw_text: str) -> Dict[str, Any]:
        cleaned = PhishingClassifier._strip_code_fence(raw_text)
        try:
            return json.loads(cleaned)
        except JSONDecodeError:
            sanitized = PhishingClassifier._escape_inline_quotes(cleaned)
            try:
                return json.loads(sanitized)
            except JSONDecodeError:
                start = sanitized.find("{")
                end = sanitized.rfind("}")
                if start != -1 and end != -1 and end > start:
                    snippet = sanitized[start : end + 1]
                    try:
                        return json.loads(snippet)
                    except JSONDecodeError:
                        pass
        # Final fallback: extract what we can to avoid hard failure
        label_match = re.search(r'"label"\\s*:\\s*"([^"]+)"', cleaned)
        conf_match = re.search(r'"confidence"\\s*:\\s*([0-9.]+)', cleaned)
        label = label_match.group(1) if label_match else "unknown"
        try:
            confidence = float(conf_match.group(1)) if conf_match else 0.0
        except ValueError:
            confidence = 0.0
        explanation = raw_text.strip()
        return {"label": label, "confidence": confidence, "explanation": explanation}

    @staticmethod
    def _escape_inline_quotes(text: str) -> str:
        # Handle common case where inner quotes in parentheses break JSON strings, e.g., ("Dear User")
        return re.sub(r'\\("([^"]*)"\\)', r'(\\1)', text)
