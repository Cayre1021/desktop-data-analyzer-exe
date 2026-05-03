from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path.cwd()
hiddenimports = collect_submodules("matplotlib.backends") + ["xlrd"]


a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "sample_data"), "sample_data"),
        (str(project_root / "docs" / "user-guide.md"), "docs"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="desktop-data-analyzer",
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="desktop-data-analyzer",
)
