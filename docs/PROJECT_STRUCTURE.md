# Project Structure

This document describes the organization and architecture of the File Comparison Tool project.

## Directory Structure

```
file-comparison-tool/
├── .github/                    # GitHub configuration
│   └── workflows/              # CI/CD workflows
├── build-tools/                # Build and packaging scripts
│   ├── build_and_package.py    # Main build script
│   ├── build_executable.py     # Executable builder
│   ├── create_installer.py     # Installer creator
│   └── FileComparisonTool.spec # PyInstaller spec
├── docs/                       # Documentation
│   ├── development/            # Development documentation
│   ├── fixes/                  # Bug fix documentation
│   ├── DEVELOPMENT.md          # Development guide
│   └── PROJECT_STRUCTURE.md    # This file
├── scripts/                    # Utility and development scripts
│   ├── create_performance_test_files.py
│   ├── create_test_files.py
│   ├── diagnose_tkinter.py
│   ├── diagnostic_*.py
│   ├── fix_panel_display.py
│   ├── main_*.py              # Various main file versions
│   ├── run_*.py               # Test runners
│   └── simple_file_tool.py
├── src/                        # Source code
│   ├── controllers/            # Application controllers
│   │   └── main_controller.py
│   ├── gui/                    # GUI components
│   │   ├── main_window.py
│   │   ├── file_selection_panel.py
│   │   ├── column_mapping_panel.py
│   │   ├── operation_config_panel.py
│   │   ├── results_panel.py
│   │   └── progress_dialog.py
│   ├── models/                 # Data models
│   │   └── data_models.py
│   └── services/               # Business logic services
│       ├── comparison_engine.py
│       ├── file_parser_service.py
│       ├── export_service.py
│       ├── error_handler.py
│       ├── performance_optimizer.py
│       └── help_service.py
├── test_data/                  # Sample test files
│   ├── test_file1.csv
│   └── test_file2.csv
├── tests/                      # Test suite
│   ├── fixes/                  # Fix verification tests
│   ├── integration/            # Integration tests
│   ├── unit/                   # Unit tests
│   └── test_*.py              # Various test files
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                    # Package setup
├── pyproject.toml             # Modern Python packaging
├── MANIFEST.in                # Package manifest
├── .pre-commit-config.yaml    # Pre-commit hooks
├── README.md                   # Main documentation
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT license
├── CONTRIBUTING.md             # Contribution guidelines
├── CODE_OF_CONDUCT.md         # Code of conduct
└── .gitignore                 # Git ignore rules
```

## Architecture Overview

### MVC Pattern
The application follows the Model-View-Controller (MVC) architectural pattern:

- **Model** (`src/models/`): Data structures, enums, and business objects
- **View** (`src/gui/`): User interface components and panels
- **Controller** (`src/controllers/`): Application logic and coordination

### Service Layer
Business logic is organized into services (`src/services/`):

- **ComparisonEngine**: Core comparison algorithms and operations
- **FileParserService**: File reading, parsing, and validation
- **ExportService**: Result export functionality
- **ErrorHandler**: Centralized error handling and user messaging
- **PerformanceOptimizer**: Memory and performance optimizations
- **HelpService**: Help text and documentation

### GUI Components
User interface is built with tkinter and organized into panels:

- **MainWindow**: Application shell and navigation
- **FileSelectionPanel**: File selection and validation
- **ColumnMappingPanel**: Column selection and mapping
- **OperationConfigPanel**: Operation configuration and preview
- **ResultsPanel**: Results display and export
- **ProgressDialog**: Progress tracking and cancellation

## Key Design Principles

### Separation of Concerns
- Each component has a single, well-defined responsibility
- Business logic is separated from UI logic
- Data access is abstracted through services

### Event-Driven Architecture
- GUI components communicate through events and callbacks
- Loose coupling between components
- Asynchronous operations for better user experience

### Error Handling
- Centralized error handling through ErrorHandler service
- User-friendly error messages
- Graceful degradation and recovery

### Performance Optimization
- Chunked processing for large datasets
- Memory-efficient operations
- Progress tracking and cancellation support

### Testability
- Modular design enables unit testing
- Dependency injection for mocking
- Comprehensive test coverage

## Data Flow

1. **File Selection**: User selects files → FileParserService validates → FileSelectionPanel updates
2. **Column Mapping**: User maps columns → ColumnMappingPanel validates → Controller updates state
3. **Operation Config**: User configures operation → OperationConfigPanel validates → Controller prepares
4. **Execution**: Controller → ComparisonEngine → PerformanceOptimizer → Results
5. **Results Display**: Results → ResultsPanel → User interaction → ExportService

## State Management

The application uses a workflow state machine:

```python
class WorkflowState(Enum):
    FILE_SELECTION = 0
    COLUMN_MAPPING = 1
    OPERATION_CONFIG = 2
    RESULTS = 3
```

State transitions are managed by the MainController with validation at each step.

## Build and Deployment

### Development Environment
- **Scripts**: Development and debugging utilities in `scripts/`
- **Build Tools**: Packaging and distribution tools in `build-tools/`
- **Tests**: Comprehensive test suite in `tests/`

### Build Process
1. **Development**: Use `main.py` for development and testing
2. **Testing**: Run test suite with `pytest` or custom runners
3. **Building**: Use `build_executable.py` to create standalone executable
4. **Packaging**: Use `build_and_package.py` for distribution packages
5. **Installation**: Use `create_installer.py` for installer creation

### Distribution
- **Source**: Available via GitHub repository
- **Executable**: Standalone executable for end users
- **Package**: Python package for developers (future PyPI release)

## Extension Points

### Adding New File Formats
1. Extend FileParserService with new format support
2. Update file selection validation
3. Add format-specific error handling

### Adding New Operations
1. Implement operation in ComparisonEngine
2. Add configuration options in OperationConfigPanel
3. Update operation validation and preview

### Adding New Export Formats
1. Extend ExportService with new format
2. Update ResultsPanel export options
3. Add format-specific validation

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock dependencies for focused testing
- Cover edge cases and error conditions

### Integration Tests
- Test component interactions
- Validate workflow scenarios
- Test end-to-end functionality

### Fix Verification Tests
- Specific tests for bug fixes in `tests/fixes/`
- Regression testing for known issues
- Validation of fix effectiveness

### Performance Tests
- Test with large datasets
- Memory usage validation
- Performance benchmarking

## Development Workflow

### Setting Up Development Environment
1. Clone repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Run tests: `pytest tests/`
4. Start development: `python main.py`

### Code Quality
- **Pre-commit hooks**: Automated code formatting and linting
- **Type hints**: Use type annotations for better code clarity
- **Documentation**: Maintain comprehensive docstrings
- **Testing**: Write tests for new features and bug fixes

### Contributing
1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Run full test suite
5. Submit pull request

## Deployment Considerations

### Dependencies
- Python 3.8+ required
- pandas for data manipulation
- openpyxl for Excel file support
- tkinter for GUI (usually included with Python)

### Cross-Platform Support
- Windows: Native executable via PyInstaller
- macOS: App bundle creation supported
- Linux: Executable and package distribution

### Performance
- Optimized for large file handling
- Memory-efficient processing
- Progress tracking for user feedback