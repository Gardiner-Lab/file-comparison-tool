"""
Column mapping panel for the File Comparison Tool.

This module contains the ColumnMappingPanel class which provides an interface
for selecting and mapping columns between two files, with compatibility validation
and sample data preview functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from typing import Optional, Callable, Dict, Any, List, Tuple
import numpy as np

from models.data_models import FileInfo
from models.interfaces import GUIComponentInterface
from services.help_service import HelpService


class ColumnMappingPanel(GUIComponentInterface):
    """
    Panel for selecting and mapping columns between two files for comparison.
    
    Provides dropdown menus for column selection, compatibility validation with
    visual feedback, and sample data preview showing matching values between
    selected columns.
    """
    
    def __init__(self, parent_frame: tk.Widget, on_mapping_changed: Optional[Callable] = None):
        """
        Initialize the column mapping panel.
        
        Args:
            parent_frame: Parent tkinter widget to contain this panel
            on_mapping_changed: Callback function called when column mapping changes
        """
        self.parent_frame = parent_frame
        self.on_mapping_changed = on_mapping_changed
        self.help_service = HelpService()
        
        # File data storage
        self.file1_info: Optional[FileInfo] = None
        self.file2_info: Optional[FileInfo] = None
        self.file1_data: Optional[pd.DataFrame] = None
        self.file2_data: Optional[pd.DataFrame] = None
        
        # Selected columns
        self.selected_file1_column: Optional[str] = None
        self.selected_file2_column: Optional[str] = None
        
        # Validation state
        self.is_mapping_valid = False
        self.validation_message = ""
        
        # Create the main panel
        self.panel = ttk.Frame(parent_frame)
        self.panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights for responsive layout
        self.panel.grid_rowconfigure(2, weight=1)  # Sample preview area
        self.panel.grid_columnconfigure(0, weight=1)
        
        self.initialize_component()
        
    def initialize_component(self) -> None:
        """Initialize the GUI component and its widgets."""
        self._create_widgets()
        self._add_tooltips()
        
    def _create_widgets(self):
        """Create all GUI widgets for the column mapping panel."""
        # Title
        title_label = ttk.Label(self.panel, text="Select Columns to Compare", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Column selection frame
        self._create_column_selection_frame()
        
        # Sample preview area
        self._create_sample_preview_area()
        
    def _create_column_selection_frame(self):
        """Create the column selection interface with dropdowns and validation."""
        # Main selection frame
        selection_frame = ttk.LabelFrame(self.panel, text="Column Selection", padding="15")
        selection_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        selection_frame.grid_columnconfigure(1, weight=1)
        selection_frame.grid_columnconfigure(3, weight=1)
        
        # File 1 column selection
        ttk.Label(selection_frame, text="File 1 Column:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.file1_column_var = tk.StringVar()
        self.file1_column_combo = ttk.Combobox(selection_frame, textvariable=self.file1_column_var,
                                              state="readonly", width=25)
        self.file1_column_combo.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        self.file1_column_combo.bind('<<ComboboxSelected>>', self._on_column_selection_changed)
        
        # File 2 column selection
        ttk.Label(selection_frame, text="File 2 Column:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky="w", padx=(0, 10))
        
        self.file2_column_var = tk.StringVar()
        self.file2_column_combo = ttk.Combobox(selection_frame, textvariable=self.file2_column_var,
                                              state="readonly", width=25)
        self.file2_column_combo.grid(row=0, column=3, sticky="ew")
        self.file2_column_combo.bind('<<ComboboxSelected>>', self._on_column_selection_changed)
        
        # Validation indicator and message
        validation_frame = ttk.Frame(selection_frame)
        validation_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(15, 0))
        validation_frame.grid_columnconfigure(1, weight=1)
        
        # Validation icon
        self.validation_icon_var = tk.StringVar()
        self.validation_icon_label = ttk.Label(validation_frame, textvariable=self.validation_icon_var,
                                              font=('Arial', 14), width=3)
        self.validation_icon_label.grid(row=0, column=0, padx=(0, 10))
        
        # Validation message
        self.validation_message_var = tk.StringVar()
        self.validation_message_var.set("Please select columns from both files")
        self.validation_message_label = ttk.Label(validation_frame, textvariable=self.validation_message_var,
                                                 font=('Arial', 10), foreground="gray")
        self.validation_message_label.grid(row=0, column=1, sticky="w")
        
        # Column info display
        self._create_column_info_display(selection_frame)
        
    def _create_column_info_display(self, parent_frame):
        """Create column information display showing data types and sample values."""
        info_frame = ttk.Frame(parent_frame)
        info_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(15, 0))
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # File 1 column info
        file1_info_frame = ttk.LabelFrame(info_frame, text="File 1 Column Info", padding="10")
        file1_info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(file1_info_frame, text="Data Type:").grid(row=0, column=0, sticky="w")
        self.file1_dtype_var = tk.StringVar()
        self.file1_dtype_var.set("-")
        ttk.Label(file1_info_frame, textvariable=self.file1_dtype_var, 
                 foreground="blue").grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(file1_info_frame, text="Non-null Count:").grid(row=1, column=0, sticky="w")
        self.file1_count_var = tk.StringVar()
        self.file1_count_var.set("-")
        ttk.Label(file1_info_frame, textvariable=self.file1_count_var, 
                 foreground="blue").grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(file1_info_frame, text="Sample Values:").grid(row=2, column=0, sticky="nw")
        self.file1_samples_var = tk.StringVar()
        self.file1_samples_var.set("-")
        sample1_label = ttk.Label(file1_info_frame, textvariable=self.file1_samples_var, 
                                 foreground="blue", wraplength=200, justify="left")
        sample1_label.grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        # File 2 column info
        file2_info_frame = ttk.LabelFrame(info_frame, text="File 2 Column Info", padding="10")
        file2_info_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ttk.Label(file2_info_frame, text="Data Type:").grid(row=0, column=0, sticky="w")
        self.file2_dtype_var = tk.StringVar()
        self.file2_dtype_var.set("-")
        ttk.Label(file2_info_frame, textvariable=self.file2_dtype_var, 
                 foreground="blue").grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(file2_info_frame, text="Non-null Count:").grid(row=1, column=0, sticky="w")
        self.file2_count_var = tk.StringVar()
        self.file2_count_var.set("-")
        ttk.Label(file2_info_frame, textvariable=self.file2_count_var, 
                 foreground="blue").grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(file2_info_frame, text="Sample Values:").grid(row=2, column=0, sticky="nw")
        self.file2_samples_var = tk.StringVar()
        self.file2_samples_var.set("-")
        sample2_label = ttk.Label(file2_info_frame, textvariable=self.file2_samples_var, 
                                 foreground="blue", wraplength=200, justify="left")
        sample2_label.grid(row=2, column=1, sticky="w", padx=(10, 0))
        
    def _create_sample_preview_area(self):
        """Create the sample data preview area showing matching values."""
        # Preview frame
        preview_frame = ttk.LabelFrame(self.panel, text="Sample Matching Values", padding="10")
        preview_frame.grid(row=2, column=0, sticky="nsew")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions
        instructions = ttk.Label(preview_frame, 
                                text="Select columns from both files to see sample matching values",
                                font=('Arial', 10), foreground="gray")
        instructions.grid(row=0, column=0, pady=(0, 10))
        
        # Sample data display frame
        sample_frame = ttk.Frame(preview_frame)
        sample_frame.grid(row=1, column=0, sticky="nsew")
        sample_frame.grid_rowconfigure(0, weight=1)
        sample_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for sample data
        self.sample_tree = ttk.Treeview(sample_frame, show="headings", height=8)
        self.sample_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars for sample data
        v_scrollbar = ttk.Scrollbar(sample_frame, orient="vertical", command=self.sample_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.sample_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(sample_frame, orient="horizontal", command=self.sample_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.sample_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Sample statistics
        self.sample_stats_var = tk.StringVar()
        self.sample_stats_var.set("")
        stats_label = ttk.Label(preview_frame, textvariable=self.sample_stats_var,
                               font=('Arial', 9), foreground="gray")
        stats_label.grid(row=2, column=0, pady=(10, 0))
        
    def set_file_data(self, file1_info: Optional[FileInfo], file2_info: Optional[FileInfo],
                      file1_data: Optional[pd.DataFrame], file2_data: Optional[pd.DataFrame]):
        """
        Set the file data for column mapping.
        
        Args:
            file1_info: FileInfo object for first file
            file2_info: FileInfo object for second file
            file1_data: DataFrame for first file
            file2_data: DataFrame for second file
        """
        self.file1_info = file1_info
        self.file2_info = file2_info
        self.file1_data = file1_data
        self.file2_data = file2_data
        
        # Update column dropdowns
        self._populate_column_dropdowns()
        
        # Reset selection
        self.selected_file1_column = None
        self.selected_file2_column = None
        self.file1_column_var.set("")
        self.file2_column_var.set("")
        
        # Reset validation
        self._update_validation_display()
        self._clear_column_info()
        self._clear_sample_preview()
        
    def _populate_column_dropdowns(self):
        """Populate the column dropdown menus based on loaded files."""
        # File 1 columns
        if self.file1_info and self.file1_info.columns:
            self.file1_column_combo['values'] = self.file1_info.columns
            self.file1_column_combo['state'] = 'readonly'
        else:
            self.file1_column_combo['values'] = []
            self.file1_column_combo['state'] = 'disabled'
            
        # File 2 columns
        if self.file2_info and self.file2_info.columns:
            self.file2_column_combo['values'] = self.file2_info.columns
            self.file2_column_combo['state'] = 'readonly'
        else:
            self.file2_column_combo['values'] = []
            self.file2_column_combo['state'] = 'disabled'
            
    def _on_column_selection_changed(self, event=None):
        """Handle column selection change events."""
        # Get selected columns
        self.selected_file1_column = self.file1_column_var.get() if self.file1_column_var.get() else None
        self.selected_file2_column = self.file2_column_var.get() if self.file2_column_var.get() else None
        
        # Update column information
        self._update_column_info()
        
        # Validate column compatibility
        self._validate_column_compatibility()
        
        # Update sample preview
        self._update_sample_preview()
        
        # Notify callback
        if self.on_mapping_changed:
            self.on_mapping_changed(self.selected_file1_column, self.selected_file2_column)
            
    def _update_column_info(self):
        """Update column information display with data types and sample values."""
        # File 1 column info
        if self.selected_file1_column and self.file1_data is not None:
            column_data = self.file1_data[self.selected_file1_column]
            
            # Data type
            dtype_str = self._get_readable_dtype(column_data.dtype)
            self.file1_dtype_var.set(dtype_str)
            
            # Non-null count
            non_null_count = column_data.notna().sum()
            total_count = len(column_data)
            self.file1_count_var.set(f"{non_null_count} / {total_count}")
            
            # Sample values
            sample_values = self._get_sample_values(column_data)
            self.file1_samples_var.set(sample_values)
        else:
            self.file1_dtype_var.set("-")
            self.file1_count_var.set("-")
            self.file1_samples_var.set("-")
            
        # File 2 column info
        if self.selected_file2_column and self.file2_data is not None:
            column_data = self.file2_data[self.selected_file2_column]
            
            # Data type
            dtype_str = self._get_readable_dtype(column_data.dtype)
            self.file2_dtype_var.set(dtype_str)
            
            # Non-null count
            non_null_count = column_data.notna().sum()
            total_count = len(column_data)
            self.file2_count_var.set(f"{non_null_count} / {total_count}")
            
            # Sample values
            sample_values = self._get_sample_values(column_data)
            self.file2_samples_var.set(sample_values)
        else:
            self.file2_dtype_var.set("-")
            self.file2_count_var.set("-")
            self.file2_samples_var.set("-")
            
    def _get_readable_dtype(self, dtype) -> str:
        """
        Convert pandas dtype to readable string.
        
        Args:
            dtype: pandas dtype
            
        Returns:
            Human-readable data type string
        """
        if pd.api.types.is_integer_dtype(dtype):
            return "Integer"
        elif pd.api.types.is_float_dtype(dtype):
            return "Float"
        elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
            return "Text"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "Date/Time"
        elif pd.api.types.is_bool_dtype(dtype):
            return "Boolean"
        else:
            return str(dtype)
            
    def _get_sample_values(self, column_data: pd.Series, max_samples: int = 5) -> str:
        """
        Get sample values from a column.
        
        Args:
            column_data: pandas Series containing column data
            max_samples: Maximum number of sample values to return
            
        Returns:
            Comma-separated string of sample values
        """
        # Get non-null unique values
        unique_values = column_data.dropna().unique()
        
        if len(unique_values) == 0:
            return "No data"
            
        # Take first few unique values
        sample_values = unique_values[:max_samples]
        
        # Convert to strings and truncate if too long
        sample_strings = []
        for val in sample_values:
            val_str = str(val)
            if len(val_str) > 20:
                val_str = val_str[:17] + "..."
            sample_strings.append(val_str)
            
        result = ", ".join(sample_strings)
        
        if len(unique_values) > max_samples:
            result += f" ... ({len(unique_values)} unique values)"
            
        return result
        
    def _validate_column_compatibility(self):
        """Validate compatibility between selected columns."""
        if not self.selected_file1_column or not self.selected_file2_column:
            self.is_mapping_valid = False
            self.validation_message = "Please select columns from both files"
            self._update_validation_display()
            return
            
        if self.file1_data is None or self.file2_data is None:
            self.is_mapping_valid = False
            self.validation_message = "File data not available"
            self._update_validation_display()
            return
            
        try:
            col1_data = self.file1_data[self.selected_file1_column]
            col2_data = self.file2_data[self.selected_file2_column]
            
            # Check data type compatibility
            compatibility_result = self._check_data_type_compatibility(col1_data, col2_data)
            
            if compatibility_result['compatible']:
                self.is_mapping_valid = True
                self.validation_message = compatibility_result['message']
            else:
                self.is_mapping_valid = False
                self.validation_message = compatibility_result['message']
                
        except Exception as e:
            self.is_mapping_valid = False
            self.validation_message = f"Error validating columns: {str(e)}"
            
        self._update_validation_display()
        
    def _check_data_type_compatibility(self, col1: pd.Series, col2: pd.Series) -> Dict[str, Any]:
        """
        Check if two columns have compatible data types for comparison.
        
        Args:
            col1: First column data
            col2: Second column data
            
        Returns:
            Dictionary with compatibility result and message
        """
        # Get data types
        dtype1 = col1.dtype
        dtype2 = col2.dtype
        
        # Check for empty columns
        if col1.dropna().empty or col2.dropna().empty:
            return {
                'compatible': False,
                'message': "One or both columns contain no data"
            }
        
        # Both numeric types
        if (pd.api.types.is_numeric_dtype(dtype1) and pd.api.types.is_numeric_dtype(dtype2)):
            return {
                'compatible': True,
                'message': "✓ Compatible: Both columns contain numeric data"
            }
            
        # Both string/object types
        if ((pd.api.types.is_string_dtype(dtype1) or pd.api.types.is_object_dtype(dtype1)) and
            (pd.api.types.is_string_dtype(dtype2) or pd.api.types.is_object_dtype(dtype2))):
            return {
                'compatible': True,
                'message': "✓ Compatible: Both columns contain text data"
            }
            
        # Both datetime types
        if (pd.api.types.is_datetime64_any_dtype(dtype1) and pd.api.types.is_datetime64_any_dtype(dtype2)):
            return {
                'compatible': True,
                'message': "✓ Compatible: Both columns contain date/time data"
            }
            
        # Mixed types - check if they can be compared as strings
        try:
            # Try to convert both to string and see if we get reasonable results
            str1_sample = col1.dropna().head(10).astype(str)
            str2_sample = col2.dropna().head(10).astype(str)
            
            # Check if conversion looks reasonable (not all "nan" or empty)
            if not str1_sample.empty and not str2_sample.empty:
                return {
                    'compatible': True,
                    'message': "⚠ Compatible: Different data types, will compare as text"
                }
        except:
            pass
            
        return {
            'compatible': False,
            'message': f"✗ Incompatible: Cannot compare {self._get_readable_dtype(dtype1)} with {self._get_readable_dtype(dtype2)}"
        }
        
    def _update_validation_display(self):
        """Update the validation indicator and message display."""
        if not self.selected_file1_column or not self.selected_file2_column:
            self.validation_icon_var.set("")
            self.validation_message_var.set("Please select columns from both files")
            self.validation_message_label.configure(foreground="gray")
        elif self.is_mapping_valid:
            self.validation_icon_var.set("✓")
            self.validation_message_var.set(self.validation_message)
            self.validation_message_label.configure(foreground="green")
        else:
            self.validation_icon_var.set("✗")
            self.validation_message_var.set(self.validation_message)
            self.validation_message_label.configure(foreground="red")
            
    def _update_sample_preview(self):
        """Update the sample preview showing matching values between selected columns."""
        # Clear existing preview
        self._clear_sample_preview()
        
        if (not self.selected_file1_column or not self.selected_file2_column or
            self.file1_data is None or self.file2_data is None or not self.is_mapping_valid):
            return
            
        try:
            # Get column data
            col1_data = self.file1_data[self.selected_file1_column].dropna()
            col2_data = self.file2_data[self.selected_file2_column].dropna()
            
            # Find matching values
            matches = self._find_sample_matches(col1_data, col2_data)
            
            if matches:
                self._display_sample_matches(matches)
            else:
                self.sample_stats_var.set("No matching values found in sample data")
                
        except Exception as e:
            self.sample_stats_var.set(f"Error generating sample preview: {str(e)}")
            
    def _find_sample_matches(self, col1: pd.Series, col2: pd.Series, max_matches: int = 20) -> List[Tuple[Any, int, int]]:
        """
        Find sample matching values between two columns.
        
        Args:
            col1: First column data
            col2: Second column data
            max_matches: Maximum number of matches to return
            
        Returns:
            List of tuples (value, count_in_col1, count_in_col2)
        """
        try:
            # Convert to comparable format (strings for mixed types)
            if col1.dtype != col2.dtype:
                col1_compare = col1.astype(str)
                col2_compare = col2.astype(str)
            else:
                col1_compare = col1
                col2_compare = col2
                
            # Get value counts for both columns
            col1_counts = col1_compare.value_counts()
            col2_counts = col2_compare.value_counts()
            
            # Find common values
            common_values = set(col1_counts.index) & set(col2_counts.index)
            
            if not common_values:
                return []
                
            # Create matches list with counts
            matches = []
            for value in list(common_values)[:max_matches]:
                matches.append((
                    value,
                    col1_counts[value],
                    col2_counts[value]
                ))
                
            # Sort by total frequency (descending)
            matches.sort(key=lambda x: x[1] + x[2], reverse=True)
            
            return matches
            
        except Exception:
            return []
            
    def _display_sample_matches(self, matches: List[Tuple[Any, int, int]]):
        """
        Display sample matches in the preview tree.
        
        Args:
            matches: List of tuples (value, count_in_col1, count_in_col2)
        """
        # Configure tree columns
        columns = ("Value", "Count in File 1", "Count in File 2")
        self.sample_tree["columns"] = columns
        
        # Set column headings and widths
        for col in columns:
            self.sample_tree.heading(col, text=col)
            if col == "Value":
                self.sample_tree.column(col, width=200, minwidth=100)
            else:
                self.sample_tree.column(col, width=120, minwidth=80, anchor="center")
                
        # Insert match data
        for value, count1, count2 in matches:
            # Truncate long values for display
            display_value = str(value)
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."
                
            self.sample_tree.insert("", "end", values=(display_value, count1, count2))
            
        # Update statistics
        total_matches = len(matches)
        total_unique_file1 = len(self.file1_data[self.selected_file1_column].dropna().unique())
        total_unique_file2 = len(self.file2_data[self.selected_file2_column].dropna().unique())
        
        stats_text = f"Showing {total_matches} matching values"
        if total_matches == 20:  # Max matches reached
            stats_text += " (limited to first 20)"
        stats_text += f" | File 1: {total_unique_file1} unique | File 2: {total_unique_file2} unique"
        
        self.sample_stats_var.set(stats_text)
        
    def _clear_sample_preview(self):
        """Clear the sample preview display."""
        self.sample_tree.delete(*self.sample_tree.get_children())
        self.sample_tree["columns"] = ()
        self.sample_stats_var.set("")
        
    def _clear_column_info(self):
        """Clear the column information display."""
        self.file1_dtype_var.set("-")
        self.file1_count_var.set("-")
        self.file1_samples_var.set("-")
        self.file2_dtype_var.set("-")
        self.file2_count_var.set("-")
        self.file2_samples_var.set("-")
        
    def validate_input(self) -> bool:
        """
        Validate the current input state of the component.
        
        Returns:
            True if input is valid, False otherwise
        """
        return self.is_mapping_valid
        
    def reset_component(self) -> None:
        """Reset the component to its initial state."""
        self.file1_info = None
        self.file2_info = None
        self.file1_data = None
        self.file2_data = None
        self.selected_file1_column = None
        self.selected_file2_column = None
        self.is_mapping_valid = False
        self.validation_message = ""
        
        # Reset UI
        self.file1_column_var.set("")
        self.file2_column_var.set("")
        self.file1_column_combo['values'] = []
        self.file2_column_combo['values'] = []
        self.file1_column_combo['state'] = 'disabled'
        self.file2_column_combo['state'] = 'disabled'
        
        self._update_validation_display()
        self._clear_column_info()
        self._clear_sample_preview()
        
    def get_component_data(self) -> Dict[str, Any]:
        """
        Get the current data/state from the component.
        
        Returns:
            Dictionary containing component data
        """
        return {
            'file1_column': self.selected_file1_column,
            'file2_column': self.selected_file2_column,
            'is_valid': self.is_mapping_valid,
            'validation_message': self.validation_message
        }
        
    def get_selected_columns(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the currently selected columns.
        
        Returns:
            Tuple of (file1_column, file2_column)
        """
        return self.selected_file1_column, self.selected_file2_column
        
    def is_valid_mapping(self) -> bool:
        """
        Check if the current column mapping is valid.
        
        Returns:
            True if mapping is valid, False otherwise
        """
        return self.is_mapping_valid
        
    def _add_tooltips(self):
        """Add tooltips to column mapping components."""
        # Column selection tooltips
        file1_combo_tooltip = ("Select the column from File 1 that contains the values you want to compare. "
                              "Choose columns with consistent data like emails, IDs, or codes.")
        file2_combo_tooltip = ("Select the column from File 2 that contains the values you want to compare. "
                              "This column will be compared against the File 1 column.")
        
        self.help_service.add_tooltip(self.file1_column_combo, file1_combo_tooltip)
        self.help_service.add_tooltip(self.file2_column_combo, file2_combo_tooltip)
        
        # Validation indicator tooltip
        validation_tooltip = ("Shows compatibility between selected columns:\n"
                            "✓ Green = Compatible data types\n"
                            "⚠ Orange = Mixed types (will compare as text)\n"
                            "✗ Red = Incompatible types")
        
        self.help_service.add_tooltip(self.validation_icon_label, validation_tooltip)
        
        # Sample preview tooltip
        sample_tooltip = ("Shows values that appear in both selected columns. "
                         "Use this to verify you've selected the correct columns for comparison.")
        
        self.help_service.add_tooltip(self.sample_tree, sample_tooltip)