"""Configuration loading for locker rules and paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class FloorConfig:
    capacity: int
    occupancy: str
    locker_start: int | None = None
    locker_end: int | None = None


@dataclass(frozen=True)
class PathConfig:
    input_dir: str = "input"
    state_dir: str = "state"
    output_dir: str = "output"


@dataclass(frozen=True)
class AppConfig:
    year: int
    floors: dict[str, FloorConfig]
    paths: PathConfig


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    raw_config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    floors = {
        floor_name: FloorConfig(
            capacity=floor_data["capacity"],
            occupancy=floor_data["occupancy"],
            locker_start=floor_data.get("locker_start"),
            locker_end=floor_data.get("locker_end"),
        )
        for floor_name, floor_data in raw_config.get("floors", {}).items()
    }
    path_config = raw_config.get("paths", {})

    return AppConfig(
        year=raw_config["year"],
        floors=floors,
        paths=PathConfig(
            input_dir=path_config.get("input_dir", "input"),
            state_dir=path_config.get("state_dir", "state"),
            output_dir=path_config.get("output_dir", "output"),
        ),
    )
