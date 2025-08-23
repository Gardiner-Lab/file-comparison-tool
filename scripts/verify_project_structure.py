#!/usr/bin/env python3
"""
Project structure verification script for File Comparison Tool.
Ensures all files are properly organized and ready for GitHub upload.
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Check that all required directories exist."""
    print("=== Directory Structure ===")
    
    required_dirs = [
        'src',
        'src/controllers',
        'src/gui', 
        'src/models',
        'src/services',
        'tests',
        'tests/unit',
        'tests/integration',
        'tests/fixes',
        'docs',
        'docs/fixes',
        'docs/development',
        'scripts',
        'build-tools',
        'test_data',
        '.github',
        '.github/workflows'
    ]
    
    all_good = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ (MISSING)")
            all_good = False
    
    return all_good

def check_core_files():
    """Check that core project files exist."""
    print("\n=== Core Project Files ===")
    
    core_files = [
        'main.py',
        'README.md',
        'CHANGELOG.md',
        'LICENSE',
        'requirements.txt',
        'requirements-dev.txt',
        'setup.py',
        'pyproject.toml',
        '.gitignore',
        '.pre-commit-config.yaml',
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
        'MANIFEST.in'
    ]
    
    all_good = True
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MISSING)")
            all_good = False
    
    return all_good

def check_source_files():
    """Check that source code files exist."""
    print("\n=== Source Code Files ===")
    
    source_files = [
        'src/controllers/main_controller.py',
        'src/gui/main_window.py',
        'src/gui/file_selection_panel.py',
        'src/gui/column_mapping_panel.py',
        'src/gui/operation_config_panel.py',
        'src/gui/results_panel.py',
        'src/models/data_models.py',
        'src/services/comparison_engine.py',
        'src/services/file_parser_service.py',
        'src/services/export_service.py',
        'src/services/error_handler.py'
    ]
    
    all_good = True
    for file_path in source_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MISSING)")
            all_good = False
    
    return all_good

def check_build_tools():
    """Check that build tools exist."""
    print("\n=== Build Tools ===")
    
    build_files = [
        'build-tools/build_executable.py',
        'build-tools/build_and_package.py',
        'build-tools/create_installer.py',
        'build-tools/FileComparisonTool.spec'
    ]
    
    all_good = True
    for file_path in build_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MISSING)")
            all_good = False
    
    return all_good

def check_documentation():
    """Check that documentation is complete."""
    print("\n=== Documentation ===")
    
    doc_files = [
        'docs/PROJECT_STRUCTURE.md',
        'docs/BUILD_AND_DEPLOY.md',
        'docs/DEVELOPMENT.md',
        'docs/fixes/README.md'
    ]
    
    all_good = True
    for file_path in doc_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MISSING)")
            all_good = False
    
    return all_good

def check_test_files():
    """Check that test files are properly organized."""
    print("\n=== Test Organization ===")
    
    # Count test files in each directory
    test_dirs = {
        'tests/unit': 'Unit tests',
        'tests/integration': 'Integration tests', 
        'tests/fixes': 'Fix verification tests'
    }
    
    all_good = True
    for test_dir, description in test_dirs.items():
        if os.path.exists(test_dir):
            test_files = list(Path(test_dir).glob('test_*.py'))
            print(f"✓ {description}: {len(test_files)} files in {test_dir}/")
        else:
            print(f"✗ {description}: {test_dir}/ missing")
            all_good = False
    
    return all_good

def check_scripts():
    """Check that utility scripts are organized."""
    print("\n=== Utility Scripts ===")
    
    script_files = [
        'scripts/create_test_files.py',
        'scripts/run_comprehensive_tests.py',
        'scripts/diagnose_tkinter.py'
    ]
    
    all_good = True
    for file_path in script_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"⚠ {file_path} (optional)")
    
    return all_good

def check_no_clutter():
    """Check that root directory is clean."""
    print("\n=== Root Directory Cleanliness ===")
    
    # Files that should NOT be in root
    unwanted_patterns = [
        'test_*.py',
        'debug_*.py', 
        'temp_*.py',
        'scratch_*.py',
        '*.tmp',
        '*.bak',
        'diagnostic_*.py'
    ]
    
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    clutter_found = []
    
    for pattern in unwanted_patterns:
        import fnmatch
        matches = fnmatch.filter(root_files, pattern)
        clutter_found.extend(matches)
    
    if clutter_found:
        print("⚠ Found files that should be moved:")
        for file in clutter_found:
            print(f"  - {file}")
        return False
    else:
        print("✓ Root directory is clean")
        return True

def check_git_readiness():
    """Check if project is ready for git."""
    print("\n=== Git Readiness ===")
    
    # Check .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            if len(gitignore_content.strip()) > 0:
                print("✓ .gitignore exists and has content")
            else:
                print("✗ .gitignore is empty")
                return False
    else:
        print("✗ .gitignore missing")
        return False
    
    # Check for git repository
    if os.path.exists('.git'):
        print("✓ Git repository initialized")
    else:
        print("⚠ Git repository not initialized (run 'git init')")
    
    return True

def main():
    """Main verification function."""
    print("File Comparison Tool - Project Structure Verification")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Core Project Files", check_core_files),
        ("Source Code Files", check_source_files),
        ("Build Tools", check_build_tools),
        ("Documentation", check_documentation),
        ("Test Organization", check_test_files),
        ("Utility Scripts", check_scripts),
        ("Root Directory Cleanliness", check_no_clutter),
        ("Git Readiness", check_git_readiness)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"✗ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{check_name:<30} | {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 PROJECT STRUCTURE IS PROPERLY ORGANIZED!")
        print("\nProject is ready for GitHub upload:")
        print("1. git init (if not already done)")
        print("2. git add .")
        print("3. git commit -m 'Initial commit'")
        print("4. git remote add origin <your-repo-url>")
        print("5. git push -u origin main")
    else:
        print("❌ PROJECT NEEDS ORGANIZATION")
        print("\nPlease fix the issues above before uploading to GitHub.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())