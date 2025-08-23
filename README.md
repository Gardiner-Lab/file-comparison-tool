# File Comparison Tool

A powerful desktop application for comparing Excel and CSV files with an intuitive graphical user interface. Perform various set operations on your data files including removing duplicates, finding common values, and identifying unique entries.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Features

- **Multi-format Support**: Works with Excel (.xlsx, .xls) and CSV files
- **Intuitive GUI**: Step-by-step workflow with visual feedback
- **Multiple Operations**: 
  - Remove matches between files
  - Keep only matching entries
  - Find common values
  - Identify unique values
- **Column Mapping**: Smart column selection with data type validation
- **Export Options**: Save results as CSV or Excel files
- **Performance Optimized**: Handles large files efficiently with progress indicators
- **Error Handling**: Comprehensive error messages and recovery options
- **Help System**: Built-in tooltips and user guidance

## Screenshots

*Screenshots will be added here to showcase the application interface*

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/yourusername/file-comparison-tool.git
cd file-comparison-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### Alternative Installation Methods

#### Using pip (when published to PyPI)
```bash
pip install file-comparison-tool
```

#### Using setup.py
```bash
python setup.py install
```

## Usage

### Basic Workflow

1. **Launch the Application**
   ```bash
   python main.py
   ```

2. **Select Files**
   - Click "Browse" to select your first file (Excel or CSV)
   - Click "Browse" to select your second file
   - Preview the first few rows of each file

3. **Map Columns**
   - Choose which columns to compare from each file
   - Verify data compatibility with the sample preview

4. **Configure Operation**
   - Select your desired operation:
     - **Remove Matches**: Remove rows from file 2 that match file 1
     - **Keep Only Matches**: Keep only matching rows from file 2
     - **Find Common Values**: Create new file with common entries
     - **Find Unique Values**: Create new file with unique entries

5. **Export Results**
   - Choose output format (CSV or Excel)
   - Save your processed file
   - Review the operation summary

### Command Line Usage

For advanced users, the application can be run with command-line arguments:

```bash
python main.py --file1 data1.csv --file2 data2.xlsx --operation remove_matches --output result.csv
```

### Example Use Cases

#### Email List Deduplication
Remove email addresses from a subscriber list that already exist in your customer database:
- File 1: customer_database.xlsx (column: "email")
- File 2: new_subscribers.csv (column: "email_address")
- Operation: Remove Matches
- Result: Clean subscriber list without existing customers

#### Finding Common Customers
Identify customers who appear in both your online and offline sales data:
- File 1: online_sales.csv (column: "customer_id")
- File 2: offline_sales.xlsx (column: "customer_id")
- Operation: Find Common Values
- Result: List of customers who shop both online and offline

## Development

### Project Structure

```
file-comparison-tool/
├── src/
│   ├── controllers/          # Application controllers
│   ├── gui/                  # GUI components
│   ├── models/              # Data models
│   └── services/            # Business logic services
├── tests/                   # Test suite
├── docs/                    # Documentation
├── test_data/              # Sample test files
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── setup.py               # Package configuration
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_comparison_engine.py
python -m pytest tests/test_gui_automation.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Building Executable

Create a standalone executable for distribution:

```bash
python build_executable.py
```

The executable will be created in the `dist/` directory.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python -m pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: Check the [docs/](docs/) directory for detailed guides
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/Gardiner-Lab/file-comparison-tool/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/Gardiner-Lab/file-comparison-tool/discussions)

## Changelog

### Version 1.0.0
- Initial release
- Support for Excel and CSV file comparison
- Four comparison operations (remove, keep, common, unique)
- Intuitive GUI with step-by-step workflow
- Performance optimization for large files
- Comprehensive error handling and help system

## Acknowledgments

- Built with [pandas](https://pandas.pydata.org/) for data processing
- GUI powered by [tkinter](https://docs.python.org/3/library/tkinter.html)
- Excel support via [openpyxl](https://openpyxl.readthedocs.io/)

---

**Made with ❤️ for data analysts and anyone who works with spreadsheets**