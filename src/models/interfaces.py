"""
Base interfaces and abstract classes for the File Comparison Tool.

This module defines the core interfaces that provide extensibility points
for different implementations of file parsing, comparison operations, and export functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, TYPE_CHECKING
from .data_models import FileInfo, ComparisonConfig, OperationResult

# Use TYPE_CHECKING to avoid import errors when pandas is not installed
if TYPE_CHECKING:
    import pandas as pd
else:
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


class FileParserInterface(ABC):
    """
    Abstract interface for file parsing implementations.
    
    This interface allows for different file parsing strategies
    while maintaining a consistent API.
    """
    
    @abstractmethod
    def parse_file(self, file_path: str) -> 'pd.DataFrame':
        """
        Parse a file and return its contents as a DataFrame.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            DataFrame containing the file contents
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        pass
    
    @abstractmethod
    def get_file_info(self, file_path: str) -> FileInfo:
        """
        Extract metadata information from a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            FileInfo object containing file metadata
        """
        pass
    
    @abstractmethod
    def validate_file_format(self, file_path: str) -> bool:
        """
        Validate if the file format is supported.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file format is supported, False otherwise
        """
        pass


class ComparisonEngineInterface(ABC):
    """
    Abstract interface for comparison operation implementations.
    
    This interface defines the contract for different comparison strategies
    and allows for easy extension with new operation types.
    """
    
    @abstractmethod
    def remove_matches(self, df1: 'pd.DataFrame', df2: 'pd.DataFrame', 
                      column1: str, column2: str, case_sensitive: bool = False) -> 'pd.DataFrame':
        """
        Remove rows from df2 where the comparison column matches values in df1.
        
        Args:
            df1: First DataFrame (source of values to remove)
            df2: Second DataFrame (target for removal)
            column1: Column name in df1 to compare
            column2: Column name in df2 to compare
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            DataFrame with matching rows removed from df2
        """
        pass
    
    @abstractmethod
    def keep_only_matches(self, df1: 'pd.DataFrame', df2: 'pd.DataFrame',
                         column1: str, column2: str, case_sensitive: bool = False) -> 'pd.DataFrame':
        """
        Keep only rows from df2 where the comparison column matches values in df1.
        
        Args:
            df1: First DataFrame (source of values to keep)
            df2: Second DataFrame (target for filtering)
            column1: Column name in df1 to compare
            column2: Column name in df2 to compare
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            DataFrame with only matching rows from df2
        """
        pass
    
    @abstractmethod
    def find_common_values(self, df1: 'pd.DataFrame', df2: 'pd.DataFrame',
                          column1: str, column2: str, case_sensitive: bool = False) -> 'pd.DataFrame':
        """
        Find rows that exist in both DataFrames based on comparison columns.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            column1: Column name in df1 to compare
            column2: Column name in df2 to compare
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            DataFrame containing rows that exist in both files
        """
        pass
    
    @abstractmethod
    def find_unique_values(self, df1: 'pd.DataFrame', df2: 'pd.DataFrame',
                          column1: str, column2: str, case_sensitive: bool = False) -> 'pd.DataFrame':
        """
        Find rows that exist in only one of the DataFrames.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            column1: Column name in df1 to compare
            column2: Column name in df2 to compare
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            DataFrame containing rows that exist in only one file
        """
        pass


class ExportServiceInterface(ABC):
    """
    Abstract interface for export service implementations.
    
    This interface allows for different export strategies and formats
    while maintaining a consistent API.
    """
    
    @abstractmethod
    def export_to_csv(self, data: 'pd.DataFrame', file_path: str) -> bool:
        """
        Export DataFrame to CSV format.
        
        Args:
            data: DataFrame to export
            file_path: Path where the CSV file should be saved
            
        Returns:
            True if export was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def export_to_excel(self, data: 'pd.DataFrame', file_path: str) -> bool:
        """
        Export DataFrame to Excel format.
        
        Args:
            data: DataFrame to export
            file_path: Path where the Excel file should be saved
            
        Returns:
            True if export was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_summary_report(self, operation_result: OperationResult) -> str:
        """
        Generate a human-readable summary report of the operation.
        
        Args:
            operation_result: Results from the comparison operation
            
        Returns:
            Formatted summary string
        """
        pass


class GUIComponentInterface(ABC):
    """
    Abstract interface for GUI components.
    
    This interface provides a common structure for all GUI panels
    and components in the application.
    """
    
    @abstractmethod
    def initialize_component(self) -> None:
        """Initialize the GUI component and its widgets."""
        pass
    
    @abstractmethod
    def validate_input(self) -> bool:
        """
        Validate the current input state of the component.
        
        Returns:
            True if input is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def reset_component(self) -> None:
        """Reset the component to its initial state."""
        pass
    
    @abstractmethod
    def get_component_data(self) -> Dict[str, Any]:
        """
        Get the current data/state from the component.
        
        Returns:
            Dictionary containing component data
        """
        pass