# Locker Lottery CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a cross-platform CLI that validates weekly locker applications, emits review CSVs for manual screening, runs floor-by-floor lotteries, and exports CSV/PDF outputs without requiring a Python runtime on the administrator machine.

**Architecture:** Implement a Python package with a thin CLI layer and isolated domain modules for config loading, CSV normalization, validation, review export, lottery execution, state persistence, and PDF rendering. Keep `validate` and `lottery` as separate commands so that auto-validation output, human-edited review files, and final lottery artifacts live in distinct directories.

**Tech Stack:** Python, pytest, standard-library `csv` / `pathlib` / `argparse`, a lightweight PDF library, and PyInstaller for packaging

---

### Task 1: Project skeleton and packaging metadata

**Files:**
- Create: `pyproject.toml`
- Create: `src/locker_manage_system/__init__.py`
- Create: `src/locker_manage_system/cli.py`
- Create: `src/locker_manage_system/main.py`
- Create: `tests/test_cli_smoke.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.cli import build_parser


def test_parser_exposes_validate_and_lottery_commands():
    parser = build_parser()
    subparsers = parser._subparsers._group_actions[0]
    assert {"validate", "lottery"}.issubset(subparsers.choices.keys())
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `build_parser`

**Step 3: Write minimal implementation**

Create the package skeleton and an `argparse` parser with `validate` and `lottery` subcommands wired to a `main()` entry point.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src/locker_manage_system tests/test_cli_smoke.py
git commit -m "feat: scaffold locker lottery cli"
```

### Task 2: Config model and default locker rules

**Files:**
- Create: `src/locker_manage_system/config.py`
- Create: `config/default.yml`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with missing config loader

**Step 3: Write minimal implementation**

Add typed config models, a loader, and a default config defining floor capacities, locker number ranges, allowed occupancy, and state directories.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add config/default.yml src/locker_manage_system/config.py tests/test_config.py
git commit -m "feat: add locker rules config"
```

### Task 3: CSV input normalization based on demo headers

**Files:**
- Create: `src/locker_manage_system/csv_io.py`
- Create: `src/locker_manage_system/models.py`
- Create: `tests/test_csv_io.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.csv_io import load_applicants_csv


def test_load_applicants_csv_resolves_floor_from_either_column(tmp_path):
    path = tmp_path / "applicants.csv"
    path.write_text(
        "\ufeffタイムスタンプ,申請者の学籍番号,申請者の氏名,申請者の学生証写真,共同利用者の有無,共同利用者の学籍番号,共同利用者の氏名,階数希望選択（共同利用者なし）,階数希望選択（共同利用者あり）\n"
        "2026-04-01 00:00:00,4654293,藤田 治,accept,共同利用者なし,,,,4階,\n",
        encoding="utf-8",
    )
    rows = load_applicants_csv(path)
    assert rows[0].requested_floor == "4F"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_csv_io.py -v`
Expected: FAIL with missing reader

**Step 3: Write minimal implementation**

Parse BOM-safe CSV files, validate required columns, normalize timestamps, and map Japanese headers to internal applicant and partner row models.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_csv_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/csv_io.py src/locker_manage_system/models.py tests/test_csv_io.py
git commit -m "feat: normalize input csv rows"
```

### Task 4: Student ID and occupancy validation rules

**Files:**
- Create: `src/locker_manage_system/validation_rules.py`
- Create: `tests/test_validation_rules.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.validation_rules import validate_student_id


def test_validate_student_id_accepts_allowed_patterns():
    assert validate_student_id("1588184") is True
    assert validate_student_id("4654293") is True
    assert validate_student_id("8654293") is True
    assert validate_student_id("2032044") is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation_rules.py -v`
Expected: FAIL with missing validator

**Step 3: Write minimal implementation**

Implement student ID validation, required-field checks, and floor occupancy rules covering pair-only floors `2F/3F` and single-only floors `4F/5F/6F`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/validation_rules.py tests/test_validation_rules.py
git commit -m "feat: add validation rule helpers"
```

### Task 5: Winner history and locker state repositories

**Files:**
- Create: `src/locker_manage_system/state.py`
- Create: `tests/test_state.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.state import load_winner_ids


