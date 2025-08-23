"""
Enhanced error dialogs and user feedback components for the File Comparison Tool.

This module provides custom dialog boxes with better error presentation,
retry mechanisms, and detailed error information for users.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Callable, Dict, Any
import webbrowser
from datetime import datetime


class ErrorDialog:
    """
    Enhanced error dialog with detailed information and recovery options.
    
    Provides a more informative error dialog than standard messageboxes,
    with expandable details, recovery suggestions, and retry options.
    """
    
    def __init__(self, parent: Optional[tk.Widget] = None):
        """
        Initialize the error dialog.
        
        Args:
            parent: Parent widget for the dialog
        """
        self.parent = parent
        self.dialog = None
        self.result = False
        
    def show_error(self, title: str, message: str, details: str = "",
                  suggestions: str = "", allow_retry: bool = False,
                  retry_callback: Optional[Callable] = None,
                  show_logs: bool = True) -> bool:
        """
        Show enhanced error dialog.
        
        Args:
            title: Dialog title
            message: Main error message
            details: Detailed error information
            suggestions: Recovery suggestions
            allow_retry: Whether to show retry button
            retry_callback: Function to call on retry
            show_logs: Whether to show log viewing option
            
        Returns:
            bool: True if retry was requested, False otherwise
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and message
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Error icon
        error_label = ttk.Label(header_frame, text="⚠", font=("Arial", 24), foreground="red")
        error_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Main message
        message_label = ttk.Label(
            header_frame, 
            text=message, 
            font=("Arial", 10, "bold"),
            wraplength=400
        )
        message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create notebook for tabbed content
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Suggestions tab
        if suggestions:
            suggestions_frame = ttk.Frame(notebook)
            notebook.add(suggestions_frame, text="Solutions")
            
            suggestions_text = scrolledtext.ScrolledText(
                suggestions_frame, 
                wrap=tk.WORD, 
                height=8,
                font=("Arial", 9)
            )
            suggestions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            suggestions_text.insert(tk.END, suggestions)
            suggestions_text.config(state=tk.DISABLED)
        
        # Details tab
        if details:
            details_frame = ttk.Frame(notebook)
            notebook.add(details_frame, text="Technical Details")
            
            details_text = scrolledtext.ScrolledText(
                details_frame, 
                wrap=tk.WORD, 
                height=8,
                font=("Courier", 8)
            )
            details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            details_text.insert(tk.END, details)
            details_text.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Retry button
        if allow_retry and retry_callback:
            retry_btn = ttk.Button(
                button_frame, 
                text="Retry", 
                command=lambda: self._handle_retry(retry_callback)
            )
            retry_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # View logs button
        if show_logs:
            logs_btn = ttk.Button(
                button_frame, 
                text="View Logs", 
                command=self._show_logs
            )
            logs_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Close button
        close_btn = ttk.Button(
            button_frame, 
            text="Close", 
            command=self._close_dialog
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result
        
    def _center_dialog(self):
        """Center the dialog on screen or parent."""
        self.dialog.update_idletasks()
        
        if self.parent:
            # Center on parent
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - self.dialog.winfo_width()) // 2
            y = parent_y + (parent_height - self.dialog.winfo_height()) // 2
        else:
            # Center on screen
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            
            x = (screen_width - self.dialog.winfo_width()) // 2
            y = (screen_height - self.dialog.winfo_height()) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
    def _handle_retry(self, retry_callback: Callable):
        """Handle retry button click."""
        self.result = True
        self.dialog.destroy()
        
    def _show_logs(self):
        """Show application logs."""
        try:
            # Try to get log file path from error handler
            from services.error_handler import ErrorHandler
            handler = ErrorHandler()
            log_path = handler.get_log_file_path()
            
            # Show log viewer dialog
            LogViewerDialog(self.dialog, log_path).show()
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Could not open log file: {str(e)}",
                parent=self.dialog
            )
        
    def _close_dialog(self):
        """Close the dialog."""
        self.result = False
        self.dialog.destroy()


