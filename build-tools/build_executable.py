#!/usr/bin/env python3
"""
Build script for creating standalone executables of the File Comparison Tool.

This script uses PyInstaller to create standalone executables for different platforms.
It handles all the necessary configuration for bundling the GUI application.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Build configuration
APP_NAME = "FileComparisonTool"
MAIN_SCRIPT = "main.py"
VERSION = "1.0.0"
AUTHOR = "File Comparison Tool Team"
DESCRIPTION = "A GUI application for comparing Excel and CSV files"

def get_platform_suffix():
    """Get platform-specific suffix for the executable."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        return f"win-{arch}"
    elif system == "darwin":
        return f"macos-{arch}"
    elif system == "linux":
        return f"linux-{arch}"
    else:
        return f"{system}-{arch}"

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        print(f"Removing {spec_file}...")
        spec_file.unlink()

def create_pyinstaller_spec():
    """Create PyInstaller spec file with custom configuration."""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

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
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
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
    name='{APP_NAME}',
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
'''
    
    with open(f"{APP_NAME}.spec", "w") as f:
        f.write(spec_content)
    
    print(f"Created PyInstaller spec file: {APP_NAME}.spec")

def create_version_info():
    """Create version info file for Windows executable."""
    if platform.system() != "Windows":
        return
    
    version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'{AUTHOR}'),
           StringStruct(u'FileDescription', u'{DESCRIPTION}'),
           StringStruct(u'FileVersion', u'{VERSION}'),
           StringStruct(u'InternalName', u'{APP_NAME}'),
           StringStruct(u'LegalCopyright', u'Copyright © 2024 {AUTHOR}'),
           StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
           StringStruct(u'ProductName', u'File Comparison Tool'),
           StringStruct(u'ProductVersion', u'{VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open("version_info.txt", "w") as f:
        f.write(version_info)
    
    print("Created version info file for Windows")

def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("Building standalone executable...")
    
    # Check if PyInstaller is available
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: PyInstaller not found. Install it with: pip install pyinstaller")
        return False
    
    # Build command
    cmd = [
        "pyinstaller",
        f"{APP_NAME}.spec",
        "--clean",
        "--noconfirm"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_distribution_package():
    """Create a distribution package with the executable and documentation."""
    platform_suffix = get_platform_suffix()
    dist_name = f"{APP_NAME}-{VERSION}-{platform_suffix}"
    dist_dir = Path("dist") / dist_name
    
    # Create distribution directory
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_name = f"{APP_NAME}.exe" if platform.system() == "Windows" else APP_NAME
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / exe_name)
        print(f"Copied executable to {dist_dir}")
    else:
        print(f"ERROR: Executable not found at {exe_path}")
        return False
    
    # Copy documentation and data files
    files_to_copy = [
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt"),
        ("docs", "docs"),
        ("test_data", "test_data"),
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = dist_dir / dst
        
        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            print(f"Copied {src} to distribution package")
    
    # Create installation instructions
    install_instructions = f"""# {APP_NAME} v{VERSION}

## Installation Instructions

### Windows
1. Extract this archive to your desired location
2. Run {exe_name} to start the application
3. No additional installation required - all dependencies are bundled

### Usage
- Double-click {exe_name} to start the File Comparison Tool
- Follow the step-by-step interface to compare your Excel/CSV files
- Refer to the docs folder for detailed user guide

### System Requirements
- Windows 10 or later (64-bit recommended)
- At least 4GB RAM for large file processing
- 100MB free disk space

### Support
For support and documentation, visit:
https://github.com/filecomparisontool/file-comparison-tool

### License
This software is distributed under the MIT License.
See the included documentation for full license terms.
"""
    
    with open(dist_dir / "INSTALL.txt", "w") as f:
        f.write(install_instructions)
    
    # Create archive
    archive_name = f"{dist_name}"
    print(f"Creating distribution archive: {archive_name}")
    
    if platform.system() == "Windows":
        shutil.make_archive(archive_name, 'zip', "dist", dist_name)
        print(f"Created: {archive_name}.zip")
    else:
        shutil.make_archive(archive_name, 'gztar', "dist", dist_name)
        print(f"Created: {archive_name}.tar.gz")
    
    return True

def main():
    """Main build process."""
    print(f"Building {APP_NAME} v{VERSION} for {platform.system()} {platform.machine()}")
    print("=" * 60)
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    
    # Step 2: Create build configuration files
    create_pyinstaller_spec()
    create_version_info()
    
    # Step 3: Build executable
    if not build_executable():
        print("Build failed!")
        return 1
    
    # Step 4: Create distribution package
    if not create_distribution_package():
        print("Distribution package creation failed!")
        return 1
    
    print("=" * 60)
    print("Build completed successfully!")
    print(f"Executable location: dist/{APP_NAME}")
    print(f"Distribution package created in current directory")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())