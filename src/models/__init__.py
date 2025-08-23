# Models package - Core data models and structures

from .data_models import FileInfo, ComparisonConfig, OperationResult
from .interfaces import (
    FileParserInterface, 
    ComparisonEngineInterface, 
    ExportServiceInterface,
    GUIComponentInterface
)
from .exceptions import (
    FileComparisonError,
    FileParsingError,
    InvalidFileFormatError,
    ComparisonOperationError,
    ExportError,
    ValidationError
)

__all__ = [
    # Data models
    'FileInfo',
    'ComparisonConfig', 
    'OperationResult',
    # Interfaces
    'FileParserInterface',
    'ComparisonEngineInterface',
    'ExportServiceInterface',
    'GUIComponentInterface',
    # Exceptions
    'FileComparisonError',
    'FileParsingError',
    'InvalidFileFormatError',
    'ComparisonOperationError',
    'ExportError',
    'ValidationError'
]