"""
Core data models for the File Comparison Tool.

This module contains the primary data structures used throughout the application
for representing file information, comparison configurations, and operation results.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

# Use TYPE_CHECKING to avoid import errors when pandas is not installed
if TYPE_CHECKING:
    import pandas as pd
else:
    # Create a placeholder for pandas DataFrame when not available
    try:
        import pandas as pd
    except ImportError:
        # Create a simple placeholder class for development
        class _DataFramePlaceholder:
            """Placeholder for pandas DataFrame when pandas is not installed."""
            pass
        
        class _PandasPlaceholder:
            DataFrame = _DataFramePlaceholder
        
        pd = _PandasPlaceholder()


@dataclass
class FileInfo:
    """
    Represents metadata and information about a loaded file.
    
    Attributes:
        file_path: Full path to the file
        file_type: Type of file ('csv' or 'excel')
        columns: List of column names in the file
        row_count: Number of data rows in the file
        file_size: Size of the file in bytes
        last_modified: Last modification timestamp of the file
    """
    file_path: str
    file_type: str  # 'csv' or 'excel'
    columns: List[str]
    row_count: int
    file_size: int
    last_modified: datetime
    
    def __post_init__(self):
        """Validate file_type after initialization."""
        if self.file_type not in ['csv', 'excel']:
            raise ValueError(f"Invalid file_type: {self.file_type}. Must be 'csv' or 'excel'")


@dataclass
class ComparisonConfig:
    """
    Configuration settings for a file comparison operation.
    
    Attributes:
        file1_path: Path to the first file
        file2_path: Path to the second file
        file1_column: Column name to compare from first file
        file2_column: Column name to compare from second file
        operation: Type of comparison operation to perform
        output_format: Format for the output file ('csv' or 'excel')
        case_sensitive: Whether comparison should be case sensitive
    """
    file1_path: str
    file2_path: str
    file1_column: str
    file2_column: str
    operation: str  # 'remove_matches', 'keep_matches', 'find_common', 'find_unique'
    output_format: str  # 'csv' or 'excel'
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        valid_operations = ['remove_matches', 'keep_matches', 'find_common', 'find_unique']
        if self.operation not in valid_operations:
            raise ValueError(f"Invalid operation: {self.operation}. Must be one of {valid_operations}")
        
        if self.output_format not in ['csv', 'excel']:
            raise ValueError(f"Invalid output_format: {self.output_format}. Must be 'csv' or 'excel'")


@dataclass
class OperationResult:
    """
    Results and metadata from a comparison operation.
    
    Attributes:
        result_data: The processed DataFrame containing the results
        original_count: Number of rows in the original dataset
        result_count: Number of rows in the result dataset
        operation_type: The type of operation that was performed
        processing_time: Time taken to complete the operation in seconds
        summary: Human-readable summary of the operation results
    """
    result_data: 'pd.DataFrame'
    original_count: int
    result_count: int
    operation_type: str
    processing_time: float
    summary: str
    
    def __post_init__(self):
        """Validate result data after initialization."""
        # Only validate DataFrame type if pandas is available
        try:
            import pandas as pd
            if not isinstance(self.result_data, pd.DataFrame):
                raise TypeError("result_data must be a pandas DataFrame")
        except ImportError:
            # Skip DataFrame validation if pandas is not installed
            pass
        
        if self.original_count < 0 or self.result_count < 0:
            raise ValueError("Row counts cannot be negative")
        
        if self.processing_time < 0:
            raise ValueError("Processing time cannot be negative")