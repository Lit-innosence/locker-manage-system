"""Entry point for the locker manage system CLI."""

from __future__ import annotations

import sys
from pathlib import Path

from .cli import build_parser
from .lottery_command import run_lottery
from .validate_command import run_validate


def _term_year(term: str) -> str:
    start_date = term.split("..", maxsplit=1)[0]
    return start_date.split("-", maxsplit=1)[0]


def _default_state_dir(term: str, output_dir: str) -> str:
    return str(Path(output_dir) / "state" / _term_year(term))


def _default_review_dir(term: str, output_dir: str) -> str:
    return str(Path(output_dir) / term / "review")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        run_validate(
            config_path=args.config,
            term=args.term,
            input_dir=args.input_dir,
            state_dir=args.state_dir or _default_state_dir(args.term, args.output_dir),
            output_dir=args.output_dir,
        )
        return 0

    if args.command == "lottery":
        run_lottery(
            config_path=args.config,
            term=args.term,
            review_dir=args.review_dir or _default_review_dir(args.term, args.output_dir),
            state_dir=args.state_dir or _default_state_dir(args.term, args.output_dir),
            output_dir=args.output_dir,
            seed=args.seed,
        )
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
