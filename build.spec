# PyInstaller spec file for surreal-namer
# Build with: pyinstaller build.spec

import sys
from pathlib import Path

ROOT = Path.cwd()
MAIN_SCRIPT = ROOT / "gui.py"

DATAS = [
    (str(ROOT / "namer.py"), "."),
    (str(ROOT / "analyzer.py"), "."),
    (str(ROOT / "main.py"), "."),
]

HIDDEN_IMPORTS = [
    "PIL", "PIL.Image", "PIL.ExifTags", "PIL.ImageQt",
    "PyQt6", "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
    "colorsys", "hashlib", "json", "pathlib", "typing",
]

EXCLUDES = [
    "pytest", "matplotlib", "numpy", "scipy", "pandas",
    "IPython", "jupyter", "notebook", "sphinx", "setuptools",
    "pip", "wheel", "tkinter", "test", "unittest", "pydoc", "doctest",
]

block_cipher = None

a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=DATAS,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="surreal-namer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "icon.ico") if (ROOT / "icon.ico").exists() else None,
)