"""
Results display and summary panel for the File Comparison Tool.

This module contains the ResultsPanel class which displays processed data,
summary statistics, pagination for large result sets, and export controls
with format selection.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, Callable, Dict, Any
import pandas as pd
from datetime import datetime

from models.data_models import OperationResult
from services.export_service import ExportService
from services.help_service import HelpService


class ResultsPanel:
    """
    Panel for displaying comparison results and providing export functionality.
    
    Shows processed data in a table widget with pagination, summary statistics,
    and export controls with format selection.
    """
    
    def __init__(self, parent_frame: tk.Widget, on_export_complete: Optional[Callable] = None):
        """
        Initialize the results panel.
        
        Args:
            parent_frame: Parent tkinter widget to contain this panel
            on_export_complete: Callback function called when export is complete
        """
        self.parent_frame = parent_frame
        self.on_export_complete = on_export_complete
        self.export_service = ExportService()
        self.help_service = HelpService()
        
        # Results data storage
        self.operation_result: Optional[OperationResult] = None
        self.current_page = 0
        self.rows_per_page = 100
        self.total_pages = 0
        
        # Create the main panel
        self.panel = ttk.Frame(parent_frame)
        self.panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights for responsive layout
        self.panel.grid_rowconfigure(1, weight=1)  # Results table area
        self.panel.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
        self._add_tooltips()
        
    def _create_widgets(self):
        """Create all GUI widgets for the results panel."""
        # Title and summary section
        self._create_summary_section()
        
        # Results table with pagination
        self._create_results_table()
        
        # Export controls
        self._create_export_section()
        
    def _create_summary_section(self):
        """Create the summary statistics section."""
        # Summary frame
        summary_frame = ttk.LabelFrame(self.panel, text="Operation Summary", padding="10")
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_columnconfigure(3, weight=1)
        
        # Operation type
        ttk.Label(summary_frame, text="Operation:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="w", padx=(0, 5))
        self.operation_var = tk.StringVar()
        self.operation_var.set("No operation performed")
        ttk.Label(summary_frame, textvariable=self.operation_var, 
                 foreground="blue").grid(row=0, column=1, sticky="w")
        
        # Processing time
        ttk.Label(summary_frame, text="Processing Time:", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky="w", padx=(20, 5))
        self.time_var = tk.StringVar()
        self.time_var.set("-")
        ttk.Label(summary_frame, textvariable=self.time_var, 
                 foreground="blue").grid(row=0, column=3, sticky="w")
        
        # Row counts
        ttk.Label(summary_frame, text="Original Rows:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.original_count_var = tk.StringVar()
        self.original_count_var.set("-")
        ttk.Label(summary_frame, textvariable=self.original_count_var, 
                 foreground="blue").grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        ttk.Label(summary_frame, text="Result Rows:", font=('Arial', 10, 'bold')).grid(
            row=1, column=2, sticky="w", padx=(20, 5), pady=(5, 0))
        self.result_count_var = tk.StringVar()
        self.result_count_var.set("-")
        ttk.Label(summary_frame, textvariable=self.result_count_var, 
                 foreground="blue").grid(row=1, column=3, sticky="w", pady=(5, 0))
        
        # Summary description
        ttk.Label(summary_frame, text="Summary:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky="nw", padx=(0, 5), pady=(10, 0))
        self.summary_var = tk.StringVar()
        self.summary_var.set("No results to display")
        summary_label = ttk.Label(summary_frame, textvariable=self.summary_var, 
                                 wraplength=600, justify="left")
        summary_label.grid(row=2, column=1, columnspan=3, sticky="w", pady=(10, 0))
        
    def _create_results_table(self):
        """Create the results table with pagination controls."""
        # Results frame
        results_frame = ttk.LabelFrame(self.panel, text="Results Data", padding="10")
        results_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        results_frame.grid_rowconfigure(1, weight=1)  # Table area
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Pagination controls (top)
        self._create_pagination_controls(results_frame, 0)
        
        # Table with scrollbars
        table_frame = ttk.Frame(results_frame)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for data display
        self.results_tree = ttk.Treeview(table_frame, show="headings")
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", 
                                   command=self.results_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", 
                                   command=self.results_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.results_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Empty state message
        self.empty_state_var = tk.StringVar()
        self.empty_state_var.set("No results to display. Complete a comparison operation to see results here.")
        self.empty_state_label = ttk.Label(results_frame, textvariable=self.empty_state_var,
                                          foreground="gray", font=('Arial', 12),
                                          anchor="center")
        self.empty_state_label.grid(row=1, column=0, pady=50)
        
        # Pagination controls (bottom)
        self._create_pagination_controls(results_frame, 2)
        
    def _create_pagination_controls(self, parent: tk.Widget, row: int):
        """
        Create pagination controls.
        
        Args:
            parent: Parent widget
            row: Grid row to place controls
        """
        pagination_frame = ttk.Frame(parent)
        pagination_frame.grid(row=row, column=0, sticky="ew")
        pagination_frame.grid_columnconfigure(2, weight=1)
        
        # Previous button
        self.prev_button = ttk.Button(pagination_frame, text="← Previous", 
                                     command=self._previous_page, state="disabled")
        self.prev_button.grid(row=0, column=0, padx=(0, 10))
        
        # Next button
        self.next_button = ttk.Button(pagination_frame, text="Next →", 
                                     command=self._next_page, state="disabled")
        self.next_button.grid(row=0, column=1, padx=(0, 20))
        
        # Page info
        self.page_info_var = tk.StringVar()
        self.page_info_var.set("No data")
        ttk.Label(pagination_frame, textvariable=self.page_info_var).grid(
            row=0, column=2, sticky="w")
        
        # Rows per page selector
        ttk.Label(pagination_frame, text="Rows per page:").grid(
            row=0, column=3, sticky="e", padx=(20, 5))
        
        self.rows_per_page_var = tk.StringVar()
        self.rows_per_page_var.set("100")
        rows_combo = ttk.Combobox(pagination_frame, textvariable=self.rows_per_page_var,
                                 values=["50", "100", "200", "500"], width=8, state="readonly")
        rows_combo.grid(row=0, column=4, sticky="e")
        rows_combo.bind("<<ComboboxSelected>>", self._on_rows_per_page_changed)
        
    def _create_export_section(self):
        """Create the export controls section."""
        # Export frame
        export_frame = ttk.LabelFrame(self.panel, text="Export Results", padding="10")
        export_frame.grid(row=2, column=0, sticky="ew")
        export_frame.grid_columnconfigure(1, weight=1)
        
        # Format selection
        ttk.Label(export_frame, text="Export Format:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="w", padx=(0, 10))
        
        self.export_format_var = tk.StringVar()
        self.export_format_var.set("csv")
        
        format_frame = ttk.Frame(export_frame)
        format_frame.grid(row=0, column=1, sticky="w")
        
        ttk.Radiobutton(format_frame, text="CSV", variable=self.export_format_var, 
                       value="csv").grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(format_frame, text="Excel", variable=self.export_format_var, 
                       value="excel").grid(row=0, column=1)
        
        # Export button
        self.export_button = ttk.Button(export_frame, text="Export Results", 
                                       command=self._export_results, state="disabled")
        self.export_button.grid(row=0, column=2, sticky="e", padx=(20, 0))
        
        # Export status
        self.export_status_var = tk.StringVar()
        self.export_status_var.set("")
        self.export_status_label = ttk.Label(export_frame, textvariable=self.export_status_var,
                                            foreground="green")
        self.export_status_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 0))
        
    def display_results(self, operation_result: OperationResult):
        """
        Display the results of a comparison operation.
        
        Args:
            operation_result: OperationResult containing the processed data and metadata
        """
        self.operation_result = operation_result
        self.current_page = 0
        
        # Update summary information
        self._update_summary()
        
        # Calculate pagination
        total_rows = len(operation_result.result_data)
        self.total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
        
        # Display data
        self._update_table_display()
        
        # Enable export button
        self.export_button.configure(state="normal")
        
        # Hide empty state message
        self.empty_state_label.grid_remove()
        
    def _update_summary(self):
        """Update the summary statistics display."""
        if not self.operation_result:
            return
            
        # Format operation type for display
        operation_display = {
            'remove_matches': 'Remove Matches',
            'keep_matches': 'Keep Only Matches', 
            'find_common': 'Find Common Values',
            'find_unique': 'Find Unique Values'
        }.get(self.operation_result.operation_type, self.operation_result.operation_type)
        
        self.operation_var.set(operation_display)
        self.time_var.set(f"{self.operation_result.processing_time:.2f}s")
        self.original_count_var.set(f"{self.operation_result.original_count:,}")
        self.result_count_var.set(f"{self.operation_result.result_count:,}")
        self.summary_var.set(self.operation_result.summary)
        
    def _update_table_display(self):
        """Update the table display with current page data."""
        if not self.operation_result:
            return
            
        # Clear existing data
        self.results_tree.delete(*self.results_tree.get_children())
        
        df = self.operation_result.result_data
        
        if df.empty:
            self.page_info_var.set("No data to display")
            self._update_pagination_buttons()
            return
            
        # Calculate page bounds
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(df))
        page_data = df.iloc[start_idx:end_idx]
        
        # Configure columns
        columns = list(df.columns)
        self.results_tree["columns"] = columns
        
        # Set column headings and widths
        for col in columns:
            self.results_tree.heading(col, text=str(col))
            # Adjust column width based on content
            max_width = max(len(str(col)), 10) * 8
            self.results_tree.column(col, width=min(max_width, 200), minwidth=80)
            
        # Insert data rows
        for index, row in page_data.iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            self.results_tree.insert("", "end", values=values)
            
        # Update pagination info
        self.page_info_var.set(
            f"Page {self.current_page + 1} of {self.total_pages} "
            f"(showing rows {start_idx + 1}-{end_idx} of {len(df):,})"
        )
        
        self._update_pagination_buttons()
        
    def _update_pagination_buttons(self):
        """Update the state of pagination buttons."""
        # Previous button
        if self.current_page > 0:
            self.prev_button.configure(state="normal")
        else:
            self.prev_button.configure(state="disabled")
            
        # Next button
        if self.current_page < self.total_pages - 1:
            self.next_button.configure(state="normal")
        else:
            self.next_button.configure(state="disabled")
            
    def _previous_page(self):
        """Navigate to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_table_display()
            
    def _next_page(self):
        """Navigate to the next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._update_table_display()
            
    def _on_rows_per_page_changed(self, event=None):
        """Handle change in rows per page selection."""
        try:
            new_rows_per_page = int(self.rows_per_page_var.get())
            if new_rows_per_page != self.rows_per_page:
                self.rows_per_page = new_rows_per_page
                self.current_page = 0  # Reset to first page
                
                if self.operation_result:
                    # Recalculate pagination
                    total_rows = len(self.operation_result.result_data)
                    self.total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
                    self._update_table_display()
        except ValueError:
            # Reset to previous valid value
            self.rows_per_page_var.set(str(self.rows_per_page))
            
    def _export_results(self):
        """Export the results to a file."""
        if not self.operation_result:
            messagebox.showwarning("No Data", "No results to export.")
            return
            
        # Get export format
        export_format = self.export_format_var.get()
        
        # File dialog for save location
        if export_format == "csv":
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            default_ext = ".csv"
        else:
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
            default_ext = ".xlsx"
            
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        operation_name = self.operation_result.operation_type.replace('_', '-')
        default_filename = f"comparison-results-{operation_name}-{timestamp}{default_ext}"
        
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=default_filename
        )
        
        if not file_path:
            return
            
        try:
            # Show progress
            self.export_status_var.set("Exporting...")
            self.export_button.configure(state="disabled")
            self.parent_frame.update_idletasks()
            
            # Export data
            if export_format == "csv":
                success = self.export_service.export_to_csv(
                    self.operation_result.result_data, file_path)
            else:
                success = self.export_service.export_to_excel(
                    self.operation_result.result_data, file_path)
                
            if success:
                self.export_status_var.set(f"Successfully exported to {os.path.basename(file_path)}")
                
                # Show success message with option to open file location
                result = messagebox.askyesno(
                    "Export Complete", 
                    f"Results exported successfully to:\n{file_path}\n\nWould you like to open the file location?")
                
                if result:
                    # Open file location in file explorer
                    try:
                        if os.name == 'nt':  # Windows
                            os.startfile(os.path.dirname(file_path))
                        elif os.name == 'posix':  # macOS and Linux
                            os.system(f'open "{os.path.dirname(file_path)}"')
                    except Exception:
                        pass  # Ignore errors opening file location
                        
                # Notify callback
                if self.on_export_complete:
                    self.on_export_complete(file_path, export_format)
                    
            else:
                self.export_status_var.set("Export failed. Please try again.")
                messagebox.showerror("Export Error", "Failed to export results. Please check the file path and try again.")
                
        except Exception as e:
            self.export_status_var.set("Export failed.")
            messagebox.showerror("Export Error", f"An error occurred during export:\n{str(e)}")
            
        finally:
            # Re-enable export button
            self.export_button.configure(state="normal")
            
    def clear_results(self):
        """Clear all results and reset the panel."""
        self.operation_result = None
        self.current_page = 0
        self.total_pages = 0
        
        # Reset summary
        self.operation_var.set("No operation performed")
        self.time_var.set("-")
        self.original_count_var.set("-")
        self.result_count_var.set("-")
        self.summary_var.set("No results to display")
        
        # Clear table
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree["columns"] = ()
        
        # Reset pagination
        self.page_info_var.set("No data")
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        
        # Disable export
        self.export_button.configure(state="disabled")
        self.export_status_var.set("")
        
        # Show empty state message
        self.empty_state_label.grid(row=1, column=0, pady=50)
        
    def get_current_results(self) -> Optional[OperationResult]:
        """
        Get the currently displayed results.
        
        Returns:
            Current OperationResult or None if no results are displayed
        """
        return self.operation_result
        
    def has_results(self) -> bool:
        """
        Check if results are currently displayed.
        
        Returns:
            True if results are displayed, False otherwise
        """
        return self.operation_result is not None
        
    def _add_tooltips(self):
        """Add tooltips to results panel components."""
        # Pagination tooltips
        prev_tooltip = "Go to previous page of results (Page Up key)"
        next_tooltip = "Go to next page of results (Page Down key)"
        
        self.help_service.add_tooltip(self.prev_button, prev_tooltip)
        self.help_service.add_tooltip(self.next_button, next_tooltip)
        
        # Results table tooltip
        table_tooltip = ("Results of the comparison operation. Use pagination controls to navigate through large result sets. "
                        "All columns from the source file(s) are preserved in the results.")
        
        self.help_service.add_tooltip(self.results_tree, table_tooltip)
        
        # Export button tooltip
        export_tooltip = ("Export the complete results to a file. Choose CSV for universal compatibility "
                         "or Excel to preserve formatting. The exported file contains all results, not just the current page.")
        
        self.help_service.add_tooltip(self.export_button, export_tooltip)