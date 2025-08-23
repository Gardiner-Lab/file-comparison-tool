# Development Guide

## Project Structure

```
excel-manager/
├── src/                          # Source code
│   ├── controllers/              # Application controllers
│   ├── gui/                      # GUI components
│   ├── models/                   # Data models
│   └── services/                 # Business logic services
├── tests/                        # Unit and integration tests
├── test_data/                    # Sample data for testing
├── docs/                         # Documentation
├── .kiro/                        # Kiro IDE specifications
└── fixes/                        # Bug fix documentation and tests
```

## Recent Fixes and Improvements

This project has undergone significant improvements to fix critical issues:

### 1. Initial Panel Display Issues
- **Problem**: Panels not displaying correctly on startup
- **Solution**: Fixed initialization sequence and panel display logic
- **Files**: See `.kiro/specs/fix-initial-panel-display/`

### 2. TypeError Fixes
- **Problem**: Multiple TypeError issues preventing operation
- **Solution**: Fixed method signatures and data type handling
- **Documentation**: `fixes/additional_errors_fix_summary.md`

### 3. Results Display Fix
- **Problem**: Comparison results not showing in results window
- **Solution**: Fixed method calls and state transitions
- **Documentation**: `fixes/results_display_complete_fix_summary.md`

## Development Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Run Tests**:
   ```bash
   # Run all tests
   python -m pytest tests/
   
   # Run specific fix verification tests
   python fixes/test_additional_errors_verification.py
   python fixes/test_correct_state_transition_fix.py
   ```

## Testing

### Test Categories

1. **Unit Tests**: Located in `tests/` directory
2. **Integration Tests**: Test complete workflows
3. **Fix Verification Tests**: Located in `fixes/` directory

### Key Test Files

- `tests/test_startup_sequence_integration.py` - Startup sequence tests
- `fixes/test_additional_errors_verification.py` - TypeError fix verification
- `fixes/test_correct_state_transition_fix.py` - State transition fix verification

## Building and Packaging

1. **Create Executable**:
   ```bash
   python build_executable.py
   ```

2. **Create Installer**:
   ```bash
   python create_installer.py
   ```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Run all tests before submitting

See `CONTRIBUTING.md` for detailed guidelines.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **GUI Issues**: Check tkinter installation
3. **File Loading Issues**: Verify pandas and openpyxl are installed

### Debug Tools

- `debug_main.py` - Main application debugging
- `diagnose_tkinter.py` - GUI diagnostics
- Various test files for component testing

## Architecture

The application follows an MVC pattern:

- **Models**: Data structures and validation
- **Views**: GUI components and panels
- **Controllers**: Business logic and coordination
- **Services**: Utility services (file parsing, comparison, export)

## Recent Improvements

All major issues have been resolved:
- ✅ Panel initialization and display
- ✅ TypeError fixes
- ✅ Results display functionality
- ✅ State management
- ✅ Error handling

The application is now fully functional and ready for production use.