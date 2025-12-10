#!/usr/bin/env python3
"""Generate profile-aware training emails and send or save them."""

import argparse
import csv
import json
import os
import re
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path
from typing import List

import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from common.config import Settings
from common.profile import Profile
from red_agent.generator import PhishingGenerator
from red_agent.scenarios import SCENARIOS, Scenario


@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    from_email: str
    use_tls: bool = True


@dataclass
class Target:
    email: str
    profile: Profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate profile-aware phishing emails for PRAHAAR training."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="CSV or JSON file with targets. Columns/fields: email, name, role, company, department, interests, recent_events.",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="salary_slip",
        help=f"Scenario name ({', '.join(s.name for s in SCENARIOS)}).",
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        default="medium",
        help="Difficulty level defined in the scenario.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send emails via SMTP. Default is dry-run to .eml files.",
    )
    parser.add_argument(
        "--outbox",
        type=Path,
        default=None,
        help="Where to write .eml files during dry-run.",
    )
    parser.add_argument(
        "--from-email",
        type=str,
        default=None,
        help="Override From email. Defaults to FROM_EMAIL env or training@example.com.",
    )
    return parser


def get_scenario(name: str) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.name == name:
            return scenario
    raise ValueError(f"Unknown scenario '{name}'. Valid options: {[s.name for s in SCENARIOS]}")


def parse_bool_env(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no"}


def load_smtp_config(from_email: str | None, require_full: bool) -> SMTPConfig:
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASS", "")
    use_tls = parse_bool_env(os.getenv("SMTP_USE_TLS"), default=True)
    resolved_from = from_email or os.getenv("FROM_EMAIL", "training@example.com")

    if require_full and not (host and username and password):
        raise RuntimeError(
            "SMTP_HOST, SMTP_PORT, SMTP_USER, and SMTP_PASS must be set to send emails."
        )

    return SMTPConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        from_email=resolved_from,
        use_tls=use_tls,
    )


def load_targets(path: Path) -> List[Target]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _load_targets_csv(path)
    if suffix in {".json", ".jsonl"}:
        return _load_targets_json(path)
    raise ValueError(f"Unsupported input format for {path}. Use CSV or JSON.")


def _extract_target(entry: dict) -> Target | None:
    email = entry.get("email") or entry.get("target_email")
    if not email:
        return None
    profile_data = entry.get("profile", {k: v for k, v in entry.items() if k not in {"email", "target_email"}})
    profile = Profile.from_dict(profile_data)
    return Target(email=email, profile=profile)


def _load_targets_csv(path: Path) -> List[Target]:
    targets: List[Target] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            target = _extract_target(row)
            if target:
                targets.append(target)
    return targets


def _load_targets_json(path: Path) -> List[Target]:
    targets: List[Target] = []
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("JSON input must be an array of objects.")
    for entry in data:
        if isinstance(entry, dict):
            target = _extract_target(entry)
            if target:
                targets.append(target)
    return targets


def sanitize_filename(value: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", value)
    return safe.strip("_") or "email"


def send_email(message: EmailMessage, config: SMTPConfig, timeout: int = 30) -> None:
    with smtplib.SMTP(config.host, config.port, timeout=timeout) as server:
        if config.use_tls:
            server.starttls()
        if config.username:
            server.login(config.username, config.password)
        server.send_message(message)


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()
    scenario = get_scenario(args.scenario)
    if args.difficulty not in scenario.difficulty_levels:
        raise ValueError(
            f"Difficulty '{args.difficulty}' not in {scenario.difficulty_levels} for scenario '{scenario.name}'."
        )

    targets = load_targets(args.input)
    if not targets:
        raise RuntimeError("No targets found in input file.")

    generator = PhishingGenerator(settings)
    smtp_config = load_smtp_config(args.from_email, require_full=args.send)
    dry_run = not args.send
    outbox = (
        args.outbox
        if args.outbox
        else settings.data_dir / "processed" / "outbox"
    )
    if dry_run:
        outbox.mkdir(parents=True, exist_ok=True)

    for target in targets:
        print(f"[start] Generating email for {target.email} ({args.scenario}/{args.difficulty})", flush=True)
        example = generator.generate(scenario, args.difficulty, profile=target.profile)
        msg = EmailMessage()
        msg["From"] = smtp_config.from_email
        msg["To"] = target.email
        msg["Subject"] = example.subject or example.summary or f"Training simulation: {example.scenario}"
        msg["X-PRAHAAR-Training"] = "true"
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        msg.set_content(example.body)
        print(f"[ready] Message composed for {target.email}, sending={not dry_run}", flush=True)

        if dry_run:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = outbox / f"{timestamp}_{sanitize_filename(target.email)}.eml"
            with filename.open("w", encoding="utf-8") as handle:
                handle.write(msg.as_string())
            print(f"[dry-run] Wrote email for {target.email} to {filename}")
        else:
            try:
                print(f"[send] Connecting to {smtp_config.host}:{smtp_config.port} for {target.email}", flush=True)
                send_email(msg, smtp_config)
                print(f"[sent] Training email to {target.email}", flush=True)
            except Exception as exc:  # pragma: no cover - runtime guardrail
                print(f"[error] Failed to send to {target.email}: {exc}", flush=True)
                raise


if __name__ == "__main__":
    main()
