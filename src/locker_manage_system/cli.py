"""Command line interface for the locker manage system."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="locker-manage-system")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate weekly applications")
    subparsers.add_parser("lottery", help="Run the locker lottery")

    return parser
