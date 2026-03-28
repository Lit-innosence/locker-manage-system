# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path(SPECPATH).resolve().parent
src_dir = project_root / "src"

a = Analysis(
    [str(src_dir / "locker_manage_system" / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[(str(project_root / "config" / "default.yml"), "config")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="locker-manage-system",
    console=True,
)
