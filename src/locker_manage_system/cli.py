"""Command line interface for the locker manage system."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="locker-manage-system")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate weekly applications")
    validate_parser.add_argument("--config", required=True)
    validate_parser.add_argument("--term", required=True)
    validate_parser.add_argument("--input-dir", required=True)
    validate_parser.add_argument("--state-dir", required=True)
    validate_parser.add_argument("--output-dir", required=True)

    lottery_parser = subparsers.add_parser("lottery", help="Run the locker lottery")
    lottery_parser.add_argument("--config", required=True)
    lottery_parser.add_argument("--term", required=True)
    lottery_parser.add_argument("--review-dir", required=True)
    lottery_parser.add_argument("--state-dir", required=True)
    lottery_parser.add_argument("--output-dir", required=True)
    lottery_parser.add_argument("--seed", type=int, default=None)

    return parser
