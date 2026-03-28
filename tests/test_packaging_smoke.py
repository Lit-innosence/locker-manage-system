from pathlib import Path


def test_pyinstaller_spec_exists():
    assert Path("packaging/pyinstaller.spec").exists()
