#!/usr/bin/env python3
"""
Installer creation script for File Comparison Tool.

This script creates platform-specific installers for the File Comparison Tool.
It supports creating MSI installers for Windows and DMG packages for macOS.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import tempfile

# Installer configuration
APP_NAME = "File Comparison Tool"
APP_ID = "FileComparisonTool"
VERSION = "1.0.0"
AUTHOR = "File Comparison Tool Team"
DESCRIPTION = "A GUI application for comparing Excel and CSV files"
URL = "https://github.com/filecomparisontool/file-comparison-tool"

def create_windows_installer():
    """Create Windows MSI installer using WiX or NSIS."""
    print("Creating Windows installer...")
    
    # Check if we have the executable
    exe_path = Path("dist") / f"{APP_ID}.exe"
    if not exe_path.exists():
        print(f"ERROR: Executable not found at {exe_path}")
        print("Please run build_executable.py first")
        return False
    
    # Try to create NSIS installer first (more common)
    if create_nsis_installer():
        return True
    
    # Fallback to simple ZIP distribution
    print("Creating ZIP distribution for Windows...")
    return create_zip_distribution()

def create_nsis_installer():
    """Create NSIS installer script and build installer."""
    try:
        # Check if NSIS is available
        subprocess.run(["makensis", "/VERSION"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("NSIS not found. Skipping NSIS installer creation.")
        return False
    
    # Create NSIS script
    nsis_script = f'''
; File Comparison Tool NSIS Installer Script
; Generated automatically by create_installer.py

!define APP_NAME "{APP_NAME}"
!define APP_ID "{APP_ID}"
!define VERSION "{VERSION}"
!define AUTHOR "{AUTHOR}"
!define URL "{URL}"
!define EXE_NAME "{APP_ID}.exe"

; Include Modern UI
!include "MUI2.nsh"

; General settings
Name "${{APP_NAME}}"
OutFile "{APP_ID}-{VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_ID}}" ""
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "{VERSION}.0"
VIAddVersionKey "ProductName" "${{APP_NAME}}"
VIAddVersionKey "CompanyName" "${{AUTHOR}}"
VIAddVersionKey "FileDescription" "{DESCRIPTION}"
VIAddVersionKey "FileVersion" "{VERSION}"
VIAddVersionKey "ProductVersion" "{VERSION}"
VIAddVersionKey "LegalCopyright" "© 2024 ${{AUTHOR}}"

; Installer sections
Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    ; Copy main executable
    File "dist\\${{EXE_NAME}}"
    
    ; Copy documentation
    File "README.md"
    File "requirements.txt"
    
    ; Copy documentation folder
    SetOutPath "$INSTDIR\\docs"
    File /r "docs\\*.*"
    
    ; Copy test data
    SetOutPath "$INSTDIR\\test_data"
    File /r "test_data\\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{EXE_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{EXE_NAME}}"
    
    ; Registry entries
    WriteRegStr HKCU "Software\\${{APP_ID}}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_ID}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_ID}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_ID}}" "DisplayVersion" "{VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_ID}}" "Publisher" "${{AUTHOR}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_ID}}" "URLInfoAbout" "${{URL}}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\\${{EXE_NAME}}"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\requirements.txt"
    Delete "$INSTDIR\\Uninstall.exe"
    
    ; Remove directories
    RMDir /r "$INSTDIR\\docs"
    RMDir /r "$INSTDIR\\test_data"
    RMDir "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKCU "Software\\${{APP_ID}}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_ID}}"
SectionEnd
'''
    
    # Write NSIS script
    with open(f"{APP_ID}.nsi", "w") as f:
        f.write(nsis_script)
    
    # Build installer
    try:
        cmd = ["makensis", f"{APP_ID}.nsi"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"NSIS installer created successfully: {APP_ID}-{VERSION}-Setup.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"NSIS build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_zip_distribution():
    """Create a simple ZIP distribution."""
    import zipfile
    
    zip_name = f"{APP_ID}-{VERSION}-Windows.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        exe_path = Path("dist") / f"{APP_ID}.exe"
        if exe_path.exists():
            zipf.write(exe_path, f"{APP_ID}.exe")
        
        # Add documentation
        for file_name in ["README.md", "requirements.txt"]:
            if Path(file_name).exists():
                zipf.write(file_name, file_name)
        
        # Add docs folder
        docs_path = Path("docs")
        if docs_path.exists():
            for file_path in docs_path.rglob("*"):
                if file_path.is_file():
                    zipf.write(file_path, file_path)
        
        # Add test data
        test_data_path = Path("test_data")
        if test_data_path.exists():
            for file_path in test_data_path.rglob("*"):
                if file_path.is_file():
                    zipf.write(file_path, file_path)
        
        # Add installation instructions
        install_txt = f"""File Comparison Tool v{VERSION} - Windows Distribution