class LogViewerDialog:
    """
    Dialog for viewing application logs.
    
    Provides a scrollable text view of log files with search functionality
    and the ability to save or copy log contents.
    """
    
    def __init__(self, parent: Optional[tk.Widget] = None, log_file_path: str = ""):
        """
        Initialize log viewer dialog.
        
        Args:
            parent: Parent widget
            log_file_path: Path to log file
        """
        self.parent = parent
        self.log_file_path = log_file_path
        self.dialog = None
        
    def show(self):
        """Show the log viewer dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Application Logs")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with file path
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Log File:").pack(side=tk.LEFT)
        ttk.Label(
            header_frame, 
            text=self.log_file_path, 
            font=("Courier", 8)
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self._search_logs)
        
        ttk.Button(
            search_frame, 
            text="Clear", 
            command=self._clear_search
        ).pack(side=tk.RIGHT)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            font=("Courier", 8)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Refresh", 
            command=self._refresh_logs
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Copy All", 
            command=self._copy_logs
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Save As...", 
            command=self._save_logs
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Close", 
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Load initial logs
        self._load_logs()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
        
    def _load_logs(self):
        """Load log file contents."""
        try:
            if self.log_file_path and tk.os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, content)
                
                # Scroll to bottom
                self.log_text.see(tk.END)
            else:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "Log file not found or empty.")
                
        except Exception as e:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"Error loading log file: {str(e)}")
            
    def _refresh_logs(self):
        """Refresh log contents."""
        self._load_logs()
        
    def _search_logs(self, event=None):
        """Search for text in logs."""
        search_term = self.search_var.get()
        
        # Clear previous highlights
        self.log_text.tag_remove("highlight", 1.0, tk.END)
        
        if search_term:
            # Search and highlight
            start_pos = 1.0
            while True:
                pos = self.log_text.search(
                    search_term, start_pos, tk.END, nocase=True
                )
                if not pos:
                    break
                    
                end_pos = f"{pos}+{len(search_term)}c"
                self.log_text.tag_add("highlight", pos, end_pos)
                start_pos = end_pos
                
            # Configure highlight tag
            self.log_text.tag_config("highlight", background="yellow")
            
    def _clear_search(self):
        """Clear search and highlights."""
        self.search_var.set("")
        self.log_text.tag_remove("highlight", 1.0, tk.END)
        
    def _copy_logs(self):
        """Copy all log contents to clipboard."""
        try:
            content = self.log_text.get(1.0, tk.END)
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(content)
            messagebox.showinfo("Success", "Logs copied to clipboard.", parent=self.dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy logs: {str(e)}", parent=self.dialog)
            
    def _save_logs(self):
        """Save logs to a file."""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                parent=self.dialog,
                title="Save Logs As",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                messagebox.showinfo(
                    "Success", 
                    f"Logs saved to {filename}", 
                    parent=self.dialog
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Failed to save logs: {str(e)}", 
                parent=self.dialog
            )


class ProgressDialog:
    """
    Progress dialog with cancellation support and detailed status updates.
    
    Shows progress for long-running operations with the ability to cancel
    and detailed status messages.
    """
    
    def __init__(self, parent: Optional[tk.Widget] = None, title: str = "Processing"):
        """
        Initialize progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
        """
        self.parent = parent
        self.title = title
        self.dialog = None
        self.cancelled = False
        self.cancel_callback = None
        
    def show(self, message: str = "Please wait...", 
            allow_cancel: bool = True,
            cancel_callback: Optional[Callable] = None) -> 'ProgressDialog':
        """
        Show progress dialog.
        
        Args:
            message: Initial status message
            allow_cancel: Whether to show cancel button
            cancel_callback: Function to call when cancelled
            
        Returns:
            ProgressDialog: Self for method chaining
        """
        self.cancel_callback = cancel_callback
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status message
        self.status_label = ttk.Label(
            main_frame, 
            text=message, 
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Cancel button
        if allow_cancel:
            self.cancel_button = ttk.Button(
                main_frame, 
                text="Cancel", 
                command=self._handle_cancel
            )
            self.cancel_button.pack()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._handle_cancel)
        
        return self
        
    def update_progress(self, percentage: float, message: str = None):
        """
        Update progress and message.
        
        Args:
            percentage: Progress percentage (0-100)
            message: Optional status message
        """
        if self.dialog and not self.cancelled:
            self.progress_var.set(percentage)
            
            if message:
                self.status_label.config(text=message)
                
            self.dialog.update()
            
    def close(self):
        """Close the progress dialog."""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
            
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.cancelled
        
    def _center_dialog(self):
        """Center the dialog."""
        self.dialog.update_idletasks()
        
        if self.parent:
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - self.dialog.winfo_width()) // 2
            y = parent_y + (parent_height - self.dialog.winfo_height()) // 2
        else:
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            
            x = (screen_width - self.dialog.winfo_width()) // 2
            y = (screen_height - self.dialog.winfo_height()) // 2
            
        self.dialog.geometry(f"+{x}+{y}")
        
    def _handle_cancel(self):
        """Handle cancel button or window close."""
        self.cancelled = True
        
        if self.cancel_callback:
            try:
                self.cancel_callback()
            except Exception as e:
                print(f"Error in cancel callback: {e}")
                
        self.close()


class ValidationIndicator:
    """
    Visual validation indicator widget.
    
    Provides visual feedback for form validation with icons and messages.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize validation indicator.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        
        # Create indicator frame
        self.frame = ttk.Frame(parent)
        
        # Icon label
        self.icon_label = ttk.Label(self.frame, text="", font=("Arial", 12))
        self.icon_label.pack(side=tk.LEFT, padx=(5, 2))
        
        # Message label
        self.message_label = ttk.Label(
            self.frame, 
            text="", 
            font=("Arial", 8),
            wraplength=200
        )
        self.message_label.pack(side=tk.LEFT)
        
        # Initially hidden
        self.frame.pack_forget()
        
    def show_valid(self, message: str = "Valid"):
        """Show valid state."""
        self.icon_label.config(text="✓", foreground="green")
        self.message_label.config(text=message, foreground="green")
        self.frame.pack(fill=tk.X, pady=(2, 0))
        
    def show_invalid(self, message: str):
        """Show invalid state."""
        self.icon_label.config(text="✗", foreground="red")
        self.message_label.config(text=message, foreground="red")
        self.frame.pack(fill=tk.X, pady=(2, 0))
        
    def show_warning(self, message: str):
        """Show warning state."""
        self.icon_label.config(text="⚠", foreground="orange")
        self.message_label.config(text=message, foreground="orange")
        self.frame.pack(fill=tk.X, pady=(2, 0))
        
    def hide(self):
        """Hide the indicator."""
        self.frame.pack_forget()
        
    def destroy(self):
        """Destroy the indicator."""
        self.frame.destroy()