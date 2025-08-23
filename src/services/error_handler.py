"""
Error handling service for the File Comparison Tool.

This module provides comprehensive error handling with user-friendly message translation,
retry mechanisms, logging, and GUI integration for displaying errors and validation feedback.
"""

import logging
import traceback
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional, Callable, Any, Tuple
from enum import Enum
from datetime import datetime
import os
from pathlib import Path

from models.exceptions import (
    FileComparisonError, FileParsingError, InvalidFileFormatError,
    ComparisonOperationError, ExportError, ValidationError
)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization."""
    FILE_OPERATION = "file_operation"
    DATA_PROCESSING = "data_processing"
    VALIDATION = "validation"
    EXPORT = "export"
    SYSTEM = "system"
    GUI = "gui"


class ErrorHandler:
    """
    Comprehensive error handling service with user-friendly messages and retry mechanisms.
    
    This service provides centralized error handling, logging, user-friendly message
    translation, and retry mechanisms for recoverable errors.
    """
    
    def __init__(self, log_file_path: Optional[str] = None):
        """
        Initialize the error handler.
        
        Args:
            log_file_path: Optional path for log file. If None, uses default location.
        """
        self.retry_counts = {}
        self.max_retries = 3
        self.retry_callbacks = {}
        
        # Setup logging
        self._setup_logging(log_file_path)
        
        # Error message templates
        self._error_messages = self._initialize_error_messages()
        
        # Recovery suggestions
        self._recovery_suggestions = self._initialize_recovery_suggestions()
        
    def _setup_logging(self, log_file_path: Optional[str] = None):
        """
        Setup logging configuration.
        
        Args:
            log_file_path: Optional custom log file path
        """
        if log_file_path is None:
            # Create logs directory in user's home or current directory
            try:
                log_dir = Path.home() / ".file_comparison_tool" / "logs"
            except Exception:
                log_dir = Path("logs")
            
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = log_dir / f"error_log_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path, encoding='utf-8'),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger('FileComparisonTool')
        self.logger.info("Error handler initialized")
        
    def _initialize_error_messages(self) -> Dict[str, str]:
        """Initialize user-friendly error message templates."""
        return {
            # File operation errors
            'file_not_found': "The file '{file_path}' could not be found. Please check the file path and try again.",
            'file_access_denied': "Access denied to file '{file_path}'. Please check file permissions.",
            'file_corrupted': "The file '{file_path}' appears to be corrupted or damaged.",
            'unsupported_format': "The file format '{format}' is not supported. Supported formats: {supported_formats}.",
            'file_too_large': "The file '{file_path}' is too large to process efficiently. Consider splitting it into smaller files.",
            'file_empty': "The file '{file_path}' is empty or contains no valid data.",
            
            # Data processing errors
            'column_not_found': "Column '{column}' was not found in the file. Available columns: {available_columns}.",
            'incompatible_columns': "The selected columns have incompatible data types and cannot be compared.",
            'data_type_mismatch': "Data type mismatch between columns '{col1}' and '{col2}'.",
            'memory_error': "Not enough memory to process the selected files. Try closing other applications or use smaller files.",
            'processing_timeout': "The operation took too long to complete and was cancelled.",
            
            # Validation errors
            'missing_files': "Please select both files before proceeding.",
            'missing_columns': "Please select columns from both files for comparison.",
            'missing_operation': "Please select a comparison operation.",
            'invalid_configuration': "The current configuration is invalid: {details}.",
            
            # Export errors
            'export_path_invalid': "The export path '{path}' is invalid or inaccessible.",
            'export_permission_denied': "Permission denied when trying to save to '{path}'.",
            'export_disk_full': "Not enough disk space to save the file to '{path}'.",
            'export_format_error': "Error saving file in '{format}' format: {details}.",
            
            # System errors
            'system_error': "A system error occurred: {details}",
            'network_error': "Network error: {details}",
            'dependency_missing': "Required dependency is missing: {dependency}",
            
            # GUI errors
            'gui_error': "Interface error: {details}",
            'display_error': "Error displaying results: {details}",
        }
        
    def _initialize_recovery_suggestions(self) -> Dict[str, str]:
        """Initialize recovery suggestions for different error types."""
        return {
            'file_not_found': "• Check if the file path is correct\n• Verify the file hasn't been moved or deleted\n• Try browsing for the file again",
            'file_access_denied': "• Check file permissions\n• Close the file if it's open in another application\n• Run the application as administrator if needed",
            'unsupported_format': "• Convert the file to CSV or Excel format\n• Check if the file extension is correct",
            'file_corrupted': "• Try opening the file in Excel or a text editor\n• Use a backup copy if available\n• Re-export the file from its original source",
            'column_not_found': "• Check the column name spelling\n• Verify the file has the expected structure\n• Try refreshing the file data",
            'memory_error': "• Close other applications to free memory\n• Split large files into smaller chunks\n• Restart the application",
            'export_permission_denied': "• Choose a different save location\n• Check folder permissions\n• Close the file if it's open elsewhere",
            'missing_files': "• Use the Browse buttons to select files\n• Ensure both files are valid and accessible",
            'missing_columns': "• Select a column from each file dropdown\n• Refresh the file data if columns are missing",
        }
        
    def handle_error(self, error: Exception, context: str = "", 
                    parent_widget: Optional[tk.Widget] = None,
                    show_dialog: bool = True, allow_retry: bool = False,
                    retry_callback: Optional[Callable] = None) -> bool:
        """
        Handle an error with comprehensive logging and user feedback.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            parent_widget: Parent widget for error dialogs
            show_dialog: Whether to show error dialog to user
            allow_retry: Whether to offer retry option
            retry_callback: Callback function for retry attempts
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        try:
            # Log the error
            self._log_error(error, context)
            
            # Categorize the error
            category, severity = self._categorize_error(error)
            
            # Generate user-friendly message
            user_message = self._generate_user_message(error, context)
            
            # Get recovery suggestions
            suggestions = self._get_recovery_suggestions(error)
            
            # Show dialog if requested
            if show_dialog:
                return self._show_error_dialog(
                    user_message, suggestions, severity, 
                    parent_widget, allow_retry, retry_callback, context
                )
            
            return True
            
        except Exception as handler_error:
            # Fallback error handling
            self.logger.critical(f"Error in error handler: {str(handler_error)}")
            if show_dialog:
                messagebox.showerror(
                    "Critical Error", 
                    f"A critical error occurred in the error handler: {str(handler_error)}"
                )
            return False
            
    def _log_error(self, error: Exception, context: str = ""):
        """
        Log error details for debugging.
        
        Args:
            error: The exception to log
            context: Additional context information
        """
        error_details = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        # Add specific error attributes if available
        if hasattr(error, 'error_code'):
            error_details['error_code'] = error.error_code
        if hasattr(error, 'file_path'):
            error_details['file_path'] = error.file_path
        if hasattr(error, 'operation_type'):
            error_details['operation_type'] = error.operation_type
            
        self.logger.error(f"Error occurred: {error_details}")
        
    def _categorize_error(self, error: Exception) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
        Categorize error by type and severity.
        
        Args:
            error: The exception to categorize
            
        Returns:
            Tuple of (category, severity)
        """
        if isinstance(error, FileParsingError):
            return ErrorCategory.FILE_OPERATION, ErrorSeverity.ERROR
        elif isinstance(error, InvalidFileFormatError):
            return ErrorCategory.FILE_OPERATION, ErrorSeverity.WARNING
        elif isinstance(error, ComparisonOperationError):
            return ErrorCategory.DATA_PROCESSING, ErrorSeverity.ERROR
        elif isinstance(error, ExportError):
            return ErrorCategory.EXPORT, ErrorSeverity.ERROR
        elif isinstance(error, ValidationError):
            return ErrorCategory.VALIDATION, ErrorSeverity.WARNING
        elif isinstance(error, MemoryError):
            return ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL
        elif isinstance(error, PermissionError):
            return ErrorCategory.SYSTEM, ErrorSeverity.ERROR
        elif isinstance(error, FileNotFoundError):
            return ErrorCategory.FILE_OPERATION, ErrorSeverity.ERROR
        else:
            return ErrorCategory.SYSTEM, ErrorSeverity.ERROR
            
    def _generate_user_message(self, error: Exception, context: str = "") -> str:
        """
        Generate user-friendly error message.
        
        Args:
            error: The exception
            context: Additional context
            
        Returns:
            str: User-friendly error message
        """
        # Try to match specific error patterns
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # File not found errors
        if isinstance(error, FileNotFoundError) or 'not found' in error_message:
            file_path = getattr(error, 'filename', 'unknown')
            return self._error_messages['file_not_found'].format(file_path=file_path)
            
        # Permission errors
        elif isinstance(error, PermissionError) or 'permission denied' in error_message:
            file_path = getattr(error, 'filename', 'unknown')
            return self._error_messages['file_access_denied'].format(file_path=file_path)
            
        # Memory errors
        elif isinstance(error, MemoryError) or 'memory' in error_message:
            return self._error_messages['memory_error']
            
        # Custom application errors
        elif isinstance(error, InvalidFileFormatError):
            format_name = getattr(error, 'file_path', 'unknown')
            supported = ', '.join(getattr(error, 'supported_formats', ['csv', 'xlsx', 'xls']))
            return self._error_messages['unsupported_format'].format(
                format=format_name, supported_formats=supported
            )
            
        elif isinstance(error, FileParsingError):
            if 'empty' in error_message:
                file_path = getattr(error, 'file_path', 'unknown')
                return self._error_messages['file_empty'].format(file_path=file_path)
            elif 'corrupted' in error_message or 'damaged' in error_message:
                file_path = getattr(error, 'file_path', 'unknown')
                return self._error_messages['file_corrupted'].format(file_path=file_path)
            else:
                return f"Error reading file: {str(error)}"
                
        elif isinstance(error, ValidationError):
            field_name = getattr(error, 'field_name', None)
            if field_name:
                return f"Validation error in {field_name}: {str(error)}"
            else:
                return f"Validation error: {str(error)}"
                
        elif isinstance(error, ExportError):
            output_path = getattr(error, 'output_path', 'unknown')
            if 'permission' in error_message:
                return self._error_messages['export_permission_denied'].format(path=output_path)
            elif 'space' in error_message or 'disk full' in error_message:
                return self._error_messages['export_disk_full'].format(path=output_path)
            else:
                return f"Export error: {str(error)}"
                
        # Generic fallback
        else:
            base_message = str(error)
            if context:
                return f"{context}: {base_message}"
            return f"An error occurred: {base_message}"
            
    def _get_recovery_suggestions(self, error: Exception) -> str:
        """
        Get recovery suggestions for the error.
        
        Args:
            error: The exception
            
        Returns:
            str: Recovery suggestions
        """
        error_message = str(error).lower()
        
        # Match error patterns to suggestions
        if isinstance(error, FileNotFoundError) or 'not found' in error_message:
            return self._recovery_suggestions['file_not_found']
        elif isinstance(error, PermissionError) or 'permission denied' in error_message:
            return self._recovery_suggestions['file_access_denied']
        elif isinstance(error, InvalidFileFormatError):
            return self._recovery_suggestions['unsupported_format']
        elif isinstance(error, MemoryError) or 'memory' in error_message:
            return self._recovery_suggestions['memory_error']
        elif 'corrupted' in error_message or 'damaged' in error_message:
            return self._recovery_suggestions['file_corrupted']
        elif 'column' in error_message and 'not found' in error_message:
            return self._recovery_suggestions['column_not_found']
        elif isinstance(error, ValidationError):
            if 'files' in error_message:
                return self._recovery_suggestions['missing_files']
            elif 'column' in error_message:
                return self._recovery_suggestions['missing_columns']
        elif isinstance(error, ExportError):
            if 'permission' in error_message:
                return self._recovery_suggestions['export_permission_denied']
                
        return "• Try the operation again\n• Check the application logs for more details\n• Contact support if the problem persists"
        
    def _show_error_dialog(self, message: str, suggestions: str, severity: ErrorSeverity,
                          parent_widget: Optional[tk.Widget] = None, allow_retry: bool = False,
                          retry_callback: Optional[Callable] = None, context: str = "") -> bool:
        """
        Show error dialog with recovery options.
        
        Args:
            message: User-friendly error message
            suggestions: Recovery suggestions
            severity: Error severity level
            parent_widget: Parent widget for dialog
            allow_retry: Whether to show retry option
            retry_callback: Callback for retry attempts
            context: Error context for retry tracking
            
        Returns:
            bool: True if user chose to retry, False otherwise
        """
        # Determine dialog type based on severity
        if severity == ErrorSeverity.CRITICAL:
            dialog_type = "critical"
            title = "Critical Error"
        elif severity == ErrorSeverity.ERROR:
            dialog_type = "error"
            title = "Error"
        elif severity == ErrorSeverity.WARNING:
            dialog_type = "warning"
            title = "Warning"
        else:
            dialog_type = "info"
            title = "Information"
            
        # Create detailed message
        detailed_message = f"{message}\n\nSuggestions:\n{suggestions}"
        
        # Show retry dialog if allowed
        if allow_retry and retry_callback:
            return self._show_retry_dialog(
                title, detailed_message, retry_callback, context, parent_widget
            )
        else:
            # Show standard error dialog
            if dialog_type == "critical":
                messagebox.showerror(title, detailed_message, parent=parent_widget)
            elif dialog_type == "error":
                messagebox.showerror(title, detailed_message, parent=parent_widget)
            elif dialog_type == "warning":
                messagebox.showwarning(title, detailed_message, parent=parent_widget)
            else:
                messagebox.showinfo(title, detailed_message, parent=parent_widget)
                
            return False
            
    def _show_retry_dialog(self, title: str, message: str, retry_callback: Callable,
                          context: str, parent_widget: Optional[tk.Widget] = None) -> bool:
        """
        Show dialog with retry option.
        
        Args:
            title: Dialog title
            message: Error message
            retry_callback: Function to call for retry
            context: Context for retry tracking
            parent_widget: Parent widget
            
        Returns:
            bool: True if retry was attempted, False otherwise
        """
        # Check retry count
        retry_count = self.retry_counts.get(context, 0)
        
        if retry_count >= self.max_retries:
            # Max retries reached
            final_message = f"{message}\n\nMaximum retry attempts ({self.max_retries}) reached."
            messagebox.showerror(title, final_message, parent=parent_widget)
            return False
            
        # Show retry dialog
        retry_message = f"{message}\n\nWould you like to try again? (Attempt {retry_count + 1} of {self.max_retries})"
        
        result = messagebox.askyesno(
            title, retry_message, 
            parent=parent_widget,
            icon='question'
        )
        
        if result:
            # User chose to retry
            self.retry_counts[context] = retry_count + 1
            
            try:
                # Execute retry callback
                retry_result = retry_callback()
                
                # Reset retry count on success
                if retry_result:
                    self.retry_counts[context] = 0
                    
                return retry_result
                
            except Exception as retry_error:
                # Handle retry error
                self.logger.warning(f"Retry attempt {retry_count + 1} failed: {str(retry_error)}")
                return self.handle_error(
                    retry_error, f"Retry attempt {retry_count + 1}",
                    parent_widget, True, True, retry_callback
                )
        else:
            # User chose not to retry
            self.retry_counts[context] = 0
            return False
            
    def create_validation_feedback(self, parent_widget: tk.Widget, 
                                 field_name: str) -> 'ValidationFeedback':
        """
        Create a validation feedback widget.
        
        Args:
            parent_widget: Parent widget to attach feedback to
            field_name: Name of the field being validated
            
        Returns:
            ValidationFeedback: Feedback widget instance
        """
        return ValidationFeedback(parent_widget, field_name, self)
        
    def reset_retry_count(self, context: str):
        """
        Reset retry count for a specific context.
        
        Args:
            context: The context to reset
        """
        if context in self.retry_counts:
            del self.retry_counts[context]
            
    def get_log_file_path(self) -> str:
        """
        Get the current log file path.
        
        Returns:
            str: Path to the log file
        """
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return "No log file configured"


class ValidationFeedback:
    """
    Widget for providing visual validation feedback.
    
    This class creates visual indicators for validation status including
    checkmarks, warning icons, and error messages.
    """
    
    def __init__(self, parent_widget: tk.Widget, field_name: str, error_handler: ErrorHandler):
        """
        Initialize validation feedback widget.
        
        Args:
            parent_widget: Parent widget
            field_name: Name of the field
            error_handler: Error handler instance
        """
        self.parent = parent_widget
        self.field_name = field_name
        self.error_handler = error_handler
        
        # Create feedback frame
        self.feedback_frame = tk.Frame(parent_widget)
        
        # Status label for icons and messages
        self.status_label = tk.Label(
            self.feedback_frame, 
            text="", 
            font=("Arial", 8),
            wraplength=200
        )
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Initially hidden
        self.feedback_frame.pack_forget()
        
    def show_success(self, message: str = "Valid"):
        """
        Show success feedback.
        
        Args:
            message: Success message to display
        """
        self.status_label.config(
            text=f"✓ {message}",
            fg="green",
            bg=self.parent.cget('bg')
        )
        self.feedback_frame.pack(fill=tk.X, pady=(2, 0))
        
    def show_warning(self, message: str):
        """
        Show warning feedback.
        
        Args:
            message: Warning message to display
        """
        self.status_label.config(
            text=f"⚠ {message}",
            fg="orange",
            bg=self.parent.cget('bg')
        )
        self.feedback_frame.pack(fill=tk.X, pady=(2, 0))
        
    def show_error(self, message: str):
        """
        Show error feedback.
        
        Args:
            message: Error message to display
        """
        self.status_label.config(
            text=f"✗ {message}",
            fg="red",
            bg=self.parent.cget('bg')
        )
        self.feedback_frame.pack(fill=tk.X, pady=(2, 0))
        
    def hide(self):
        """Hide the feedback widget."""
        self.feedback_frame.pack_forget()
        
    def destroy(self):
        """Destroy the feedback widget."""
        self.feedback_frame.destroy()