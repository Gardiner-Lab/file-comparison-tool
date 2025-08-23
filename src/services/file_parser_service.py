"""
File parsing service for the File Comparison Tool.

This module provides functionality to parse Excel and CSV files, validate file formats,
and extract metadata. It handles various file formats and provides comprehensive error
handling for unsupported formats and corrupted files.
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from models.data_models import FileInfo


class FileParsingError(Exception):
    """Custom exception for file parsing errors."""
    pass


class UnsupportedFileFormatError(FileParsingError):
    """Exception raised when file format is not supported."""
    pass


class FileParserService:
    """
    Service class for parsing Excel and CSV files with validation and metadata extraction.
    
    This service handles file format validation, parsing, and metadata extraction
    for Excel (.xlsx, .xls) and CSV (.csv) files. It provides comprehensive error
    handling and user-friendly error messages.
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    
    def __init__(self):
        """Initialize the FileParserService."""
        self._encoding_fallbacks = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def validate_file_format(self, file_path: str) -> bool:
        """
        Validate that the file format is supported.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file format is supported, False otherwise
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            UnsupportedFileFormatError: If the file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        return True
    
    def get_file_info(self, file_path: str) -> Dict[str, Union[str, int, datetime, List[str]]]:
        """
        Extract metadata from a file without fully parsing it.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            FileParsingError: If metadata extraction fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Get basic file stats
            stat = os.stat(file_path)
            file_size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Determine file type
            file_extension = Path(file_path).suffix.lower()
            file_type = 'excel' if file_extension in ['.xlsx', '.xls'] else 'csv'
            
            # Get column information and row count
            columns, row_count = self._extract_basic_info(file_path, file_type)
            
            return {
                'file_path': file_path,
                'file_type': file_type,
                'columns': columns,
                'row_count': row_count,
                'file_size': file_size,
                'last_modified': last_modified
            }
            
        except Exception as e:
            raise FileParsingError(f"Failed to extract file metadata: {str(e)}")
    
    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse a file and return a pandas DataFrame.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Parsed DataFrame
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            UnsupportedFileFormatError: If the file format is not supported
            FileParsingError: If parsing fails
        """
        # Validate file format first
        self.validate_file_format(file_path)
        
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.csv':
                return self._parse_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                return self._parse_excel(file_path)
            else:
                raise UnsupportedFileFormatError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            if isinstance(e, (UnsupportedFileFormatError, FileParsingError)):
                raise
            raise FileParsingError(f"Failed to parse file {file_path}: {str(e)}")
    
    def create_file_info(self, file_path: str) -> FileInfo:
        """
        Create a FileInfo object with complete metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object with complete metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            UnsupportedFileFormatError: If the file format is not supported
            FileParsingError: If metadata extraction fails
        """
        metadata = self.get_file_info(file_path)
        
        return FileInfo(
            file_path=metadata['file_path'],
            file_type=metadata['file_type'],
            columns=metadata['columns'],
            row_count=metadata['row_count'],
            file_size=metadata['file_size'],
            last_modified=metadata['last_modified']
        )
    
    def _parse_csv(self, file_path: str) -> pd.DataFrame:
        """
        Parse a CSV file with encoding fallback.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Parsed DataFrame
            
        Raises:
            FileParsingError: If parsing fails with all encoding attempts
        """
        last_error = None
        
        for encoding in self._encoding_fallbacks:
            try:
                # Try with error_bad_lines=False for malformed CSV files
                df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip')
                # Validate that we got some data
                if df.empty:
                    raise FileParsingError("CSV file is empty or contains no valid data")
                return df
                
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                raise FileParsingError(f"Failed to parse CSV file: {str(e)}")
        
        raise FileParsingError(
            f"Failed to parse CSV file with any supported encoding. "
            f"Last error: {str(last_error)}"
        )
    
    def _parse_excel(self, file_path: str) -> pd.DataFrame:
        """
        Parse an Excel file.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Parsed DataFrame
            
        Raises:
            FileParsingError: If parsing fails
        """
        try:
            # Try to read the first sheet
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Validate that we got some data
            if df.empty:
                raise FileParsingError("Excel file is empty or contains no valid data")
            
            return df
            
        except Exception as e:
            raise FileParsingError(f"Failed to parse Excel file: {str(e)}")
    
    def _extract_basic_info(self, file_path: str, file_type: str) -> Tuple[List[str], int]:
        """
        Extract basic information (columns and row count) without loading full file.
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('csv' or 'excel')
            
        Returns:
            Tuple of (column_names, row_count)
            
        Raises:
            FileParsingError: If extraction fails
        """
        try:
            if file_type == 'csv':
                # Read just the header and a small sample to get info
                sample_df = pd.read_csv(file_path, nrows=0)  # Just header
                columns = sample_df.columns.tolist()
                
                # Count rows efficiently
                with open(file_path, 'r', encoding='utf-8') as f:
                    row_count = sum(1 for _ in f) - 1  # Subtract header row
                    
            else:  # Excel
                # Read just the header
                sample_df = pd.read_excel(file_path, nrows=0)
                columns = sample_df.columns.tolist()
                
                # For Excel, we need to read the full file to count rows efficiently
                # This is a limitation of Excel format
                full_df = pd.read_excel(file_path)
                row_count = len(full_df)
            
            return columns, max(0, row_count)  # Ensure non-negative row count
            
        except Exception as e:
            raise FileParsingError(f"Failed to extract basic file information: {str(e)}")