def test_load_winner_ids_reads_both_applicant_and_partner_ids(tmp_path):
    path = tmp_path / "winners.csv"
    path.write_text(
        "申請者氏名,申請者学籍番号,共同利用者氏名,共同利用者学籍番号,処理日,割り当てロッカー\n"
        "吉田 結衣,1556822,中村 稔,4162071,2026-04-01,5001\n",
        encoding="utf-8",
    )
    assert load_winner_ids(path) == {"1556822", "4162071"}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_state.py -v`
Expected: FAIL with missing state loader

**Step 3: Write minimal implementation**

Add repository functions for loading and saving winner history and locker assignment state, including initialization helpers for a fresh academic year.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/state.py tests/test_state.py
git commit -m "feat: add state repositories"
```

### Task 6: Validation pipeline for E1 to E3

**Files:**
- Create: `src/locker_manage_system/validation_pipeline.py`
- Create: `tests/test_validation_pipeline.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.validation_pipeline import classify_application
from locker_manage_system.models import NormalizedApplication


def test_classify_application_returns_e2_when_partner_submission_missing():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="pair",
        partner_id="4162071",
        partner_name="中村 稔",
        partner_timestamp=None,
        partner_card_ref=None,
    )
    assert classify_application(application, winner_ids=set()) == "E2"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation_pipeline.py -v`
Expected: FAIL with missing classifier

**Step 3: Write minimal implementation**

Build the initial validation pipeline that classifies each normalized application with priority ordering for E1, E2, and E3.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/validation_pipeline.py tests/test_validation_pipeline.py
git commit -m "feat: classify applications with validation pipeline"
```

### Task 7: E4 deduplication and competing-pair resolution

**Files:**
- Modify: `src/locker_manage_system/validation_pipeline.py`
- Create: `tests/test_validation_e4.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.validation_pipeline import resolve_duplicate_applications


def test_resolve_duplicate_applications_prefers_earliest_conflicting_pair():
    resolved = resolve_duplicate_applications([...])
    assert resolved.accepted_application_ids == {"pair-a"}
    assert resolved.rejected_codes["pair-b"] == "E4"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation_e4.py -v`
Expected: FAIL because E4 logic is absent

**Step 3: Write minimal implementation**

Implement duplicate submission pruning and competing-pair conflict resolution using latest-single and earliest-pair rules from the requirements.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation_e4.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/validation_pipeline.py tests/test_validation_e4.py
git commit -m "feat: resolve duplicate and competing applications"
```

### Task 8: Validation exports and review file generation

**Files:**
- Create: `src/locker_manage_system/validate_command.py`
- Create: `tests/test_validate_command.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.validate_command import run_validate


def test_run_validate_writes_validation_and_review_outputs(tmp_path):
    result = run_validate(...)
    assert (tmp_path / "output/term1/validation/valid_4F.csv").exists()
    assert (tmp_path / "output/term1/review/review_4F.csv").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_validate_command.py -v`
Expected: FAIL with missing validate workflow

**Step 3: Write minimal implementation**

Wire together config loading, CSV parsing, validation, floor grouping, invalid export generation, and review file creation with `manual_status` initialized blank.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_validate_command.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/validate_command.py tests/test_validate_command.py
git commit -m "feat: export validation and review files"
```

### Task 9: Lottery engine and locker assignment

**Files:**
- Create: `src/locker_manage_system/lottery.py`
- Create: `tests/test_lottery.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.lottery import run_floor_lottery


