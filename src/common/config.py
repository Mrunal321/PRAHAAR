import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Shared runtime configuration for both agents."""

    openai_api_key: str
    model: str = "gpt-4o-mini"
    data_dir: Path = Path("data")

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment or .env file")
        model = os.getenv("LLM_MODEL", cls.model)
        data_dir = Path(os.getenv("DATA_DIR", cls.data_dir))
        return cls(openai_api_key=api_key, model=model, data_dir=data_dir)
