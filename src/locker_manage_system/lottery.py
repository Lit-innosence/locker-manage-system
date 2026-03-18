"""Lottery helpers for selecting winners and assigning lockers."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Sequence


@dataclass(frozen=True)
class FloorLotteryWinner:
    application_id: str
    locker_number: str


def _application_id(application: object) -> str:
    application_id = getattr(application, "application_id", "")
    if not application_id:
        raise ValueError("Lottery applications must have an application_id")
    return application_id


def run_floor_lottery(
    *,
    applications: Sequence[object],
    open_lockers: Sequence[str],
    seed: int | None = None,
) -> list[FloorLotteryWinner]:
    winner_count = min(len(applications), len(open_lockers))
    if winner_count == 0:
        return []

    selected_applications = Random(seed).sample(list(applications), winner_count)
    sorted_lockers = sorted(open_lockers)

    return [
        FloorLotteryWinner(
            application_id=_application_id(application),
            locker_number=locker_number,
        )
        for application, locker_number in zip(selected_applications, sorted_lockers)
    ]
