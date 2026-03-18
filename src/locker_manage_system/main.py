"""Entry point for the locker manage system CLI."""

from __future__ import annotations

import sys

from .cli import build_parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
