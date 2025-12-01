#!/usr/bin/env python3
"""Generate a synthetic phishing dataset and store it under data/raw/."""

import argparse
import csv
from datetime import datetime
from pathlib import Path

from common.config import Settings
from red_agent.generator import PhishingGenerator
from red_agent.scenarios import SCENARIOS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate phishing emails for PRAHAAR red agent."
    )
    parser.add_argument(
        "--per-scenario",
        type=int,
        default=5,
        help="Number of samples per scenario/difficulty pair.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional override for the output CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()
    generator = PhishingGenerator(settings)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = (
        args.output
        if args.output
        else settings.data_dir / "raw" / f"phishing_{timestamp}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for scenario in SCENARIOS:
        for difficulty in scenario.difficulty_levels:
            for _ in range(args.per_scenario):
                example = generator.generate(scenario, difficulty)
                rows.append(example.to_dict())

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "difficulty",
                "subject",
                "body",
                "summary",
                "red_flags",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} examples to {output_path}")


if __name__ == "__main__":
    main()
