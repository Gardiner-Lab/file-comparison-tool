"""
Export service for generating and saving result files.

This module provides functionality for exporting comparison results to various
file formats (CSV, Excel) and generating summary reports with operation statistics.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from models.data_models import OperationResult


class ExportService:
    """
    Service for exporting comparison results to files and generating reports.
    
    This service handles:
    - Exporting DataFrames to CSV and Excel formats
    - Validating file paths and write permissions
    - Generating summary reports with operation statistics
    - Error handling for export operations
    """
    
    def __init__(self):
        """Initialize the export service."""
        self.supported_formats = ['csv', 'excel']
    
    def export_to_csv(self, data: pd.DataFrame, file_path: str, **kwargs) -> bool:
        """
        Export DataFrame to CSV format.
        
        Args:
            data: The DataFrame to export
            file_path: Path where the CSV file should be saved
            **kwargs: Additional arguments passed to pandas to_csv method
            
        Returns:
            bool: True if export was successful, False otherwise
            
        Raises:
            ValueError: If file path is invalid or data is empty
            PermissionError: If write permission is denied
            Exception: For other export-related errors
        """
        try:
            # Validate inputs
            self._validate_export_inputs(data, file_path, 'csv')
            
            # Ensure directory exists
            self._ensure_directory_exists(file_path)
            
            # Set default CSV export parameters
            csv_kwargs = {
                'index': False,
                'encoding': 'utf-8',
                **kwargs
            }
            
            # Export to CSV
            data.to_csv(file_path, **csv_kwargs)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to export CSV file: {str(e)}")
    
    def export_to_excel(self, data: pd.DataFrame, file_path: str, **kwargs) -> bool:
        """
        Export DataFrame to Excel format.
        
        Args:
            data: The DataFrame to export
            file_path: Path where the Excel file should be saved
            **kwargs: Additional arguments passed to pandas to_excel method
            
        Returns:
            bool: True if export was successful, False otherwise
            
        Raises:
            ValueError: If file path is invalid or data is empty
            PermissionError: If write permission is denied
            Exception: For other export-related errors
        """
        try:
            # Validate inputs
            self._validate_export_inputs(data, file_path, 'excel')
            
            # Ensure directory exists
            self._ensure_directory_exists(file_path)
            
            # Set default Excel export parameters
            excel_kwargs = {
                'index': False,
                'engine': 'openpyxl',
                **kwargs
            }
            
            # Export to Excel
            data.to_excel(file_path, **excel_kwargs)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to export Excel file: {str(e)}")
    
    def export_result(self, operation_result: OperationResult, file_path: str, 
                     format_type: str = 'csv', **kwargs) -> bool:
        """
        Export an OperationResult to the specified format.
        
        Args:
            operation_result: The OperationResult containing data to export
            file_path: Path where the file should be saved
            format_type: Export format ('csv' or 'excel')
            **kwargs: Additional arguments for the export method
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if format_type.lower() == 'csv':
            return self.export_to_csv(operation_result.result_data, file_path, **kwargs)
        elif format_type.lower() == 'excel':
            return self.export_to_excel(operation_result.result_data, file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format_type}. Must be 'csv' or 'excel'")
    
    def generate_summary_report(self, operation_result: OperationResult, 
                              config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a summary report with operation statistics.
        
        Args:
            operation_result: The OperationResult to generate a report for
            config: Optional configuration details to include in the report
            
        Returns:
            str: Formatted summary report
        """
        report_lines = [
            "=" * 50,
            "FILE COMPARISON OPERATION SUMMARY",
            "=" * 50,
            "",
            f"Operation Type: {operation_result.operation_type}",
            f"Processing Time: {operation_result.processing_time:.2f} seconds",
            f"Original Row Count: {operation_result.original_count:,}",
            f"Result Row Count: {operation_result.result_count:,}",
            "",
            "Operation Summary:",
            operation_result.summary,
            "",
        ]
        
        # Add configuration details if provided
        if config:
            report_lines.extend([
                "Configuration Details:",
                f"  - File 1: {config.get('file1_path', 'N/A')}",
                f"  - File 2: {config.get('file2_path', 'N/A')}",
                f"  - Comparison Column 1: {config.get('file1_column', 'N/A')}",
                f"  - Comparison Column 2: {config.get('file2_column', 'N/A')}",
                f"  - Case Sensitive: {config.get('case_sensitive', False)}",
                "",
            ])
        
        # Add data statistics
        if not operation_result.result_data.empty:
            report_lines.extend([
                "Result Data Statistics:",
                f"  - Columns: {len(operation_result.result_data.columns)}",
                f"  - Column Names: {', '.join(operation_result.result_data.columns.tolist())}",
                "",
            ])
        
        # Add timestamp
        report_lines.extend([
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50
        ])
        
        return "\n".join(report_lines)
    
    def save_summary_report(self, operation_result: OperationResult, 
                           file_path: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save a summary report to a text file.
        
        Args:
            operation_result: The OperationResult to generate a report for
            file_path: Path where the report should be saved
            config: Optional configuration details to include in the report
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Validate file path
            self.validate_file_path(file_path)
            
            # Ensure directory exists
            self._ensure_directory_exists(file_path)
            
            # Generate and save report
            report_content = self.generate_summary_report(operation_result, config)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to save summary report: {str(e)}")
    
    def validate_file_path(self, file_path: str) -> bool:
        """
        Validate that a file path is valid and writable.
        
        Args:
            file_path: The file path to validate
            
        Returns:
            bool: True if path is valid and writable
            
        Raises:
            ValueError: If path is invalid
            PermissionError: If write permission is denied
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")
        
        # Convert to Path object for easier manipulation
        path = Path(file_path)
        
        # Check if parent directory exists or can be created
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise PermissionError(f"Cannot create directory: {parent_dir}")
        
        # Check write permissions on parent directory
        if not os.access(parent_dir, os.W_OK):
            raise PermissionError(f"No write permission for directory: {parent_dir}")
        
        # If file exists, check if it's writable
        if path.exists():
            if not os.access(path, os.W_OK):
                raise PermissionError(f"No write permission for file: {file_path}")
        
        return True
    
    def _validate_export_inputs(self, data: pd.DataFrame, file_path: str, format_type: str) -> None:
        """
        Validate inputs for export operations.
        
        Args:
            data: DataFrame to validate
            file_path: File path to validate
            format_type: Format type to validate
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        if data.empty:
            raise ValueError("Cannot export empty DataFrame")
        
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Validate file path
        self.validate_file_path(file_path)
        
        # Validate file extension matches format
        path = Path(file_path)
        if format_type == 'csv' and path.suffix.lower() not in ['.csv']:
            raise ValueError("CSV format requires .csv file extension")
        elif format_type == 'excel' and path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError("Excel format requires .xlsx or .xls file extension")
    
    def _ensure_directory_exists(self, file_path: str) -> None:
        """
        Ensure the directory for the given file path exists.
        
        Args:
            file_path: The file path whose directory should exist
        """
        directory = Path(file_path).parent
        directory.mkdir(parents=True, exist_ok=True)