def test_run_floor_lottery_assigns_lowest_available_lockers_with_seed():
    winners = run_floor_lottery(applications=[...], open_lockers=["4001", "4002"], seed=7)
    assert [winner.locker_number for winner in winners] == ["4001", "4002"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lottery.py -v`
Expected: FAIL with missing lottery engine

**Step 3: Write minimal implementation**

Implement deterministic random selection, floor-specific capacity handling, and ascending locker assignment for chosen winners.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lottery.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/lottery.py tests/test_lottery.py
git commit -m "feat: add lottery engine"
```

### Task 10: Review-input parsing and `lottery` command workflow

**Files:**
- Create: `src/locker_manage_system/review_io.py`
- Create: `src/locker_manage_system/lottery_command.py`
- Create: `tests/test_lottery_command.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.lottery_command import run_lottery


def test_run_lottery_uses_only_manual_keep_rows(tmp_path):
    result = run_lottery(...)
    assert result.winner_count == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lottery_command.py -v`
Expected: FAIL with missing lottery workflow

**Step 3: Write minimal implementation**

Parse review CSV files, filter `manual_status=keep`, call the lottery engine, and write `result.csv`, locker state updates, and a machine-readable lottery log.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lottery_command.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/review_io.py src/locker_manage_system/lottery_command.py tests/test_lottery_command.py
git commit -m "feat: wire lottery command workflow"
```

### Task 11: PDF export for public winner list

**Files:**
- Create: `src/locker_manage_system/pdf_export.py`
- Create: `tests/test_pdf_export.py`

**Step 1: Write the failing test**

```python
from locker_manage_system.pdf_export import export_lottery_pdf


def test_export_lottery_pdf_creates_single_file(tmp_path):
    output = tmp_path / "lottery_result.pdf"
    export_lottery_pdf(output, processed_date="2026-04-03", floor_winners={"2F": [], "4F": ["4654293"]})
    assert output.exists()
    assert output.stat().st_size > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pdf_export.py -v`
Expected: FAIL with missing PDF exporter

**Step 3: Write minimal implementation**

Add a minimal PDF renderer that writes one document with floor sections and applicant IDs only, showing `該当なし` when a floor has no winners.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pdf_export.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/locker_manage_system/pdf_export.py tests/test_pdf_export.py
git commit -m "feat: export lottery result pdf"
```

### Task 12: End-to-end regression fixture using `demo-input`

**Files:**
- Create: `tests/fixtures/demo_state/winners.csv`
- Create: `tests/fixtures/demo_state/lockers.csv`
- Create: `tests/test_end_to_end.py`

**Step 1: Write the failing test**

```python
def test_validate_then_lottery_with_demo_input(tmp_path):
    ...
    assert (tmp_path / "output/term1/lottery/result.csv").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_end_to_end.py -v`
Expected: FAIL before workflows are fully wired

**Step 3: Write minimal implementation**

Use the repository `demo-input` CSV files plus fixture state files to verify the full `validate` then `lottery` flow, including review-file editing and final artifact creation.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_end_to_end.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/fixtures/demo_state tests/test_end_to_end.py
git commit -m "test: add end-to-end flow coverage"
```

### Task 13: Executable packaging and operator documentation

**Files:**
- Modify: `README.md`
- Create: `packaging/pyinstaller.spec`
- Create: `tests/test_packaging_smoke.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_pyinstaller_spec_exists():
    assert Path("packaging/pyinstaller.spec").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_packaging_smoke.py -v`
Expected: FAIL because packaging assets are absent

**Step 3: Write minimal implementation**

Add packaging assets and README instructions covering config setup, `validate`, manual review editing, `lottery`, and OS-specific executable builds.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_packaging_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md packaging/pyinstaller.spec tests/test_packaging_smoke.py
git commit -m "docs: add packaging and operator guide"
```

### Task 14: Full verification before handoff

**Files:**
- Modify: `README.md`

**Step 1: Run the targeted test suite**

Run: `pytest tests/test_cli_smoke.py tests/test_config.py tests/test_csv_io.py tests/test_validation_rules.py tests/test_state.py tests/test_validation_pipeline.py tests/test_validation_e4.py tests/test_validate_command.py tests/test_lottery.py tests/test_lottery_command.py tests/test_pdf_export.py tests/test_end_to_end.py tests/test_packaging_smoke.py -v`
Expected: PASS

**Step 2: Run the full suite**

Run: `pytest -v`
Expected: PASS

**Step 3: Exercise the CLI manually**

Run: `python -m locker_manage_system.main validate --config config/default.yml --term term1 --input-dir demo-input --state-dir tests/fixtures/demo_state --output-dir tmp/output`
Expected: Validation and review CSVs are created

**Step 4: Exercise lottery manually**

Run: `python -m locker_manage_system.main lottery --config config/default.yml --term term1 --review-dir tmp/output/term1/review --state-dir tests/fixtures/demo_state --output-dir tmp/output`
Expected: Result CSV, locker state, and PDF are created

**Step 5: Commit**

```bash
git add README.md
git commit -m "chore: verify locker lottery cli"
```
