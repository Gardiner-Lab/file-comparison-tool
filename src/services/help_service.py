"""
Help service for the File Comparison Tool.

This module provides centralized help content management, tooltip functionality,
contextual help dialogs, and keyboard shortcuts for the application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable
import webbrowser
import os


class HelpService:
    """
    Service for managing help content, tooltips, and user assistance features.
    
    Provides centralized help content management, tooltip creation and management,
    contextual help dialogs, and keyboard shortcut handling.
    """
    
    def __init__(self):
        """Initialize the help service with content and tooltip management."""
        self.tooltips = {}  # Store active tooltips
        self.help_content = self._initialize_help_content()
        self.keyboard_shortcuts = self._initialize_keyboard_shortcuts()
        
    def _initialize_help_content(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize help content for different components and operations.
        
        Returns:
            Dictionary containing help content organized by component/topic
        """
        return {
            'file_selection': {
                'title': 'File Selection Help',
                'content': """
FILE SELECTION GUIDE

Supported File Formats:
• CSV files (.csv) - Comma-separated values
• Excel files (.xlsx, .xls) - Microsoft Excel format

How to Select Files:
1. Click the "Browse..." button to open a file dialog
2. Navigate to your file and select it
3. The file will be automatically validated and previewed

File Validation:
✓ Green checkmark = File loaded successfully
✗ Red X = File has errors or unsupported format

File Preview:
• Shows the first 10 rows of your data
• Displays file information (type, size, columns, rows)
• Use tabs to switch between File 1 and File 2 previews

Tips:
• Ensure your files have column headers in the first row
• CSV files should use comma separators
• Excel files can have multiple sheets (first sheet will be used)
• Large files may take a moment to load and preview
                """.strip()
            },
            
            'column_mapping': {
                'title': 'Column Mapping Help',
                'content': """
COLUMN MAPPING GUIDE

Purpose:
Select which columns from each file you want to compare. These columns will be used to find matches, differences, or perform other operations.

How to Map Columns:
1. Select a column from File 1 using the dropdown menu
2. Select a column from File 2 using the dropdown menu
3. The system will validate compatibility automatically

Column Compatibility:
✓ Compatible data types (both text, both numbers, etc.)
⚠ Mixed types (will be compared as text)
✗ Incompatible types (cannot be compared)

Column Information Display:
• Data Type: Shows whether the column contains text, numbers, dates, etc.
• Non-null Count: Shows how many rows have data (not empty)
• Sample Values: Shows examples of data in the column

Sample Matching Values:
• Shows values that appear in both selected columns
• Helps verify you've selected the correct columns
• Displays frequency counts for common values

Tips:
• Email columns work well for comparisons
• ID numbers and codes are also good comparison columns
• Avoid columns with mostly unique values (like names or descriptions)
• Case sensitivity can be adjusted in the next step
                """.strip()
            },
            
            'operation_config': {
                'title': 'Operation Configuration Help',
                'content': """
OPERATION CONFIGURATION GUIDE

Available Operations:

1. REMOVE MATCHES
   • Removes rows from File 2 that have matching values in File 1
   • Example: Remove customers from File 2 who already exist in File 1
   • Result: File 2 with matching rows removed

2. KEEP ONLY MATCHES
   • Keeps only rows from File 2 that have matching values in File 1
   • Example: Keep only customers from File 2 who exist in File 1
   • Result: File 2 with only matching rows

3. FIND COMMON VALUES
   • Creates a new file with rows that exist in both files
   • Example: Find customers who appear in both files
   • Result: Combined file with common rows from both files

4. FIND UNIQUE VALUES
   • Creates a new file with rows that exist in only one file
   • Example: Find customers who appear in only one file
   • Result: Combined file with unique rows from both files

Parameters:

Case Sensitive Comparison:
☐ Unchecked: "Email@test.com" = "email@test.com" (same)
☑ Checked: "Email@test.com" ≠ "email@test.com" (different)

Output Format:
• CSV: Comma-separated values, compatible with Excel and other tools
• Excel: Microsoft Excel format with formatting preserved

Operation Preview:
• Shows expected results before processing
• Displays row counts and statistics
• Helps verify the operation will produce desired results

Tips:
• Start with a small test to verify results before processing large files
• Use "Find Common Values" to see what matches exist
• Case sensitivity matters for email addresses and IDs
• CSV format is more universal, Excel preserves formatting
                """.strip()
            },
            
            'results': {
                'title': 'Results Display Help',
                'content': """
RESULTS DISPLAY GUIDE

Operation Summary:
• Shows which operation was performed
• Displays processing time and row counts
• Provides a summary of what was accomplished

Results Table:
• Shows the processed data in a scrollable table
• Use pagination controls to navigate through large results
• Adjust "Rows per page" to show more or fewer rows at once

Pagination Controls:
• Previous/Next buttons to navigate pages
• Page information shows current position
• Rows per page: 50, 100, 200, or 500 rows

Export Options:
• CSV Format: Universal format, opens in Excel and other programs
• Excel Format: Preserves formatting, creates .xlsx file
• Choose location and filename for your exported results

Export Process:
1. Select your preferred format (CSV or Excel)
2. Click "Export Results"
3. Choose where to save the file
4. Option to open file location after export

Tips:
• Review results before exporting to ensure they're correct
• CSV files are smaller and more compatible
• Excel files preserve data types and formatting
• Large result sets may take a moment to export
• The exported file contains all results, not just the current page
                """.strip()
            },
            
            'operations_detailed': {
                'title': 'Detailed Operation Examples',
                'content': """
DETAILED OPERATION EXAMPLES

Example Scenario:
File 1 (customers.csv): Existing customers with emails
File 2 (prospects.csv): Potential new customers with emails
Comparison Column: Email address

REMOVE MATCHES Example:
Input:
  File 1: john@test.com, mary@test.com, bob@test.com
  File 2: mary@test.com, alice@test.com, bob@test.com, charlie@test.com

Result: File 2 with matching emails removed
  Output: alice@test.com, charlie@test.com

Use Case: Remove prospects who are already customers

KEEP ONLY MATCHES Example:
Same input as above

Result: File 2 with only matching emails kept
  Output: mary@test.com, bob@test.com

Use Case: Find prospects who are already in your system

FIND COMMON VALUES Example:
Same input as above

Result: New file with emails that appear in both files
  Output: mary@test.com (from both files), bob@test.com (from both files)

Use Case: Identify overlap between two lists

FIND UNIQUE VALUES Example:
Same input as above

Result: New file with emails that appear in only one file
  Output: john@test.com (File 1 only), alice@test.com (File 2 only), charlie@test.com (File 2 only)

Use Case: Identify what's unique to each list

Real-World Applications:
• Email marketing: Remove existing subscribers from new lists
• Customer management: Find duplicate customers across systems
• Data cleanup: Identify and handle overlapping records
• List segmentation: Separate known vs. unknown contacts
                """.strip()
            },
            
            'troubleshooting': {
                'title': 'Troubleshooting Guide',
                'content': """
TROUBLESHOOTING GUIDE

Common Issues and Solutions:

FILE LOADING PROBLEMS:
Problem: "File format not supported" error
Solution: Ensure file is .csv, .xlsx, or .xls format

Problem: "File cannot be parsed" error
Solution: Check that CSV files use comma separators and Excel files aren't corrupted

Problem: File loads but shows no data
Solution: Verify the file has data and column headers in the first row

COLUMN MAPPING ISSUES:
Problem: Columns show as incompatible
Solution: Check data types - numbers can't be compared with text directly

Problem: No matching values found
Solution: Verify you've selected the correct columns and check case sensitivity

Problem: Sample preview shows unexpected results
Solution: Review the actual data in your files for formatting issues

OPERATION PROBLEMS:
Problem: Operation produces no results
Solution: Check that the selected columns actually contain matching values

Problem: Results are different than expected
Solution: Review the operation description and preview before processing

Problem: Processing takes too long
Solution: Large files may take time - check the progress indicator

EXPORT ISSUES:
Problem: Export fails with permission error
Solution: Ensure you have write access to the selected folder

Problem: Exported file is empty
Solution: Verify that the operation produced results before exporting

Problem: Can't open exported file
Solution: Check that you have appropriate software (Excel for .xlsx, text editor for .csv)

PERFORMANCE TIPS:
• Close other applications when processing large files
• Use CSV format for better performance with very large datasets
• Test with smaller files first to verify your settings
• Ensure sufficient disk space for large result files

Getting Help:
• Use tooltips (hover over elements) for quick help
• Check the operation preview before processing
• Review file information to verify data loaded correctly
• Use the Help menu for additional guidance
                """.strip()
            }
        }
        
    def _initialize_keyboard_shortcuts(self) -> Dict[str, Dict[str, str]]:
        """
        Initialize keyboard shortcuts for the application.
        
        Returns:
            Dictionary containing keyboard shortcuts organized by category
        """
        return {
            'global': {
                'Ctrl+N': 'New comparison',
                'Ctrl+O': 'Open files',
                'Ctrl+S': 'Export results',
                'Ctrl+R': 'Reset workflow',
                'F1': 'Show help',
                'F5': 'Refresh current step',
                'Escape': 'Cancel current operation'
            },
            'navigation': {
                'Ctrl+Right': 'Next step',
                'Ctrl+Left': 'Previous step',
                'Ctrl+1': 'Go to File Selection',
                'Ctrl+2': 'Go to Column Mapping',
                'Ctrl+3': 'Go to Operation Config',
                'Ctrl+4': 'Go to Results'
            },
            'results': {
                'Ctrl+E': 'Export results',
                'Page Up': 'Previous page',
                'Page Down': 'Next page',
                'Ctrl+Home': 'First page',
                'Ctrl+End': 'Last page'
            }
        }
        
    def add_tooltip(self, widget: tk.Widget, text: str, delay: int = 500) -> None:
        """
        Add a tooltip to a widget.
        
        Args:
            widget: The widget to add tooltip to
            text: Tooltip text to display
            delay: Delay in milliseconds before showing tooltip
        """
        tooltip = ToolTip(widget, text, delay)
        self.tooltips[widget] = tooltip
        
    def remove_tooltip(self, widget: tk.Widget) -> None:
        """
        Remove tooltip from a widget.
        
        Args:
            widget: The widget to remove tooltip from
        """
        if widget in self.tooltips:
            self.tooltips[widget].destroy()
            del self.tooltips[widget]
            
    def show_contextual_help(self, topic: str, parent: Optional[tk.Widget] = None) -> None:
        """
        Show contextual help dialog for a specific topic.
        
        Args:
            topic: Help topic key
            parent: Parent widget for the dialog
        """
        if topic not in self.help_content:
            messagebox.showwarning("Help", f"Help content for '{topic}' is not available.")
            return
            
        help_info = self.help_content[topic]
        HelpDialog(parent, help_info['title'], help_info['content'])
        
    def show_keyboard_shortcuts(self, parent: Optional[tk.Widget] = None) -> None:
        """
        Show keyboard shortcuts dialog.
        
        Args:
            parent: Parent widget for the dialog
        """
        shortcuts_text = "KEYBOARD SHORTCUTS\n\n"
        
        for category, shortcuts in self.keyboard_shortcuts.items():
            shortcuts_text += f"{category.upper()}:\n"
            for key, description in shortcuts.items():
                shortcuts_text += f"  {key:<15} {description}\n"
            shortcuts_text += "\n"
            
        HelpDialog(parent, "Keyboard Shortcuts", shortcuts_text.strip())
        
    def show_about_dialog(self, parent: Optional[tk.Widget] = None) -> None:
        """
        Show about dialog with application information.
        
        Args:
            parent: Parent widget for the dialog
        """
        about_text = """
FILE COMPARISON TOOL
Version 1.0

A desktop application for comparing Excel and CSV files with configurable operations and export capabilities.

Features:
• Support for CSV and Excel file formats
• Multiple comparison operations (remove, keep, find common/unique)
• Column mapping with compatibility validation
• Real-time preview of operations and results
• Export results in CSV or Excel format
• Comprehensive help system and tooltips

Built with Python and tkinter.

© 2024 File Comparison Tool
        """.strip()
        
        HelpDialog(parent, "About File Comparison Tool", about_text)
        
    def open_user_guide(self) -> None:
        """Open the user guide in the default web browser or show built-in guide."""
        # For now, show a comprehensive user guide dialog
        # In a real application, this might open a web page or PDF
        user_guide_text = """
FILE COMPARISON TOOL - USER GUIDE

GETTING STARTED:
1. Launch the application
2. Select two files to compare (CSV or Excel)
3. Choose which columns to compare
4. Select the comparison operation
5. Review and export results

STEP-BY-STEP WORKFLOW:

Step 1: File Selection
• Click "Browse..." to select your first file
• Click "Browse..." to select your second file
• Review the file preview to ensure data loaded correctly
• Both files must be successfully loaded to proceed

Step 2: Column Mapping
• Select the column from File 1 that contains comparison values
• Select the column from File 2 that contains comparison values
• Verify compatibility (green checkmark indicates compatible columns)
• Review sample matching values to confirm correct selection

Step 3: Operation Configuration
• Choose your desired operation:
  - Remove Matches: Remove File 2 rows that match File 1
  - Keep Only Matches: Keep only File 2 rows that match File 1
  - Find Common Values: Create file with rows from both files
  - Find Unique Values: Create file with rows unique to each file
• Configure case sensitivity if needed
• Select output format (CSV or Excel)
• Review operation preview

Step 4: Results
• Review the operation summary and statistics
• Browse through results using pagination controls
• Export results to your desired location and format

TIPS FOR SUCCESS:
• Use columns with consistent data (emails, IDs, codes)
• Test with small files first to verify settings
• Review previews before processing large datasets
• Choose appropriate case sensitivity for your data
• Export results promptly after processing

For additional help, use the Help menu or hover over interface elements for tooltips.
        """.strip()
        
        HelpDialog(None, "User Guide", user_guide_text)


