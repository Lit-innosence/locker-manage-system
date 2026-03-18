from locker_manage_system.config import load_config


def test_load_config_reads_floor_rules(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "year: 2026\nfloors:\n  2F:\n    capacity: 420\n    occupancy: pair_only\n",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.year == 2026
    assert config.floors["2F"].capacity == 420
    assert config.floors["2F"].occupancy == "pair_only"
