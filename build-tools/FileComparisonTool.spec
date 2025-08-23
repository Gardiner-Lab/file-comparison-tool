# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.abspath(SPECPATH)), 'src')
sys.path.insert(0, src_path)

block_cipher = None

# Data files to include
datas = [
    ('docs', 'docs'),
    ('test_data', 'test_data'),
    ('README.md', '.'),
    ('requirements.txt', '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'pandas',
    'openpyxl',
    'xlrd',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'src.gui.main_window',
    'src.controllers.main_controller',
    'src.services.file_parser_service',
    'src.services.comparison_engine',
    'src.services.export_service',
    'src.services.error_handler',
    'src.services.help_service',
    'src.services.performance_optimizer',
    'src.models.file_info',
    'src.models.comparison_config',
    'src.models.operation_result',
]

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary modules to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith('matplotlib')]
a.binaries = [x for x in a.binaries if not x[0].startswith('scipy')]
a.binaries = [x for x in a.binaries if not x[0].startswith('numpy.random')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileComparisonTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
