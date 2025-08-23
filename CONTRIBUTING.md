# Contributing to File Comparison Tool

Thank you for your interest in contributing to the File Comparison Tool! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Code Style](#code-style)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python, pandas, and tkinter
- Familiarity with GUI application development (helpful but not required)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/file-comparison-tool.git
   cd file-comparison-tool
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Verify Installation**
   ```bash
   python main.py  # Should launch the application
   python -m pytest tests/  # Should run all tests
   ```

5. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix issues reported in GitHub Issues
- **Feature Enhancements**: Add new functionality or improve existing features
- **Documentation**: Improve README, code comments, or user guides
- **Testing**: Add test cases or improve test coverage
- **Performance**: Optimize code for better performance
- **UI/UX**: Improve the user interface and user experience

### Before You Start

1. **Check Existing Issues**: Look for existing issues or discussions about your proposed change
2. **Create an Issue**: For significant changes, create an issue to discuss the approach first
3. **Small Changes**: For small bug fixes or documentation updates, you can proceed directly with a PR

## Pull Request Process

### 1. Prepare Your Changes

- Ensure your code follows the project's coding standards
- Add or update tests for your changes
- Update documentation if necessary
- Test your changes thoroughly

### 2. Commit Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Fix column mapping validation for empty files"
git commit -m "Add progress indicator for large file processing"
git commit -m "Update README with installation instructions"

# Avoid
git commit -m "Fix bug"
git commit -m "Update stuff"
```

### 3. Submit Pull Request

1. Push your branch to your fork
2. Create a pull request from your branch to the main repository
3. Fill out the pull request template completely
4. Link any related issues

### 4. Pull Request Review

- Maintainers will review your PR and may request changes
- Address feedback promptly and push updates to your branch
- Once approved, your PR will be merged

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_comparison_engine.py

# Run with coverage report
python -m pytest --cov=src tests/

# Run GUI tests (may require display)
python -m pytest tests/test_gui_automation.py
```

### Writing Tests

- Add unit tests for new functions and classes
- Include integration tests for complex workflows
- Test edge cases and error conditions
- Use descriptive test names that explain what is being tested

Example test structure:
```python
def test_remove_matches_with_empty_file():
    """Test remove_matches operation when one file is empty."""
    # Arrange
    engine = ComparisonEngine()
    df1 = pd.DataFrame({'email': []})
    df2 = pd.DataFrame({'email': ['test@example.com']})
    
    # Act
    result = engine.remove_matches(df1, df2, 'email')
    
    # Assert
    assert len(result) == 1
    assert result.iloc[0]['email'] == 'test@example.com'
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **GUI Tests**: Test user interface components
- **Performance Tests**: Test with large datasets
- **Error Handling Tests**: Test error conditions and recovery

## Code Style

### Python Style Guidelines

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and reasonably sized
- Use type hints where appropriate

### Code Formatting

We use the following tools for code formatting:

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check style with flake8
flake8 src/ tests/
```

### Documentation Style

- Use clear, concise docstrings
- Include parameter and return type information
- Provide usage examples for complex functions

Example:
```python
def compare_files(file1_path: str, file2_path: str, operation: str) -> pd.DataFrame:
    """
    Compare two files using the specified operation.
    
    Args:
        file1_path: Path to the first file
        file2_path: Path to the second file
        operation: Type of comparison ('remove_matches', 'keep_matches', etc.)
    
    Returns:
        DataFrame containing the comparison results
    
    Raises:
        FileNotFoundError: If either file doesn't exist
        ValueError: If operation type is not supported
    
    Example:
        >>> result = compare_files('data1.csv', 'data2.csv', 'remove_matches')
        >>> print(len(result))
        150
    """
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, application version
- **Files**: Sample files that demonstrate the issue (if applicable)
- **Screenshots**: Screenshots of error messages or unexpected behavior

### Feature Requests

For feature requests, please include:

- **Description**: Clear description of the proposed feature
- **Use Case**: Why this feature would be useful
- **Proposed Solution**: Your ideas for how it could be implemented
- **Alternatives**: Alternative solutions you've considered

## Development Tips

### Project Architecture

The project follows an MVC (Model-View-Controller) pattern:

- **Models** (`src/models/`): Data structures and business objects
- **Views** (`src/gui/`): User interface components
- **Controllers** (`src/controllers/`): Application logic and coordination
- **Services** (`src/services/`): Business logic and data processing

### Adding New Features

1. **Plan the Feature**: Consider how it fits into the existing architecture
2. **Update Models**: Add or modify data models if needed
3. **Implement Services**: Add business logic in the services layer
4. **Update GUI**: Modify or add GUI components
5. **Wire Controllers**: Connect GUI events to business logic
6. **Add Tests**: Ensure comprehensive test coverage
7. **Update Documentation**: Update user guides and code documentation

### Debugging Tips

- Use the built-in logging system for debugging
- Test with various file formats and sizes
- Use the test data in `test_data/` directory for consistent testing
- Run the application with `python main.py --debug` for verbose output

## Getting Help

- **Documentation**: Check the `docs/` directory for detailed guides
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Code Review**: Don't hesitate to ask for feedback on your approach

## Recognition

Contributors will be recognized in the project's acknowledgments. Significant contributors may be invited to become maintainers.

Thank you for contributing to the File Comparison Tool! 🎉