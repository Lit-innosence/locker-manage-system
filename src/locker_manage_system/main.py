"""Entry point for the locker manage system CLI."""

from __future__ import annotations

import sys
from datetime import date
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


def _prompt_command() -> str:
    while True:
        value = input("実行する処理を入力してください [validate/lottery]: ").strip()
        if value in {"validate", "lottery"}:
            return value
        print("validate または lottery を入力してください。Ctrl+C で終了できます。")


def _prompt_date(label: str, example: str) -> str:
    while True:
        value = input(f"{label}を入力してください（例: {example}）: ").strip()
        try:
            date.fromisoformat(value)
            return value
        except ValueError:
            print("日付は YYYY-MM-DD 形式で入力してください。Ctrl+C で終了できます。")


def _prompt_term() -> str:
    while True:
        start_date = _prompt_date("開始日", "2026-04-01")
        end_date = _prompt_date("終了日", "2026-04-07")
        if end_date >= start_date:
            return f"{start_date}..{end_date}"
        print("終了日は開始日以降の日付を入力してください。Ctrl+C で終了できます。")


def _interactive_args() -> list[str]:
    command = _prompt_command()
    term = _prompt_term()
    return [command, "--term", term]


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv = _interactive_args()

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
