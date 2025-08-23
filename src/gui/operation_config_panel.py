"""
Operation configuration panel for the File Comparison Tool.

This module contains the OperationConfigPanel class which provides an interface
for selecting comparison operations, configuring parameters, and previewing
expected results with validation.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from models.data_models import FileInfo, ComparisonConfig
from models.interfaces import GUIComponentInterface
from services.help_service import HelpService


class OperationConfigPanel(GUIComponentInterface):
    """
    Panel for configuring comparison operations and parameters.
    
    Provides radio buttons for operation selection, parameter inputs for
    case sensitivity and other options, operation preview showing expected
    result summary, and validation for operation-specific parameters.
    """
    
    def __init__(self, parent_frame: tk.Widget, on_config_changed: Optional[Callable] = None):
        """
        Initialize the operation configuration panel.
        
        Args:
            parent_frame: Parent tkinter widget to contain this panel
            on_config_changed: Callback function called when configuration changes
        """
        self.parent_frame = parent_frame
        self.on_config_changed = on_config_changed
        self.help_service = HelpService()
        
        # Configuration state
        self.selected_operation: Optional[str] = None
        self.case_sensitive = False
        self.output_format = "csv"
        
        # File data for preview
        self.file1_info: Optional[FileInfo] = None
        self.file2_info: Optional[FileInfo] = None
        self.file1_data: Optional[pd.DataFrame] = None
        self.file2_data: Optional[pd.DataFrame] = None
        self.file1_column: Optional[str] = None
        self.file2_column: Optional[str] = None
        
        # Validation state
        self.is_config_valid = False
        self.validation_message = ""
        
        # Operation definitions
        self.operations = {
            'remove_matches': {
                'name': 'Remove Matches',
                'description': 'Remove rows from File 2 where the comparison column matches values in File 1',
                'example': 'File 2 rows with emails that exist in File 1 will be removed'
            },
            'keep_matches': {
                'name': 'Keep Only Matches', 
                'description': 'Keep only rows from File 2 where the comparison column matches values in File 1',
                'example': 'Only File 2 rows with emails that exist in File 1 will be kept'
            },
            'find_common': {
                'name': 'Find Common Values',
                'description': 'Create a new file with rows that exist in both files',
                'example': 'New file with rows containing emails that appear in both files'
            },
            'find_unique': {
                'name': 'Find Unique Values',
                'description': 'Create a new file with rows that exist in only one of the files',
                'example': 'New file with rows containing emails that appear in only one file'
            }
        }
        
        # Create the main panel
        self.panel = ttk.Frame(parent_frame)
        self.panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights for responsive layout
        self.panel.grid_rowconfigure(2, weight=1)  # Preview area
        self.panel.grid_columnconfigure(0, weight=1)
        
        self.initialize_component()
        
    def initialize_component(self) -> None:
        """Initialize the GUI component and its widgets."""
        self._create_widgets()
        self._add_tooltips()
        
    def _create_widgets(self):
        """Create all GUI widgets for the operation configuration panel."""
        # Title
        title_label = ttk.Label(self.panel, text="Configure Comparison Operation", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Operation selection frame
        self._create_operation_selection_frame()
        
        # Parameters frame
        self._create_parameters_frame()
        
        # Preview area
        self._create_preview_area()
        
    def _create_operation_selection_frame(self):
        """Create the operation selection interface with radio buttons."""
        # Main selection frame
        selection_frame = ttk.LabelFrame(self.panel, text="Select Operation", padding="15")
        selection_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        selection_frame.grid_columnconfigure(0, weight=1)
        
        # Operation selection variable
        self.operation_var = tk.StringVar()
        self.operation_var.trace('w', self._on_operation_changed)
        
        # Create radio buttons for each operation
        self.operation_radios = {}
        for i, (op_key, op_info) in enumerate(self.operations.items()):
            # Radio button frame
            radio_frame = ttk.Frame(selection_frame)
            radio_frame.grid(row=i, column=0, sticky="ew", pady=5)
            radio_frame.grid_columnconfigure(1, weight=1)
            
            # Radio button
            radio = ttk.Radiobutton(radio_frame, text=op_info['name'], 
                                   variable=self.operation_var, value=op_key)
            radio.grid(row=0, column=0, sticky="w", padx=(0, 15))
            self.operation_radios[op_key] = radio
            
            # Description
            desc_label = ttk.Label(radio_frame, text=op_info['description'],
                                  font=('Arial', 9), foreground="gray")
            desc_label.grid(row=0, column=1, sticky="w")
            
            # Example (on next line)
            example_label = ttk.Label(radio_frame, text=f"Example: {op_info['example']}",
                                     font=('Arial', 8), foreground="blue")
            example_label.grid(row=1, column=1, sticky="w", padx=(0, 0), pady=(2, 0))
        
    def _create_parameters_frame(self):
        """Create the parameters configuration frame."""
        # Parameters frame
        params_frame = ttk.LabelFrame(self.panel, text="Operation Parameters", padding="15")
        params_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        params_frame.grid_columnconfigure(0, weight=1)
        
        # Parameters container
        params_container = ttk.Frame(params_frame)
        params_container.grid(row=0, column=0, sticky="ew")
        params_container.grid_columnconfigure(1, weight=1)
        
        # Case sensitivity option
        self.case_sensitive_var = tk.BooleanVar()
        self.case_sensitive_var.trace('w', self._on_parameter_changed)
        self.case_sensitive_checkbox = ttk.Checkbutton(params_container, text="Case sensitive comparison",
                                                      variable=self.case_sensitive_var)
        self.case_sensitive_checkbox.grid(row=0, column=0, sticky="w", pady=5)
        
        # Case sensitivity explanation
        case_help = ttk.Label(params_container, 
                             text="When checked, 'Email@test.com' and 'email@test.com' will be treated as different",
                             font=('Arial', 8), foreground="gray")
        case_help.grid(row=0, column=1, sticky="w", padx=(20, 0))
        
        # Output format selection
        format_frame = ttk.Frame(params_container)
        format_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 5))
        
        ttk.Label(format_frame, text="Output Format:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w")
        
        self.output_format_var = tk.StringVar(value="csv")
        self.output_format_var.trace('w', self._on_parameter_changed)
        
        csv_radio = ttk.Radiobutton(format_frame, text="CSV (.csv)", 
                                   variable=self.output_format_var, value="csv")
        csv_radio.grid(row=0, column=1, sticky="w", padx=(20, 15))
        
        excel_radio = ttk.Radiobutton(format_frame, text="Excel (.xlsx)", 
                                     variable=self.output_format_var, value="excel")
        excel_radio.grid(row=0, column=2, sticky="w")
        
        # Validation indicator
        validation_frame = ttk.Frame(params_container)
        validation_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        validation_frame.grid_columnconfigure(1, weight=1)
        
        # Validation icon
        self.validation_icon_var = tk.StringVar()
        self.validation_icon_label = ttk.Label(validation_frame, textvariable=self.validation_icon_var,
                                              font=('Arial', 14), width=3)
        self.validation_icon_label.grid(row=0, column=0, padx=(0, 10))
        
        # Validation message
        self.validation_message_var = tk.StringVar()
        self.validation_message_var.set("Please select an operation")
        self.validation_message_label = ttk.Label(validation_frame, textvariable=self.validation_message_var,
                                                 font=('Arial', 10), foreground="gray")
        self.validation_message_label.grid(row=0, column=1, sticky="w")
        
    def _create_preview_area(self):
        """Create the operation preview area showing expected results."""
        # Preview frame
        preview_frame = ttk.LabelFrame(self.panel, text="Operation Preview", padding="10")
        preview_frame.grid(row=3, column=0, sticky="nsew")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions
        instructions = ttk.Label(preview_frame, 
                                text="Select an operation to see expected results summary",
                                font=('Arial', 10), foreground="gray")
        instructions.grid(row=0, column=0, pady=(0, 10))
        
        # Preview content frame
        self.preview_content_frame = ttk.Frame(preview_frame)
        self.preview_content_frame.grid(row=1, column=0, sticky="nsew")
        self.preview_content_frame.grid_rowconfigure(0, weight=1)
        self.preview_content_frame.grid_columnconfigure(0, weight=1)
        
        # Preview text widget
        self.preview_text = tk.Text(self.preview_content_frame, height=8, wrap=tk.WORD,
                                   font=('Arial', 10), state=tk.DISABLED,
                                   background="#f8f9fa", relief="flat")
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar for preview text
        preview_scrollbar = ttk.Scrollbar(self.preview_content_frame, orient="vertical", 
                                         command=self.preview_text.yview)
        preview_scrollbar.grid(row=0, column=1, sticky="ns")
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
    def set_file_data(self, file1_info: Optional[FileInfo], file2_info: Optional[FileInfo],
                      file1_data: Optional[pd.DataFrame], file2_data: Optional[pd.DataFrame],
                      file1_column: Optional[str], file2_column: Optional[str]):
        """
        Set the file data and column selection for operation preview.
        
        Args:
            file1_info: FileInfo object for first file
            file2_info: FileInfo object for second file
            file1_data: DataFrame for first file
            file2_data: DataFrame for second file
            file1_column: Selected column from first file
            file2_column: Selected column from second file
        """
        self.file1_info = file1_info
        self.file2_info = file2_info
        self.file1_data = file1_data
        self.file2_data = file2_data
        self.file1_column = file1_column
        self.file2_column = file2_column
        
        # Update preview
        self._update_preview()
        
        # Validate configuration
        self._validate_configuration()
        
    def _on_operation_changed(self, *args):
        """Handle operation selection change."""
        self.selected_operation = self.operation_var.get() if self.operation_var.get() else None
        self._update_preview()
        self._validate_configuration()
        
        if self.on_config_changed:
            try:
                config = self.get_operation_config()
                self.on_config_changed(config)
            except Exception:
                # Fallback to calling without arguments for compatibility
                self.on_config_changed()
            
    def _on_parameter_changed(self, *args):
        """Handle parameter change."""
        self.case_sensitive = self.case_sensitive_var.get()
        self.output_format = self.output_format_var.get()
        
        self._update_preview()
        self._validate_configuration()
        
        if self.on_config_changed:
            try:
                config = self.get_operation_config()
                self.on_config_changed(config)
            except Exception:
                # Fallback to calling without arguments for compatibility
                self.on_config_changed()
            
    def _validate_configuration(self):
        """Validate the current operation configuration."""
        if not self.selected_operation:
            self.is_config_valid = False
            self.validation_message = "Please select an operation"
            self._update_validation_display()
            return
            
        if not self.file1_column or not self.file2_column:
            self.is_config_valid = False
            self.validation_message = "Column mapping required before operation configuration"
            self._update_validation_display()
            return
            
        if self.file1_data is None or self.file2_data is None:
            self.is_config_valid = False
            self.validation_message = "File data not available"
            self._update_validation_display()
            return
            
        # All validations passed
        self.is_config_valid = True
        self.validation_message = "✓ Configuration is valid and ready for processing"
        self._update_validation_display()
        
    def _update_validation_display(self):
        """Update the validation indicator and message display."""
        if not self.selected_operation:
            self.validation_icon_var.set("")
            self.validation_message_var.set("Please select an operation")
            self.validation_message_label.configure(foreground="gray")
        elif self.is_config_valid:
            self.validation_icon_var.set("✓")
            self.validation_message_var.set(self.validation_message)
            self.validation_message_label.configure(foreground="green")
        else:
            self.validation_icon_var.set("⚠")
            self.validation_message_var.set(self.validation_message)
            self.validation_message_label.configure(foreground="orange")
            
    def _update_preview(self):
        """Update the operation preview with expected results."""
        # Clear preview
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        if not self.selected_operation:
            self.preview_text.insert(tk.END, "Select an operation to see preview...")
            self.preview_text.configure(state=tk.DISABLED)
            return
            
        if not self.file1_column or not self.file2_column or self.file1_data is None or self.file2_data is None:
            self.preview_text.insert(tk.END, "File data and column mapping required for preview...")
            self.preview_text.configure(state=tk.DISABLED)
            return
            
        try:
            preview_content = self._generate_preview_content()
            self.preview_text.insert(tk.END, preview_content)
        except Exception as e:
            self.preview_text.insert(tk.END, f"Error generating preview: {str(e)}")
            
        self.preview_text.configure(state=tk.DISABLED)
        
    def _generate_preview_content(self) -> str:
        """
        Generate preview content for the selected operation.
        
        Returns:
            String containing preview information
        """
        if not self.selected_operation or self.file1_data is None or self.file2_data is None:
            return "Preview not available"
            
        # Get basic file information
        file1_name = self.file1_info.file_path.split('/')[-1] if self.file1_info else "File 1"
        file2_name = self.file2_info.file_path.split('/')[-1] if self.file2_info else "File 2"
        file1_rows = len(self.file1_data)
        file2_rows = len(self.file2_data)
        
        # Get column data for analysis
        col1_data = self.file1_data[self.file1_column].dropna()
        col2_data = self.file2_data[self.file2_column].dropna()
        
        # Convert to comparable format based on case sensitivity
        if not self.case_sensitive:
            col1_compare = col1_data.astype(str).str.lower()
            col2_compare = col2_data.astype(str).str.lower()
        else:
            col1_compare = col1_data.astype(str)
            col2_compare = col2_data.astype(str)
            
        # Calculate statistics
        col1_unique = set(col1_compare.unique())
        col2_unique = set(col2_compare.unique())
        common_values = col1_unique & col2_unique
        unique_to_file1 = col1_unique - col2_unique
        unique_to_file2 = col2_unique - col1_unique
        
        # Count rows that would be affected
        if self.selected_operation == 'remove_matches':
            # Rows in file2 that have matching values in file1
            affected_mask = col2_compare.isin(col1_unique)
            affected_rows = affected_mask.sum()
            result_rows = file2_rows - affected_rows
            
        elif self.selected_operation == 'keep_matches':
            # Rows in file2 that have matching values in file1
            affected_mask = col2_compare.isin(col1_unique)
            result_rows = affected_mask.sum()
            affected_rows = result_rows
            
        elif self.selected_operation == 'find_common':
            # Rows from both files that have common values
            file1_common_mask = col1_compare.isin(common_values)
            file2_common_mask = col2_compare.isin(common_values)
            result_rows = file1_common_mask.sum() + file2_common_mask.sum()
            affected_rows = result_rows
            
        elif self.selected_operation == 'find_unique':
            # Rows from both files that have unique values
            file1_unique_mask = col1_compare.isin(unique_to_file1)
            file2_unique_mask = col2_compare.isin(unique_to_file2)
            result_rows = file1_unique_mask.sum() + file2_unique_mask.sum()
            affected_rows = result_rows
            
        else:
            affected_rows = 0
            result_rows = 0
            
        # Generate preview text
        preview_lines = []
        preview_lines.append(f"OPERATION: {self.operations[self.selected_operation]['name']}")
        preview_lines.append("=" * 50)
        preview_lines.append("")
        
        preview_lines.append("INPUT FILES:")
        preview_lines.append(f"  • {file1_name}: {file1_rows:,} rows")
        preview_lines.append(f"  • {file2_name}: {file2_rows:,} rows")
        preview_lines.append("")
        
        preview_lines.append("COMPARISON COLUMNS:")
        preview_lines.append(f"  • File 1: '{self.file1_column}' ({len(col1_unique):,} unique values)")
        preview_lines.append(f"  • File 2: '{self.file2_column}' ({len(col2_unique):,} unique values)")
        preview_lines.append("")
        
        preview_lines.append("VALUE ANALYSIS:")
        preview_lines.append(f"  • Common values: {len(common_values):,}")
        preview_lines.append(f"  • Unique to File 1: {len(unique_to_file1):,}")
        preview_lines.append(f"  • Unique to File 2: {len(unique_to_file2):,}")
        preview_lines.append("")
        
        preview_lines.append("OPERATION PARAMETERS:")
        preview_lines.append(f"  • Case sensitive: {'Yes' if self.case_sensitive else 'No'}")
        preview_lines.append(f"  • Output format: {self.output_format.upper()}")
        preview_lines.append("")
        
        preview_lines.append("EXPECTED RESULTS:")
        if self.selected_operation == 'remove_matches':
            preview_lines.append(f"  • Rows to remove: {affected_rows:,}")
            preview_lines.append(f"  • Remaining rows: {result_rows:,}")
            preview_lines.append(f"  • Source: {file2_name} (modified)")
            
        elif self.selected_operation == 'keep_matches':
            preview_lines.append(f"  • Rows to keep: {result_rows:,}")
            preview_lines.append(f"  • Rows to remove: {file2_rows - result_rows:,}")
            preview_lines.append(f"  • Source: {file2_name} (filtered)")
            
        elif self.selected_operation == 'find_common':
            preview_lines.append(f"  • Total common rows: {result_rows:,}")
            preview_lines.append(f"  • Source: Both files (combined)")
            
        elif self.selected_operation == 'find_unique':
            preview_lines.append(f"  • Total unique rows: {result_rows:,}")
            preview_lines.append(f"  • Source: Both files (combined)")
            
        preview_lines.append("")
        preview_lines.append("DESCRIPTION:")
        preview_lines.append(f"  {self.operations[self.selected_operation]['description']}")
        
        return "\n".join(preview_lines)
        
    def validate_input(self) -> bool:
        """
        Validate the current input state of the component.
        
        Returns:
            True if input is valid, False otherwise
        """
        return self.is_config_valid
        
    def reset_component(self) -> None:
        """Reset the component to its initial state."""
        self.selected_operation = None
        self.case_sensitive = False
        self.output_format = "csv"
        self.file1_info = None
        self.file2_info = None
        self.file1_data = None
        self.file2_data = None
        self.file1_column = None
        self.file2_column = None
        self.is_config_valid = False
        self.validation_message = ""
        
        # Reset UI
        self.operation_var.set("")
        self.case_sensitive_var.set(False)
        self.output_format_var.set("csv")
        
        self._update_validation_display()
        self._update_preview()
        
    def get_component_data(self) -> Dict[str, Any]:
        """
        Get the current data/state from the component.
        
        Returns:
            Dictionary containing component data
        """
        return {
            'operation': self.selected_operation,
            'case_sensitive': self.case_sensitive,
            'output_format': self.output_format,
            'is_valid': self.is_config_valid,
            'validation_message': self.validation_message
        }
        
    def get_comparison_config(self) -> Optional[ComparisonConfig]:
        """
        Get the current comparison configuration.
        
        Returns:
            ComparisonConfig object if valid, None otherwise
        """
        if not self.is_config_valid or not self.file1_info or not self.file2_info:
            return None
            
        return ComparisonConfig(
            file1_path=self.file1_info.file_path,
            file2_path=self.file2_info.file_path,
            file1_column=self.file1_column,
            file2_column=self.file2_column,
            operation=self.selected_operation,
            output_format=self.output_format,
            case_sensitive=self.case_sensitive
        )
        
    def is_valid_configuration(self) -> bool:
        """
        Check if the current configuration is valid.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return self.is_config_valid
    
    def get_operation_config(self) -> Dict[str, Any]:
        """
        Get the current operation configuration for the MainController.
        
        Returns:
            Dictionary containing operation configuration
        """
        return {
            'operation': self.selected_operation,
            'case_sensitive': self.case_sensitive,
            'output_format': self.output_format,
            'is_valid': self.is_config_valid,
            'validation_message': self.validation_message,
            'file1_column': self.file1_column,
            'file2_column': self.file2_column
        }
    
    def set_file_info(self, file1_info: Optional[FileInfo], file2_info: Optional[FileInfo]):
        """
        Set file information for the operation config panel.
        
        Args:
            file1_info: FileInfo object for first file
            file2_info: FileInfo object for second file
        """
        self.file1_info = file1_info
        self.file2_info = file2_info
        
        # Update preview and validation
        self._update_preview()
        self._validate_configuration()
        
    def _add_tooltips(self):
        """Add tooltips to operation configuration components."""
        # Operation radio button tooltips
        operation_tooltips = {
            'remove_matches': ("Remove rows from File 2 that have matching values in File 1. "
                             "Example: Remove existing customers from a prospect list."),
            'keep_matches': ("Keep only rows from File 2 that have matching values in File 1. "
                           "Example: Find prospects who are already in your system."),
            'find_common': ("Create a new file with rows that exist in both files. "
                          "Example: Find customers who appear in both lists."),
            'find_unique': ("Create a new file with rows that exist in only one file. "
                          "Example: Find what's unique to each list.")
        }
        
        for op_key, tooltip_text in operation_tooltips.items():
            if op_key in self.operation_radios:
                self.help_service.add_tooltip(self.operation_radios[op_key], tooltip_text)
        
        # Case sensitivity tooltip
        case_tooltip = ("When checked, 'Email@test.com' and 'email@test.com' are treated as different values. "
                       "When unchecked, they are treated as the same value.")
        
        # Find the case sensitivity checkbox (need to store reference)
        if hasattr(self, 'case_sensitive_checkbox'):
            self.help_service.add_tooltip(self.case_sensitive_checkbox, case_tooltip)
        
        # Output format tooltips
        csv_tooltip = "CSV format is universal and works with Excel, Google Sheets, and other programs."
        excel_tooltip = "Excel format preserves formatting and data types but may not work with all programs."
        
        # Preview tooltip
        preview_tooltip = ("Shows expected results before processing. Review this carefully to ensure "
                         "the operation will produce the desired output.")
        
        self.help_service.add_tooltip(self.preview_text, preview_tooltip)