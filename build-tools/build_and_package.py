#!/usr/bin/env python3
"""
Complete build and packaging script for File Comparison Tool.

This script orchestrates the entire build and packaging process:
1. Builds the standalone executable
2. Creates distribution packages
3. Creates installers
4. Tests deployment
5. Generates final distribution artifacts
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import time

def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print('='*50)
    
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=check, text=True)
        else:
            result = subprocess.run(cmd, check=check, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False
    except Exception as e:
        print(f"❌ {description} failed with error: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are available."""
    print("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required packages
    required_packages = ['pandas', 'openpyxl', 'tkinter']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    if missing_packages:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # Check if PyInstaller is available for building
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
        print("✅ PyInstaller available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  PyInstaller not found - will install automatically")
    
    return True

def install_build_dependencies():
    """Install build dependencies."""
    print("\nInstalling build dependencies...")
    
    build_deps = ['pyinstaller>=5.0.0', 'auto-py-to-exe>=2.20.0']
    
    for dep in build_deps:
        if not run_command([sys.executable, '-m', 'pip', 'install', dep], 
                          f"Installing {dep}", check=False):
            print(f"⚠️  Failed to install {dep}, continuing anyway...")

def clean_previous_builds():
    """Clean up previous build artifacts."""
    print("\nCleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec', '*.pyc', '*.pyo']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            file_path.unlink()
            print(f"Removed {file_path}")

def build_executable():
    """Build the standalone executable."""
    return run_command([sys.executable, 'build_executable.py'], 
                      "Building standalone executable")

def create_installers():
    """Create platform-specific installers."""
    return run_command([sys.executable, 'create_installer.py'], 
                      "Creating installers")

def test_deployment():
    """Test the deployment."""
    return run_command([sys.executable, 'test_deployment.py'], 
                      "Testing deployment", check=False)

def create_source_distribution():
    """Create source distribution."""
    print("\nCreating source distribution...")
    
    # Create sdist
    if not run_command([sys.executable, 'setup.py', 'sdist'], 
                      "Creating source distribution", check=False):
        return False
    
    # Create wheel
    if not run_command([sys.executable, 'setup.py', 'bdist_wheel'], 
                      "Creating wheel distribution", check=False):
        return False
    
    return True

def generate_checksums():
    """Generate checksums for all distribution files."""
    print("\nGenerating checksums...")
    
    import hashlib
    
    # Find all distribution files
    dist_files = []
    
    # Executables and packages
    patterns = [
        '*.exe', '*.dmg', '*.tar.gz', '*.zip',
        'dist/*.whl', 'dist/*.tar.gz'
    ]
    
    for pattern in patterns:
        dist_files.extend(Path('.').glob(pattern))
    
    if not dist_files:
        print("No distribution files found to checksum")
        return False
    
    # Generate checksums
    checksums = {}
    
    for file_path in dist_files:
        if file_path.is_file():
            with open(file_path, 'rb') as f:
                content = f.read()
                sha256_hash = hashlib.sha256(content).hexdigest()
                checksums[str(file_path)] = {
                    'sha256': sha256_hash,
                    'size': len(content)
                }
    
    # Write checksums file
    with open('CHECKSUMS.txt', 'w') as f:
        f.write(f"File Comparison Tool v1.0.0 - Distribution Checksums\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write(f"Platform: {platform.system()} {platform.machine()}\n\n")
        
        for file_path, info in checksums.items():
            f.write(f"File: {file_path}\n")
            f.write(f"Size: {info['size']} bytes\n")
            f.write(f"SHA256: {info['sha256']}\n\n")
    
    print(f"✅ Generated checksums for {len(checksums)} files")
    return True

def create_release_notes():
    """Create release notes."""
    release_notes = f"""# File Comparison Tool v1.0.0 Release Notes

## Release Information
- **Version**: 1.0.0
- **Release Date**: {time.strftime('%Y-%m-%d', time.gmtime())}
- **Platform**: {platform.system()} {platform.machine()}

## What's New
This is the initial release of the File Comparison Tool, a GUI application for comparing Excel and CSV files.

### Features
- **File Support**: Excel (.xlsx, .xls) and CSV (.csv) files
- **Comparison Operations**:
  - Remove matches: Remove rows from file 2 that match file 1
  - Keep only matches: Keep only rows from file 2 that match file 1
  - Find common values: Create file with rows that exist in both files
  - Find unique values: Create file with rows that exist in only one file
- **User-Friendly GUI**: Step-by-step interface with progress indicators
- **Performance Optimized**: Handles large files efficiently with chunked processing
- **Comprehensive Help**: Built-in help system with tooltips and documentation
- **Error Handling**: Robust error handling with user-friendly messages

### System Requirements
- **Windows**: Windows 10 or later (64-bit recommended)
- **macOS**: macOS 10.14 or later
- **Linux**: Most modern distributions with GUI support
- **Memory**: 4GB RAM recommended for large files
- **Storage**: 100MB free disk space

### Installation
1. Download the appropriate package for your platform
2. Extract/install according to platform instructions
3. Run the application executable
4. No additional dependencies required - all libraries are bundled

### Usage
1. Start the application
2. Select your two files to compare
3. Choose which columns to compare
4. Select the comparison operation
5. Configure output options
6. Export your results

### Support
- Documentation: See the included docs folder
- Issues: Report bugs and request features on GitHub
- Community: Join discussions on GitHub

## Distribution Files
The following files are included in this release:

### Windows
- `FileComparisonTool-1.0.0-Setup.exe` - Windows installer
- `FileComparisonTool-1.0.0-Windows.zip` - Portable Windows version

### macOS
- `FileComparisonTool-1.0.0-macOS.dmg` - macOS installer

### Linux
- `FileComparisonTool-1.0.0-Linux.tar.gz` - Linux distribution

### Source
- `file-comparison-tool-1.0.0.tar.gz` - Source distribution
- `file_comparison_tool-1.0.0-py3-none-any.whl` - Python wheel

## Verification
All distribution files include SHA256 checksums in `CHECKSUMS.txt` for verification.

## License
This software is released under the MIT License. See LICENSE file for details.

## Acknowledgments
Built with Python, tkinter, pandas, and openpyxl.
"""
    
    with open('RELEASE_NOTES.md', 'w') as f:
        f.write(release_notes)
    
    print("✅ Created release notes")
    return True

def main():
    """Main build and packaging process."""
    print("File Comparison Tool - Build and Package Script")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed!")
        return 1
    
    # Step 2: Install build dependencies
    install_build_dependencies()
    
    # Step 3: Clean previous builds
    clean_previous_builds()
    
    # Step 4: Build executable
    if not build_executable():
        print("❌ Executable build failed!")
        return 1
    
    # Step 5: Create installers
    if not create_installers():
        print("⚠️  Installer creation failed, but continuing...")
    
    # Step 6: Create source distribution
    if not create_source_distribution():
        print("⚠️  Source distribution creation failed, but continuing...")
    
    # Step 7: Test deployment
    if not test_deployment():
        print("⚠️  Deployment tests failed, but continuing...")
    
    # Step 8: Generate checksums
    if not generate_checksums():
        print("⚠️  Checksum generation failed, but continuing...")
    
    # Step 9: Create release notes
    if not create_release_notes():
        print("⚠️  Release notes creation failed, but continuing...")
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("BUILD AND PACKAGE SUMMARY")
    print("=" * 60)
    print(f"Total time: {duration:.1f} seconds")
    
    # List created files
    print("\nCreated files:")
    patterns = ['*.exe', '*.dmg', '*.tar.gz', '*.zip', 'dist/*', '*.txt', '*.md']
    created_files = []
    
    for pattern in patterns:
        created_files.extend(Path('.').glob(pattern))
    
    for file_path in sorted(set(created_files)):
        if file_path.is_file():
            size = file_path.stat().st_size
            print(f"  {file_path} ({size:,} bytes)")
    
    print("\n✅ Build and packaging completed!")
    print("\nNext steps:")
    print("1. Test the executable on target systems")
    print("2. Verify checksums match")
    print("3. Upload to distribution channels")
    print("4. Update documentation and release notes")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())