from types import SimpleNamespace

from locker_manage_system.lottery import run_floor_lottery


def test_run_floor_lottery_assigns_lowest_available_lockers_with_seed():
    applications = [
        SimpleNamespace(application_id="app1"),
        SimpleNamespace(application_id="app2"),
        SimpleNamespace(application_id="app3"),
    ]

    winners = run_floor_lottery(applications=applications, open_lockers=["4002", "4001"], seed=7)

    assert [winner.application_id for winner in winners] == ["app2", "app1"]
    assert [winner.locker_number for winner in winners] == ["4001", "4002"]
