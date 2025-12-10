#!/usr/bin/env python3
"""Simple red-vs-blue simulation loop."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pathlib import Path

from blue_agent.classifier import PhishingClassifier
from common.config import Settings
from red_agent.generator import PhishingGenerator
from red_agent.scenarios import SCENARIOS


def main() -> None:
    settings = Settings.from_env()
    generator = PhishingGenerator(settings)
    classifier = PhishingClassifier(settings)

    log_path = settings.data_dir / "processed" / "simulation_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("w", encoding="utf-8") as handle:
        for scenario in SCENARIOS:
            for difficulty in scenario.difficulty_levels:
                example = generator.generate(scenario, difficulty)
                result = classifier.classify(example.body)
                hit = result.label.lower().startswith("phish")
                handle.write(
                    f"{scenario.name},{difficulty},{'CAUGHT' if hit else 'MISSED'},"
                    f"{result.confidence:.2f},{result.explanation}\n"
                )
    print(f"Simulation log stored at {log_path}")


if __name__ == "__main__":
    main()
