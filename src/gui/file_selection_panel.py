"""
File selection panel for the File Comparison Tool.

This module contains the FileSelectionPanel class which provides an interface
for selecting two files to compare, with file validation, preview functionality,
and drag-and-drop support.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, Callable, Dict, Any
import pandas as pd

from services.file_parser_service import FileParserService, FileParsingError, UnsupportedFileFormatError
from models.data_models import FileInfo
from services.help_service import HelpService


class FileSelectionPanel:
    """
    Panel for selecting and previewing files for comparison.
    
    Provides file browse buttons, drag-and-drop functionality, file validation
    with visual feedback, and preview of file contents.
    """
    
    def __init__(self, parent_frame: tk.Widget, on_files_changed: Optional[Callable] = None):
        """
        Initialize the file selection panel.
        
        Args:
            parent_frame: Parent tkinter widget to contain this panel
            on_files_changed: Callback function called when files are selected/changed
        """
        self.parent_frame = parent_frame
        self.on_files_changed = on_files_changed
        self.file_parser = FileParserService()
        self.help_service = HelpService()
        
        # File information storage
        self.file1_info: Optional[FileInfo] = None
        self.file2_info: Optional[FileInfo] = None
        self.file1_preview: Optional[pd.DataFrame] = None
        self.file2_preview: Optional[pd.DataFrame] = None
        
        # Create the main panel
        self.panel = ttk.Frame(parent_frame)
        self.panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights for responsive layout
        self.panel.grid_rowconfigure(2, weight=1)  # Preview area
        self.panel.grid_columnconfigure(0, weight=1)
        self.panel.grid_columnconfigure(1, weight=1)
        
        self._create_widgets()
        self._setup_drag_drop()
        self._add_tooltips()
        
    def _create_widgets(self):
        """Create all GUI widgets for the file selection panel."""
        # Title
        title_label = ttk.Label(self.panel, text="Select Files to Compare", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # File selection frames
        self._create_file_selection_frame(1, "First File", 0)
        self._create_file_selection_frame(2, "Second File", 1)
        
        # Preview area
        self._create_preview_area()
        
    def _create_file_selection_frame(self, file_num: int, title: str, column: int):
        """
        Create file selection frame for a single file.
        
        Args:
            file_num: File number (1 or 2)
            title: Title for the file selection frame
            column: Grid column to place the frame
        """
        # Main frame for this file
        frame = ttk.LabelFrame(self.panel, text=title, padding="10")
        frame.grid(row=1, column=column, sticky="nsew", padx=(0, 5) if column == 0 else (5, 0))
        frame.grid_columnconfigure(0, weight=1)
        
        # File path display with validation indicator
        path_frame = ttk.Frame(frame)
        path_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        path_frame.grid_columnconfigure(1, weight=1)
        
        # Validation indicator (checkmark or error icon)
        indicator_var = tk.StringVar()
        indicator_label = ttk.Label(path_frame, textvariable=indicator_var, 
                                   font=('Arial', 12), width=2)
        indicator_label.grid(row=0, column=0, padx=(0, 5))
        
        # File path display
        path_var = tk.StringVar()
        path_var.set("No file selected")
        path_label = ttk.Label(path_frame, textvariable=path_var, 
                              foreground="gray", relief="sunken", 
                              padding="5", anchor="w")
        path_label.grid(row=0, column=1, sticky="ew")
        
        # Browse button
        browse_button = ttk.Button(frame, text="Browse...", 
                                  command=lambda: self._browse_file(file_num))
        browse_button.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Store button reference for tooltips
        setattr(self, f'file{file_num}_browse_button', browse_button)
        
        # File info display
        info_frame = ttk.Frame(frame)
        info_frame.grid(row=2, column=0, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        # File type and size
        ttk.Label(info_frame, text="Type:").grid(row=0, column=0, sticky="w")
        type_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=type_var, foreground="blue").grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        ttk.Label(info_frame, text="Size:").grid(row=1, column=0, sticky="w")
        size_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=size_var, foreground="blue").grid(row=1, column=1, sticky="w", padx=(5, 0))
        
        # Columns and rows
        ttk.Label(info_frame, text="Columns:").grid(row=2, column=0, sticky="w")
        cols_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=cols_var, foreground="blue").grid(row=2, column=1, sticky="w", padx=(5, 0))
        
        ttk.Label(info_frame, text="Rows:").grid(row=3, column=0, sticky="w")
        rows_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=rows_var, foreground="blue").grid(row=3, column=1, sticky="w", padx=(5, 0))
        
        # Store references to widgets for later updates
        setattr(self, f'file{file_num}_frame', frame)
        setattr(self, f'file{file_num}_indicator_var', indicator_var)
        setattr(self, f'file{file_num}_path_var', path_var)
        setattr(self, f'file{file_num}_path_label', path_label)
        setattr(self, f'file{file_num}_type_var', type_var)
        setattr(self, f'file{file_num}_size_var', size_var)
        setattr(self, f'file{file_num}_cols_var', cols_var)
        setattr(self, f'file{file_num}_rows_var', rows_var)
        
    def _create_preview_area(self):
        """Create the file preview area showing first few rows of data."""
        # Preview frame
        preview_frame = ttk.LabelFrame(self.panel, text="File Preview", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(20, 0))
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Notebook for tabbed preview
        self.preview_notebook = ttk.Notebook(preview_frame)
        self.preview_notebook.grid(row=0, column=0, sticky="nsew")
        
        # Create preview tabs
        self._create_preview_tab("File 1", 1)
        self._create_preview_tab("File 2", 2)
        
    def _create_preview_tab(self, title: str, file_num: int):
        """
        Create a preview tab for a file.
        
        Args:
            title: Tab title
            file_num: File number (1 or 2)
        """
        # Tab frame
        tab_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(tab_frame, text=title)
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for data display
        tree_frame = ttk.Frame(tab_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview with scrollbars
        tree = ttk.Treeview(tree_frame, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Status label for empty state
        status_var = tk.StringVar()
        status_var.set("No file selected")
        status_label = ttk.Label(tab_frame, textvariable=status_var, 
                                foreground="gray", font=('Arial', 10))
        status_label.grid(row=1, column=0, pady=10)
        
        # Store references
        setattr(self, f'preview_tree_{file_num}', tree)
        setattr(self, f'preview_status_var_{file_num}', status_var)
        setattr(self, f'preview_status_label_{file_num}', status_label)
        
    def _setup_drag_drop(self):
        """Set up drag and drop functionality for file selection."""
        # Note: Basic tkinter doesn't have full drag-and-drop support
        # This is a placeholder for future enhancement with tkinterdnd2
        # For now, we'll add visual hints about drag-and-drop capability
        
        # Add drag-and-drop hint labels
        hint1 = ttk.Label(self.file1_frame, text="(Drag & drop files here)", 
                         font=('Arial', 8), foreground="gray")
        hint1.grid(row=3, column=0, pady=(5, 0))
        
        hint2 = ttk.Label(self.file2_frame, text="(Drag & drop files here)", 
                         font=('Arial', 8), foreground="gray")
        hint2.grid(row=3, column=0, pady=(5, 0))
        
    def _browse_file(self, file_num: int):
        """
        Open file dialog to browse for a file.
        
        Args:
            file_num: File number (1 or 2)
        """
        filetypes = [
            ("Supported files", "*.csv;*.xlsx;*.xls"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx;*.xls"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title=f"Select File {file_num}",
            filetypes=filetypes
        )
        
        if file_path:
            self._load_file(file_path, file_num)
            
    def _handle_drop(self, event, file_num: int):
        """
        Handle file drop event.
        Note: This is a placeholder for future drag-and-drop implementation.
        
        Args:
            event: Drop event
            file_num: File number (1 or 2)
        """
        # Placeholder for drag-and-drop functionality
        # Would require tkinterdnd2 library for full implementation
        pass
        
    def _load_file(self, file_path: str, file_num: int):
        """
        Load and validate a file.
        
        Args:
            file_path: Path to the file to load
            file_num: File number (1 or 2)
        """
        try:
            # Validate and get file info
            file_info = self.file_parser.create_file_info(file_path)
            
            # Load preview data (first 10 rows)
            df = self.file_parser.parse_file(file_path)
            preview_df = df.head(10)
            
            # Store file information
            setattr(self, f'file{file_num}_info', file_info)
            setattr(self, f'file{file_num}_preview', preview_df)
            
            # Update UI
            self._update_file_display(file_num, file_info, success=True)
            self._update_preview(file_num, preview_df)
            
            # Notify callback with current file info
            if self.on_files_changed:
                self.on_files_changed(self.file1_info, self.file2_info)
                
        except (FileNotFoundError, UnsupportedFileFormatError, FileParsingError) as e:
            # Handle known errors
            self._show_file_error(file_num, str(e))
            
        except Exception as e:
            # Handle unexpected errors
            self._show_file_error(file_num, f"Unexpected error: {str(e)}")
            
    def _update_file_display(self, file_num: int, file_info: FileInfo, success: bool = True):
        """
        Update the file display with file information.
        
        Args:
            file_num: File number (1 or 2)
            file_info: FileInfo object with file metadata
            success: Whether the file was loaded successfully
        """
        # Update validation indicator
        indicator_var = getattr(self, f'file{file_num}_indicator_var')
        path_var = getattr(self, f'file{file_num}_path_var')
        path_label = getattr(self, f'file{file_num}_path_label')
        
        if success:
            indicator_var.set("✓")
            path_var.set(os.path.basename(file_info.file_path))
            path_label.configure(foreground="black")
        else:
            indicator_var.set("✗")
            path_label.configure(foreground="red")
            
        # Update file information
        type_var = getattr(self, f'file{file_num}_type_var')
        size_var = getattr(self, f'file{file_num}_size_var')
        cols_var = getattr(self, f'file{file_num}_cols_var')
        rows_var = getattr(self, f'file{file_num}_rows_var')
        
        if success:
            type_var.set(file_info.file_type.upper())
            size_var.set(self._format_file_size(file_info.file_size))
            cols_var.set(str(len(file_info.columns)))
            rows_var.set(str(file_info.row_count))
        else:
            type_var.set("-")
            size_var.set("-")
            cols_var.set("-")
            rows_var.set("-")
            
    def _update_preview(self, file_num: int, df: pd.DataFrame):
        """
        Update the preview display with DataFrame data.
        
        Args:
            file_num: File number (1 or 2)
            df: DataFrame to display
        """
        tree = getattr(self, f'preview_tree_{file_num}')
        status_var = getattr(self, f'preview_status_var_{file_num}')
        
        # Clear existing data
        tree.delete(*tree.get_children())
        
        if df.empty:
            status_var.set("File is empty")
            return
            
        # Configure columns
        columns = list(df.columns)
        tree["columns"] = columns
        
        # Set column headings and widths
        for col in columns:
            tree.heading(col, text=str(col))
            tree.column(col, width=100, minwidth=50)
            
        # Insert data rows
        for index, row in df.iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            tree.insert("", "end", values=values)
            
        # Update status
        total_rows = getattr(self, f'file{file_num}_info').row_count if hasattr(self, f'file{file_num}_info') else len(df)
        status_var.set(f"Showing first {len(df)} of {total_rows} rows")
        
    def _show_file_error(self, file_num: int, error_message: str):
        """
        Show file error and update UI accordingly.
        
        Args:
            file_num: File number (1 or 2)
            error_message: Error message to display
        """
        # Clear file information
        setattr(self, f'file{file_num}_info', None)
        setattr(self, f'file{file_num}_preview', None)
        
        # Update UI to show error state
        indicator_var = getattr(self, f'file{file_num}_indicator_var')
        path_var = getattr(self, f'file{file_num}_path_var')
        path_label = getattr(self, f'file{file_num}_path_label')
        
        indicator_var.set("✗")
        path_var.set("Error loading file")
        path_label.configure(foreground="red")
        
        # Clear file info
        type_var = getattr(self, f'file{file_num}_type_var')
        size_var = getattr(self, f'file{file_num}_size_var')
        cols_var = getattr(self, f'file{file_num}_cols_var')
        rows_var = getattr(self, f'file{file_num}_rows_var')
        
        type_var.set("-")
        size_var.set("-")
        cols_var.set("-")
        rows_var.set("-")
        
        # Clear preview
        tree = getattr(self, f'preview_tree_{file_num}')
        status_var = getattr(self, f'preview_status_var_{file_num}')
        
        tree.delete(*tree.get_children())
        tree["columns"] = ()
        status_var.set("Error loading file")
        
        # Show error dialog
        messagebox.showerror("File Error", error_message)
        
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted file size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
    def get_selected_files(self) -> Dict[str, Optional[FileInfo]]:
        """
        Get information about currently selected files.
        
        Returns:
            Dictionary with file1 and file2 FileInfo objects
        """
        return {
            'file1': self.file1_info,
            'file2': self.file2_info
        }
        
    def are_files_valid(self) -> bool:
        """
        Check if both files are selected and valid.
        
        Returns:
            True if both files are valid, False otherwise
        """
        return self.file1_info is not None and self.file2_info is not None
        
    def clear_files(self):
        """Clear all selected files and reset the panel."""
        self.file1_info = None
        self.file2_info = None
        self.file1_preview = None
        self.file2_preview = None
        
        # Reset UI for both files
        for file_num in [1, 2]:
            indicator_var = getattr(self, f'file{file_num}_indicator_var')
            path_var = getattr(self, f'file{file_num}_path_var')
            path_label = getattr(self, f'file{file_num}_path_label')
            
            indicator_var.set("")
            path_var.set("No file selected")
            path_label.configure(foreground="gray")
            
            # Clear file info
            type_var = getattr(self, f'file{file_num}_type_var')
            size_var = getattr(self, f'file{file_num}_size_var')
            cols_var = getattr(self, f'file{file_num}_cols_var')
            rows_var = getattr(self, f'file{file_num}_rows_var')
            
            type_var.set("")
            size_var.set("")
            cols_var.set("")
            rows_var.set("")
            
            # Clear preview
            tree = getattr(self, f'preview_tree_{file_num}')
            status_var = getattr(self, f'preview_status_var_{file_num}')
            
            tree.delete(*tree.get_children())
            tree["columns"] = ()
            status_var.set("No file selected")
            
        # Notify callback with cleared file info
        if self.on_files_changed:
            self.on_files_changed(self.file1_info, self.file2_info)
            
    def _add_tooltips(self):
        """Add tooltips to file selection components."""
        # Title tooltip
        title_tooltip = ("Select two files to compare. Supported formats: CSV (.csv) and Excel (.xlsx, .xls). "
                        "Files will be validated and previewed automatically.")
        
        # Browse button tooltips
        browse1_tooltip = ("Click to select the first file for comparison. "
                          "Supported formats: CSV and Excel files.")
        browse2_tooltip = ("Click to select the second file for comparison. "
                          "Supported formats: CSV and Excel files.")
        
        # Add tooltips to browse buttons (need to store references)
        if hasattr(self, 'file1_browse_button'):
            self.help_service.add_tooltip(self.file1_browse_button, browse1_tooltip)
        if hasattr(self, 'file2_browse_button'):
            self.help_service.add_tooltip(self.file2_browse_button, browse2_tooltip)
            
        # Preview tooltips
        preview_tooltip = ("Preview shows the first 10 rows of your file data. "
                          "Use this to verify the file loaded correctly and has the expected structure.")
        
        if hasattr(self, 'preview_notebook'):
            self.help_service.add_tooltip(self.preview_notebook, preview_tooltip)