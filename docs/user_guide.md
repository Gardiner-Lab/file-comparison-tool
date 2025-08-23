# File Comparison Tool - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Step-by-Step Workflow](#step-by-step-workflow)
3. [Operation Types Explained](#operation-types-explained)
4. [Tips and Best Practices](#tips-and-best-practices)
5. [Troubleshooting](#troubleshooting)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Frequently Asked Questions](#frequently-asked-questions)

## Getting Started

### System Requirements
- Windows, macOS, or Linux operating system
- Python 3.7 or higher (if running from source)
- Sufficient disk space for your data files and results

### Supported File Formats
- **CSV files** (.csv) - Comma-separated values
- **Excel files** (.xlsx, .xls) - Microsoft Excel format

### First Launch
1. Launch the File Comparison Tool
2. You'll see a clean interface with four main steps
3. Follow the step-by-step workflow from left to right
4. Use the Help menu or F1 key for assistance at any time

## Step-by-Step Workflow

### Step 1: File Selection

**Purpose**: Choose the two files you want to compare.

**How to do it**:
1. Click "Browse..." for File 1 and select your first file
2. Click "Browse..." for File 2 and select your second file
3. Review the file information and preview to ensure files loaded correctly

**What to look for**:
- ✅ Green checkmark = File loaded successfully
- ❌ Red X = File has errors or is unsupported
- File preview shows the first 10 rows of your data
- File information displays type, size, columns, and row count

**Tips**:
- Ensure your files have column headers in the first row
- CSV files should use comma separators
- Large files may take a moment to load

### Step 2: Column Mapping

**Purpose**: Select which columns from each file you want to compare.

**How to do it**:
1. Use the dropdown for File 1 to select a comparison column
2. Use the dropdown for File 2 to select a comparison column
3. Review the compatibility indicator and sample matching values

**What to look for**:
- ✅ Green checkmark = Compatible data types
- ⚠️ Orange warning = Mixed types (will compare as text)
- ❌ Red X = Incompatible types
- Sample matching values show what will be compared

**Best columns to choose**:
- Email addresses
- ID numbers or codes
- Product SKUs
- Customer numbers
- Any column with consistent, comparable data

**Avoid**:
- Columns with mostly unique values (like names or descriptions)
- Columns with inconsistent formatting
- Empty or mostly empty columns

### Step 3: Operation Configuration

**Purpose**: Choose what type of comparison operation to perform.

**Available Operations**:

#### Remove Matches
- **What it does**: Removes rows from File 2 that have matching values in File 1
- **Example**: Remove existing customers from a new prospect list
- **Result**: File 2 with matching rows removed

#### Keep Only Matches
- **What it does**: Keeps only rows from File 2 that have matching values in File 1
- **Example**: Find prospects who are already customers
- **Result**: File 2 with only matching rows

#### Find Common Values
- **What it does**: Creates a new file with rows that exist in both files
- **Example**: Find customers who appear in both lists
- **Result**: Combined file with common rows from both files

#### Find Unique Values
- **What it does**: Creates a new file with rows that exist in only one file
- **Example**: Find what's unique to each list
- **Result**: Combined file with unique rows from both files

**Parameters**:
- **Case Sensitive**: Whether "Email@test.com" and "email@test.com" are treated as different
- **Output Format**: CSV (universal) or Excel (preserves formatting)

**Operation Preview**:
- Shows expected results before processing
- Displays row counts and statistics
- Review this carefully to ensure correct operation

### Step 4: Results

**Purpose**: Review and export your processed data.

**What you'll see**:
- Operation summary with statistics
- Results table with processed data
- Pagination controls for large result sets
- Export options

**How to export**:
1. Choose your preferred format (CSV or Excel)
2. Click "Export Results"
3. Select where to save the file
4. Optionally open the file location after export

## Operation Types Explained

### Real-World Examples

**Scenario**: You have a customer database (File 1) and a prospect list (File 2), both with email addresses.

#### Remove Matches Example
- **File 1**: john@test.com, mary@test.com, bob@test.com
- **File 2**: mary@test.com, alice@test.com, bob@test.com, charlie@test.com
- **Result**: alice@test.com, charlie@test.com
- **Use Case**: Clean prospect list by removing existing customers

#### Keep Only Matches Example
- **Same input as above**
- **Result**: mary@test.com, bob@test.com
- **Use Case**: Find prospects who are already in your system

#### Find Common Values Example
- **Same input as above**
- **Result**: mary@test.com (from both files), bob@test.com (from both files)
- **Use Case**: Identify overlap between two lists

#### Find Unique Values Example
- **Same input as above**
- **Result**: john@test.com (File 1 only), alice@test.com (File 2 only), charlie@test.com (File 2 only)
- **Use Case**: Identify what's unique to each list

## Tips and Best Practices

### File Preparation
- Ensure column headers are in the first row
- Use consistent data formatting within columns
- Remove extra spaces or special characters if possible
- Save Excel files in .xlsx format for best compatibility

### Column Selection
- Choose columns with consistent, comparable data
- Email addresses work well for most comparisons
- ID numbers and codes are also good choices
- Avoid columns with mostly unique values

### Performance Optimization
- Test with smaller files first to verify settings
- Close other applications when processing large files
- Use CSV format for better performance with very large datasets
- Ensure sufficient disk space for result files

### Data Quality
- Review file previews to ensure data loaded correctly
- Check sample matching values to verify column selection
- Use the operation preview to confirm expected results
- Consider case sensitivity based on your data

## Troubleshooting

### File Loading Issues

**Problem**: "File format not supported" error
**Solution**: Ensure file is .csv, .xlsx, or .xls format

**Problem**: "File cannot be parsed" error
**Solution**: Check that CSV files use comma separators and Excel files aren't corrupted

**Problem**: File loads but shows no data
**Solution**: Verify the file has data and column headers in the first row

### Column Mapping Issues

**Problem**: Columns show as incompatible
**Solution**: Check data types - ensure both columns contain similar types of data

**Problem**: No matching values found
**Solution**: Verify you've selected the correct columns and check case sensitivity settings

**Problem**: Sample preview shows unexpected results
**Solution**: Review the actual data in your files for formatting inconsistencies

### Operation Problems

**Problem**: Operation produces no results
**Solution**: Check that the selected columns actually contain matching values

**Problem**: Results are different than expected
**Solution**: Review the operation description and preview before processing

**Problem**: Processing takes too long
**Solution**: Large files may take time - check the progress indicator and be patient

### Export Issues

**Problem**: Export fails with permission error
**Solution**: Ensure you have write access to the selected folder

**Problem**: Exported file is empty
**Solution**: Verify that the operation produced results before exporting

**Problem**: Can't open exported file
**Solution**: Check that you have appropriate software (Excel for .xlsx, text editor for .csv)

## Keyboard Shortcuts

### Global Shortcuts
- **F1**: Show help for current step
- **Ctrl+N**: New comparison (reset)
- **Ctrl+R**: Reset workflow
- **F5**: Refresh current step
- **Escape**: Cancel current operation

### Navigation Shortcuts
- **Ctrl+Right Arrow**: Next step
- **Ctrl+Left Arrow**: Previous step
- **Ctrl+1**: Go to File Selection
- **Ctrl+2**: Go to Column Mapping
- **Ctrl+3**: Go to Operation Config
- **Ctrl+4**: Go to Results

### Results Shortcuts
- **Ctrl+E**: Export results
- **Page Up**: Previous page of results
- **Page Down**: Next page of results
- **Ctrl+Home**: First page
- **Ctrl+End**: Last page

## Frequently Asked Questions

### General Questions

**Q: What file formats are supported?**
A: CSV (.csv) and Excel (.xlsx, .xls) files are supported.

**Q: How large can my files be?**
A: The tool can handle files with hundreds of thousands of rows, but performance depends on your system's memory and processing power.

**Q: Can I compare files with different structures?**
A: Yes, as long as both files have at least one comparable column (like email addresses or IDs).

### Operation Questions

**Q: What's the difference between "Remove Matches" and "Keep Only Matches"?**
A: "Remove Matches" gives you File 2 minus the matches, while "Keep Only Matches" gives you only the matches from File 2.

**Q: Which operation should I use to find duplicates?**
A: Use "Find Common Values" to see what appears in both files.

**Q: Can I undo an operation?**
A: No, but you can always go back and run a different operation with the same files.

### Technical Questions

**Q: Why is case sensitivity important?**
A: Email addresses and IDs might have different capitalization. Case sensitivity determines whether "John@test.com" and "john@test.com" are treated as the same or different.

**Q: Should I choose CSV or Excel for export?**
A: CSV is more universal and works with any program. Excel preserves formatting but requires Excel or compatible software.

**Q: What happens to columns that aren't used for comparison?**
A: All columns from the source files are preserved in the results - only the rows are filtered based on the comparison column.

### Getting Help

If you need additional assistance:
1. Use the Help menu for contextual help
2. Hover over interface elements for tooltips
3. Press F1 for help with the current step
4. Review the operation preview before processing
5. Test with small files first to verify your settings

---

*File Comparison Tool v1.0 - Built with Python and tkinter*