class ToolTip:
    """
    Tooltip widget that displays help text when hovering over a widget.
    
    Provides customizable tooltip functionality with configurable delay,
    positioning, and styling.
    """
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        """
        Initialize tooltip for a widget.
        
        Args:
            widget: Widget to attach tooltip to
            text: Text to display in tooltip
            delay: Delay in milliseconds before showing tooltip
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)
        
    def _on_enter(self, event=None):
        """Handle mouse enter event."""
        self._schedule_tooltip()
        
    def _on_leave(self, event=None):
        """Handle mouse leave event."""
        self._cancel_tooltip()
        self._hide_tooltip()
        
    def _on_motion(self, event=None):
        """Handle mouse motion event."""
        if self.tooltip_window:
            self._update_tooltip_position(event)
            
    def _schedule_tooltip(self):
        """Schedule tooltip to appear after delay."""
        self._cancel_tooltip()
        self.after_id = self.widget.after(self.delay, self._show_tooltip)
        
    def _cancel_tooltip(self):
        """Cancel scheduled tooltip."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
            
    def _show_tooltip(self):
        """Show the tooltip window."""
        if self.tooltip_window:
            return
            
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Configure tooltip appearance
        self.tooltip_window.configure(background="#ffffe0", relief="solid", borderwidth=1)
        
        # Add tooltip text
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            foreground="#000000",
            font=("Arial", 9),
            justify="left",
            wraplength=300,
            padx=5,
            pady=3
        )
        label.pack()
        
    def _hide_tooltip(self):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
    def _update_tooltip_position(self, event):
        """Update tooltip position based on mouse movement."""
        if self.tooltip_window:
            x = event.x_root + 20
            y = event.y_root + 5
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            
    def destroy(self):
        """Destroy the tooltip and clean up."""
        self._cancel_tooltip()
        self._hide_tooltip()
        
        # Unbind events
        try:
            self.widget.unbind("<Enter>")
            self.widget.unbind("<Leave>")
            self.widget.unbind("<Motion>")
        except:
            pass  # Widget may already be destroyed


