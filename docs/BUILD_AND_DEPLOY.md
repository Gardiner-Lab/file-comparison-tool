# Build and Deployment Guide

This guide covers building, packaging, and deploying the File Comparison Tool.

## Quick Start

### Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/file-comparison-tool.git
cd file-comparison-tool

# Install dependencies
pip install -r requirements-dev.txt

# Run the application
python main.py

# Run tests
pytest tests/
```

### Building Executable
```bash
# Build standalone executable
python build-tools/build_executable.py

# The executable will be in dist/
```

## Development Environment

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git for version control

### Installing Dependencies

#### Production Dependencies
```bash
pip install -r requirements.txt
```

#### Development Dependencies
```bash
pip install -r requirements-dev.txt
```

This includes:
- pytest for testing
- black for code formatting
- flake8 for linting
- mypy for type checking
- pre-commit for git hooks

### Pre-commit Hooks
Set up pre-commit hooks for code quality:
```bash
pre-commit install
```

This will automatically:
- Format code with black
- Lint with flake8
- Check type hints with mypy
- Validate commit messages

## Testing

### Running Tests

#### All Tests
```bash
# Using pytest
pytest tests/

# Using custom test runner
python scripts/run_comprehensive_tests.py
```

#### Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Fix verification tests
pytest tests/fixes/
```

#### Test Coverage
```bash
# Run with coverage report
pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Test Data
Sample test files are provided in `test_data/`:
- `test_file1.csv` - Sample CSV file
- `test_file2.csv` - Sample CSV file

Create additional test files:
```bash
python scripts/create_test_files.py
python scripts/create_performance_test_files.py
```

## Building

### Standalone Executable

#### Using PyInstaller (Recommended)
```bash
# Build executable with custom script
python build-tools/build_executable.py

# Or use PyInstaller directly
pyinstaller build-tools/FileComparisonTool.spec
```

The executable will be created in `dist/FileComparisonTool/` or `dist/FileComparisonTool.exe`.

#### Build Options
- **One-file**: Single executable file (slower startup)
- **One-dir**: Directory with executable and dependencies (faster startup)
- **Console**: Shows console window for debugging
- **Windowed**: No console window (production)

### Python Package

#### Source Distribution
```bash
python setup.py sdist
```

#### Wheel Distribution
```bash
python setup.py bdist_wheel
```

#### Using build (Modern approach)
```bash
pip install build
python -m build
```

### Installer Creation

#### Windows Installer
```bash
python build-tools/create_installer.py
```

This creates an NSIS-based installer for Windows.

#### macOS App Bundle
```bash
# Requires macOS
python build-tools/build_executable.py --platform=macos
```

#### Linux Package
```bash
# Creates .deb package
python build-tools/build_executable.py --platform=linux
```

## Deployment

### GitHub Releases

#### Automated Release (GitHub Actions)
The project includes GitHub Actions workflows for automated building and releasing:

1. **On Push to Main**: Runs tests and builds
2. **On Tag**: Creates release with executables
3. **On Pull Request**: Runs tests and validation

#### Manual Release
1. Tag the release:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. Create release on GitHub with built executables

### Distribution Channels

#### GitHub Releases
- Source code (automatic)
- Windows executable
- macOS app bundle
- Linux executable

#### PyPI (Future)
```bash
# Build and upload to PyPI
python -m build
twine upload dist/*
```

#### Package Managers
- **Windows**: Chocolatey package
- **macOS**: Homebrew formula
- **Linux**: APT/RPM packages

## Configuration

### Build Configuration

#### PyInstaller Spec File
The `build-tools/FileComparisonTool.spec` file controls the build process:

```python
# Key configuration options
a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
```

#### Setup.py Configuration
The `setup.py` file defines package metadata:

```python
setup(
    name="file-comparison-tool",
    version="1.0.0",
    description="A comprehensive GUI application for comparing Excel and CSV files",
    # ... other metadata
)
```

### Environment Variables

#### Build Environment
- `BUILD_VERSION`: Override version number
- `BUILD_TYPE`: Set to 'release' for production builds
- `PYTHON_PATH`: Custom Python path for building

#### Runtime Environment
- `FCT_DEBUG`: Enable debug mode
- `FCT_LOG_LEVEL`: Set logging level
- `FCT_CONFIG_PATH`: Custom configuration directory

## Troubleshooting

### Common Build Issues

#### Missing Dependencies
```bash
# Install all dependencies
pip install -r requirements-dev.txt

# Update pip and setuptools
pip install --upgrade pip setuptools wheel
```

#### PyInstaller Issues
```bash
# Clear PyInstaller cache
pyinstaller --clean build-tools/FileComparisonTool.spec

# Verbose output for debugging
pyinstaller --log-level=DEBUG build-tools/FileComparisonTool.spec
```

#### Import Errors
Add missing modules to `hiddenimports` in the spec file:
```python
hiddenimports=['pandas', 'openpyxl', 'tkinter'],
```

### Platform-Specific Issues

#### Windows
- Ensure Visual C++ Redistributable is installed
- Use Windows Defender exclusions for build directory
- Run as administrator if permission issues occur

#### macOS
- Install Xcode command line tools
- Sign the application for distribution
- Handle Gatekeeper restrictions

#### Linux
- Install system dependencies (python3-tk, etc.)
- Handle different distribution package managers
- Consider AppImage for universal distribution

### Performance Optimization

#### Build Performance
- Use SSD for build directory
- Exclude unnecessary files in .gitignore
- Use parallel builds when possible

#### Runtime Performance
- Profile the application with cProfile
- Optimize data processing algorithms
- Use appropriate data structures

## Continuous Integration

### GitHub Actions Workflow

The `.github/workflows/ci.yml` file defines the CI/CD pipeline:

1. **Test Matrix**: Tests on multiple Python versions and platforms
2. **Code Quality**: Linting, formatting, and type checking
3. **Security**: Dependency vulnerability scanning
4. **Build**: Creates executables for all platforms
5. **Release**: Publishes releases on tags

### Local CI Testing
```bash
# Install act to run GitHub Actions locally
# https://github.com/nektos/act

# Run the workflow locally
act push
```

## Security Considerations

### Code Signing
- **Windows**: Use Authenticode signing
- **macOS**: Use Apple Developer ID
- **Linux**: Use GPG signing

### Dependency Security
```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip-compile --upgrade requirements.in
```

### Distribution Security
- Use HTTPS for all downloads
- Provide checksums for releases
- Sign release artifacts

## Monitoring and Analytics

### Error Reporting
Consider integrating error reporting services:
- Sentry for error tracking
- Application Insights for telemetry
- Custom logging for debugging

### Usage Analytics
- Respect user privacy
- Provide opt-out mechanisms
- Follow GDPR/privacy regulations

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Run security scans
- Update documentation
- Review and merge pull requests

### Version Management
- Follow semantic versioning (SemVer)
- Maintain changelog
- Tag releases consistently
- Provide migration guides for breaking changes

### Support
- Monitor GitHub issues
- Respond to user feedback
- Maintain compatibility with new Python versions
- Update for new operating system versions