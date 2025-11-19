#!/usr/bin/env python3
"""Run the blue agent against a dataset and print simple metrics."""

import argparse
import csv
from pathlib import Path

from blue_agent.classifier import PhishingClassifier
from common.config import Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate blue agent classifier.")
    parser.add_argument("dataset", type=Path, help="Path to phishing CSV dataset.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()
    classifier = PhishingClassifier(settings)

    total = 0
    correct = 0
    with args.dataset.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total += 1
            result = classifier.classify(row["body"])
            predicted = result.label.lower()
            expected = row.get("label", "phishing").lower()
            if predicted == expected:
                correct += 1
            print(
                f"[{predicted.upper()}|{result.confidence:.2f}] {row['scenario']} - {result.explanation}"
            )

    accuracy = correct / total if total else 0
    print(f"\nAccuracy: {accuracy:.2%} ({correct}/{total})")


if __name__ == "__main__":
    main()
