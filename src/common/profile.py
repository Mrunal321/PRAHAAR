from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


def _clean_text(value: str, max_len: int = 280) -> str:
    """Collapse whitespace and trim length to reduce prompt-injection surface."""
    collapsed = " ".join(value.split())
    return collapsed[:max_len]


def _clean_list(items: List[str] | str | None, max_len: int = 180) -> List[str]:
    if items is None:
        return []
    if isinstance(items, str):
        parts = [part.strip() for part in items.replace(";", ",").split(",")]
    else:
        parts = [str(item).strip() for item in items]
    cleaned = [_clean_text(part, max_len=max_len) for part in parts if part.strip()]
    return [item for item in cleaned if item]


@dataclass
class Profile:
    """Profile attributes used to personalize training emails."""

    name: str | None = None
    email: str | None = None
    role: str | None = None
    company: str | None = None
    department: str | None = None
    interests: List[str] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)
    extra: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Profile":
        """Create a Profile from a loosely typed dictionary."""
        known = {key: data.get(key) for key in (
            "name",
            "email",
            "role",
            "company",
            "department",
            "interests",
            "recent_events",
        )}
        extras = {
            key: _clean_text(str(value))
            for key, value in data.items()
            if key not in known and value is not None
        }

        return cls(
            name=_clean_text(str(known["name"])) if known.get("name") else None,
            email=_clean_text(str(known["email"])) if known.get("email") else None,
            role=_clean_text(str(known["role"])) if known.get("role") else None,
            company=_clean_text(str(known["company"])) if known.get("company") else None,
            department=_clean_text(str(known["department"]))
            if known.get("department")
            else None,
            interests=_clean_list(known.get("interests")),
            recent_events=_clean_list(known.get("recent_events")),
            extra=extras,
        )

    def to_prompt_block(self) -> str:
        """Render the profile as a short, safe prompt snippet."""
        lines: List[str] = []

        def add(label: str, value: str | None) -> None:
            if value:
                lines.append(f"{label}: {value}")

        add("Name", self.name)
        add("Email", self.email)
        add("Role", self.role)
        add("Company", self.company)
        add("Department", self.department)
        if self.interests:
            lines.append(f"Interests: {', '.join(self.interests)}")
        if self.recent_events:
            lines.append(f"Recent events: {', '.join(self.recent_events)}")
        for key, value in self.extra.items():
            add(key.capitalize(), value)

        return "\n".join(lines) if lines else "N/A"