INSTALLATION INSTRUCTIONS:
1. Extract all files to your desired location (e.g., C:\\Program Files\\File Comparison Tool\\)
2. Run {APP_ID}.exe to start the application
3. Create a desktop shortcut if desired

SYSTEM REQUIREMENTS:
- Windows 10 or later
- 4GB RAM recommended for large files
- 100MB free disk space

USAGE:
Double-click {APP_ID}.exe to start the File Comparison Tool.
The application provides a step-by-step interface for comparing Excel and CSV files.

For detailed instructions, see the docs folder or visit:
{URL}

SUPPORT:
For support and bug reports, visit:
{URL}/issues
"""
        zipf.writestr("INSTALL.txt", install_txt)
    
    print(f"ZIP distribution created: {zip_name}")
    return True

def create_macos_installer():
    """Create macOS DMG installer."""
    print("Creating macOS installer...")
    
    # Check if we have the executable
    app_path = Path("dist") / f"{APP_ID}.app"
    if not app_path.exists():
        print(f"ERROR: Application bundle not found at {app_path}")
        print("Please run build_executable.py first")
        return False
    
    # Create DMG
    dmg_name = f"{APP_ID}-{VERSION}-macOS.dmg"
    
    try:
        # Create temporary directory for DMG contents
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy app bundle
            shutil.copytree(app_path, temp_path / f"{APP_ID}.app")
            
            # Copy documentation
            for file_name in ["README.md", "requirements.txt"]:
                if Path(file_name).exists():
                    shutil.copy2(file_name, temp_path / file_name)
            
            # Create Applications symlink
            os.symlink("/Applications", temp_path / "Applications")
            
            # Create DMG
            cmd = [
                "hdiutil", "create",
                "-volname", APP_NAME,
                "-srcfolder", str(temp_path),
                "-ov", "-format", "UDZO",
                dmg_name
            ]
            
            subprocess.run(cmd, check=True)
            print(f"DMG installer created: {dmg_name}")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"DMG creation failed: {e}")
        return False

def create_linux_installer():
    """Create Linux distribution package."""
    print("Creating Linux distribution...")
    
    # Create tar.gz distribution
    import tarfile
    
    tar_name = f"{APP_ID}-{VERSION}-Linux.tar.gz"
    
    with tarfile.open(tar_name, "w:gz") as tar:
        # Add executable
        exe_path = Path("dist") / APP_ID
        if exe_path.exists():
            tar.add(exe_path, f"{APP_ID}/{APP_ID}")
        
        # Add documentation
        for file_name in ["README.md", "requirements.txt"]:
            if Path(file_name).exists():
                tar.add(file_name, f"{APP_ID}/{file_name}")
        
        # Add docs and test data
        for dir_name in ["docs", "test_data"]:
            dir_path = Path(dir_name)
            if dir_path.exists():
                tar.add(dir_path, f"{APP_ID}/{dir_name}")
        
        # Add installation script
        install_script = f"""#!/bin/bash
# File Comparison Tool Installation Script

APP_NAME="{APP_ID}"
INSTALL_DIR="/opt/$APP_NAME"
BIN_DIR="/usr/local/bin"

echo "Installing File Comparison Tool v{VERSION}..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy files
cp -r * "$INSTALL_DIR/"

# Make executable
chmod +x "$INSTALL_DIR/$APP_NAME"

# Create symlink in PATH
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_DIR/file-comparison-tool"

# Create desktop entry
cat > /usr/share/applications/file-comparison-tool.desktop << EOF
[Desktop Entry]
Name={APP_NAME}
Comment={DESCRIPTION}
Exec=$INSTALL_DIR/$APP_NAME
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=Office;Utility;
EOF

echo "Installation completed!"
echo "You can now run 'file-comparison-tool' from the command line"
echo "or find it in your applications menu."
"""
        
        # Add install script to tar
        import io
        script_data = install_script.encode('utf-8')
        script_info = tarfile.TarInfo(name=f"{APP_ID}/install.sh")
        script_info.size = len(script_data)
        script_info.mode = 0o755
        tar.addfile(script_info, io.BytesIO(script_data))
    
    print(f"Linux distribution created: {tar_name}")
    return True

def main():
    """Main installer creation process."""
    system = platform.system()
    
    print(f"Creating installer for {system}...")
    print("=" * 50)
    
    success = False
    
    if system == "Windows":
        success = create_windows_installer()
    elif system == "Darwin":
        success = create_macos_installer()
    elif system == "Linux":
        success = create_linux_installer()
    else:
        print(f"Unsupported platform: {system}")
        return 1
    
    if success:
        print("=" * 50)
        print("Installer created successfully!")
        return 0
    else:
        print("Installer creation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())