class HelpDialog:
    """
    Modal dialog for displaying help content.
    
    Provides a scrollable text area for displaying help content with
    proper formatting and user-friendly navigation.
    """
    
    def __init__(self, parent: Optional[tk.Widget], title: str, content: str):
        """
        Initialize help dialog.
        
        Args:
            parent: Parent widget for the dialog
            title: Dialog title
            content: Help content to display
        """
        self.parent = parent
        self.title = title
        self.content = content
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure dialog
        self._setup_dialog()
        self._create_widgets()
        self._center_dialog()
        
        # Focus and wait
        self.dialog.focus_set()
        self.dialog.wait_window()
        
    def _setup_dialog(self):
        """Configure dialog window properties."""
        self.dialog.resizable(True, True)
        self.dialog.minsize(500, 400)
        
        # Configure grid weights
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Text widget
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            background="#f8f9fa",
            foreground="#333333",
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Insert content
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, self.content)
        self.text_widget.configure(state=tk.DISABLED)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=self._close_dialog)
        close_button.grid(row=0, column=1, sticky="e")
        
        # Bind Escape key
        self.dialog.bind("<Escape>", lambda e: self._close_dialog())
        
    def _center_dialog(self):
        """Center the dialog on screen or parent."""
        self.dialog.update_idletasks()
        
        # Get dialog size
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        # Calculate position
        if self.parent:
            # Center on parent
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
        else:
            # Center on screen
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def _close_dialog(self):
        """Close the dialog."""
        self.dialog.destroy()