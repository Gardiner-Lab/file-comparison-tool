"""
Custom exceptions for the File Comparison Tool.

This module defines application-specific exceptions that provide
better error handling and user feedback throughout the application.
"""


class FileComparisonError(Exception):
    """Base exception class for all File Comparison Tool errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class FileParsingError(FileComparisonError):
    """Raised when file parsing operations fail."""
    
    def __init__(self, message: str, file_path: str = None, error_code: str = "FILE_PARSE_ERROR"):
        super().__init__(message, error_code)
        self.file_path = file_path


class InvalidFileFormatError(FileComparisonError):
    """Raised when an unsupported file format is encountered."""
    
    def __init__(self, message: str, file_path: str = None, supported_formats: list = None):
        super().__init__(message, "INVALID_FORMAT")
        self.file_path = file_path
        self.supported_formats = supported_formats or ['csv', 'xlsx', 'xls']


class ComparisonOperationError(FileComparisonError):
    """Raised when comparison operations fail."""
    
    def __init__(self, message: str, operation_type: str = None, error_code: str = "COMPARISON_ERROR"):
        super().__init__(message, error_code)
        self.operation_type = operation_type


class ExportError(FileComparisonError):
    """Raised when export operations fail."""
    
    def __init__(self, message: str, output_path: str = None, error_code: str = "EXPORT_ERROR"):
        super().__init__(message, error_code)
        self.output_path = output_path


class ValidationError(FileComparisonError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field_name: str = None, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)
        self.field_name = field_name