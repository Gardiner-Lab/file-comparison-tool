"""
Comparison Engine for File Comparison Tool.

This module provides the core comparison functionality for performing various
set operations between two datasets based on specified columns.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Set, Any, Optional, Callable
import time
from models.data_models import OperationResult
from .performance_optimizer import PerformanceOptimizer


class ComparisonEngine:
    """
    Engine for performing comparison operations between two datasets.
    
    Supports operations like removing matches, keeping only matches,
    finding common values, and finding unique values between datasets.
    """
    
    def __init__(self):
        """Initialize the comparison engine."""
        self.supported_operations = {
            'remove_matches',
            'keep_matches', 
            'find_common',
            'find_unique'
        }
        self.performance_optimizer = PerformanceOptimizer()
        self.cancelled = False
    
    def validate_column_compatibility(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                                    col1: str, col2: str) -> Tuple[bool, str]:
        """
        Validate that two columns are compatible for comparison.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            
        Returns:
            Tuple of (is_compatible, error_message)
        """
        # Check if columns exist
        if col1 not in df1.columns:
            return False, f"Column '{col1}' not found in first file"
        
        if col2 not in df2.columns:
            return False, f"Column '{col2}' not found in second file"
        
        # Get column data types
        dtype1 = df1[col1].dtype
        dtype2 = df2[col2].dtype
        
        # Check for empty columns (but allow empty DataFrames)
        if len(df1) > 0 and df1[col1].isna().all():
            return False, f"Column '{col1}' in first file contains only null values"
        
        if len(df2) > 0 and df2[col2].isna().all():
            return False, f"Column '{col2}' in second file contains only null values"
        
        # Define compatible type groups
        numeric_types = ['int64', 'int32', 'float64', 'float32', 'number']
        string_types = ['object', 'string']
        datetime_types = ['datetime64[ns]', 'datetime']
        
        def get_type_group(dtype):
            dtype_str = str(dtype)
            if any(t in dtype_str for t in numeric_types):
                return 'numeric'
            elif any(t in dtype_str for t in datetime_types):
                return 'datetime'
            else:
                return 'string'
        
        type_group1 = get_type_group(dtype1)
        type_group2 = get_type_group(dtype2)
        
        if type_group1 != type_group2:
            return False, (f"Incompatible column types: '{col1}' is {type_group1} "
                          f"but '{col2}' is {type_group2}")
        
        return True, "Columns are compatible"
    
    def _prepare_comparison_values(self, df1: pd.DataFrame, df2: pd.DataFrame,
                                 col1: str, col2: str, case_sensitive: bool = True) -> Tuple[Set[Any], Set[Any]]:
        """
        Prepare values from both columns for comparison.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame  
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            case_sensitive: Whether to perform case-sensitive comparison
            
        Returns:
            Tuple of (set1, set2) containing prepared values
        """
        # Get non-null values
        values1 = df1[col1].dropna()
        values2 = df2[col2].dropna()
        
        # Handle case sensitivity for string columns
        if not case_sensitive:
            # Check if columns contain string-like data
            if values1.dtype == 'object' or str(values1.dtype) == 'string':
                values1 = values1.astype(str).str.lower()
            if values2.dtype == 'object' or str(values2.dtype) == 'string':
                values2 = values2.astype(str).str.lower()
        
        return set(values1), set(values2)
    
    def remove_matches(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                      col1: str, col2: str, case_sensitive: bool = True,
                      progress_callback: Optional[Callable[[float, str], None]] = None) -> OperationResult:
        """
        Remove rows from df2 where the comparison column matches values in df1.
        
        Args:
            df1: First DataFrame (source of values to remove)
            df2: Second DataFrame (target for removal)
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            case_sensitive: Whether comparison should be case sensitive
            progress_callback: Optional callback for progress updates
            
        Returns:
            OperationResult containing the processed data and metadata
        """
        start_time = time.time()
        original_count = len(df2)
        
        # Check for cancellation
        if self.cancelled:
            raise InterruptedError("Operation was cancelled")
        
        # Validate column compatibility
        is_compatible, error_msg = self.validate_column_compatibility(df1, df2, col1, col2)
        if not is_compatible:
            raise ValueError(f"Column compatibility error: {error_msg}")
        
        # Use performance optimizer for large datasets
        total_rows = len(df1) + len(df2)
        if total_rows > 10000 and progress_callback:
            # Use optimized processing
            result_df = self.performance_optimizer.optimize_comparison_operation(
                df1, df2, col1, col2, 'remove_matches', case_sensitive, progress_callback
            )
        else:
            # Standard processing for smaller datasets
            if progress_callback:
                progress_callback(25, "Preparing comparison values...")
            
            # Prepare comparison values
            values1, values2 = self._prepare_comparison_values(df1, df2, col1, col2, case_sensitive)
            
            if progress_callback:
                progress_callback(50, "Removing matching rows...")
            
            # Create mask for rows to keep (not in df1)
            if case_sensitive:
                mask = ~df2[col2].isin(df1[col1])
            else:
                # For case-insensitive comparison
                if df2[col2].dtype == 'object' or str(df2[col2].dtype) == 'string':
                    df2_lower = df2[col2].astype(str).str.lower()
                    df1_lower = df1[col1].astype(str).str.lower()
                    mask = ~df2_lower.isin(df1_lower)
                else:
                    mask = ~df2[col2].isin(df1[col1])
            
            result_df = df2[mask].copy()
            
            if progress_callback:
                progress_callback(90, "Finalizing results...")
        
        result_count = len(result_df)
        processing_time = time.time() - start_time
        
        summary = (f"Removed {original_count - result_count} matching rows. "
                  f"Result contains {result_count} rows.")
        
        return OperationResult(
            result_data=result_df,
            original_count=original_count,
            result_count=result_count,
            operation_type='remove_matches',
            processing_time=processing_time,
            summary=summary
        )
    
    def keep_only_matches(self, df1: pd.DataFrame, df2: pd.DataFrame,
                         col1: str, col2: str, case_sensitive: bool = True,
                         progress_callback: Optional[Callable[[float, str], None]] = None) -> OperationResult:
        """
        Keep only rows from df2 where the comparison column matches values in df1.
        
        Args:
            df1: First DataFrame (source of values to keep)
            df2: Second DataFrame (target for filtering)
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            case_sensitive: Whether comparison should be case sensitive
            progress_callback: Optional callback for progress updates
            
        Returns:
            OperationResult containing the processed data and metadata
        """
        start_time = time.time()
        original_count = len(df2)
        
        # Check for cancellation
        if self.cancelled:
            raise InterruptedError("Operation was cancelled")
        
        # Validate column compatibility
        is_compatible, error_msg = self.validate_column_compatibility(df1, df2, col1, col2)
        if not is_compatible:
            raise ValueError(f"Column compatibility error: {error_msg}")
        
        # Use performance optimizer for large datasets
        total_rows = len(df1) + len(df2)
        if total_rows > 10000 and progress_callback:
            # Use optimized processing
            result_df = self.performance_optimizer.optimize_comparison_operation(
                df1, df2, col1, col2, 'keep_matches', case_sensitive, progress_callback
            )
        else:
            # Standard processing for smaller datasets
            if progress_callback:
                progress_callback(25, "Preparing comparison...")
            
            # Create mask for rows to keep (in df1)
            if case_sensitive:
                mask = df2[col2].isin(df1[col1])
            else:
                # For case-insensitive comparison
                if df2[col2].dtype == 'object' or str(df2[col2].dtype) == 'string':
                    df2_lower = df2[col2].astype(str).str.lower()
                    df1_lower = df1[col1].astype(str).str.lower()
                    mask = df2_lower.isin(df1_lower)
                else:
                    mask = df2[col2].isin(df1[col1])
            
            if progress_callback:
                progress_callback(75, "Filtering matching rows...")
            
            result_df = df2[mask].copy()
        
        result_count = len(result_df)
        processing_time = time.time() - start_time
        
        summary = (f"Kept {result_count} matching rows from {original_count} total rows. "
                  f"Removed {original_count - result_count} non-matching rows.")
        
        return OperationResult(
            result_data=result_df,
            original_count=original_count,
            result_count=result_count,
            operation_type='keep_only_matches',
            processing_time=processing_time,
            summary=summary
        )
    
    def find_common_values(self, df1: pd.DataFrame, df2: pd.DataFrame,
                          col1: str, col2: str, case_sensitive: bool = True,
                          progress_callback: Optional[Callable[[float, str], None]] = None) -> OperationResult:
        """
        Find rows that exist in both DataFrames based on the comparison columns.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            OperationResult containing the processed data and metadata
        """
        start_time = time.time()
        original_count = len(df1) + len(df2)
        
        # Validate column compatibility
        is_compatible, error_msg = self.validate_column_compatibility(df1, df2, col1, col2)
        if not is_compatible:
            raise ValueError(f"Column compatibility error: {error_msg}")
        
        # Prepare comparison values
        values1, values2 = self._prepare_comparison_values(df1, df2, col1, col2, case_sensitive)
        common_values = values1.intersection(values2)
        
        # Get rows from both DataFrames that have common values
        if case_sensitive:
            df1_common = df1[df1[col1].isin(common_values)].copy()
            df2_common = df2[df2[col2].isin(common_values)].copy()
        else:
            # For case-insensitive comparison
            if df1[col1].dtype == 'object' or str(df1[col1].dtype) == 'string':
                df1_lower = df1[col1].astype(str).str.lower()
                df1_common = df1[df1_lower.isin(common_values)].copy()
            else:
                df1_common = df1[df1[col1].isin(common_values)].copy()
                
            if df2[col2].dtype == 'object' or str(df2[col2].dtype) == 'string':
                df2_lower = df2[col2].astype(str).str.lower()
                df2_common = df2[df2_lower.isin(common_values)].copy()
            else:
                df2_common = df2[df2[col2].isin(common_values)].copy()
        
        # Add source column to identify which file each row came from
        df1_common['_source_file'] = 'file1'
        df2_common['_source_file'] = 'file2'
        
        # Combine results
        result_df = pd.concat([df1_common, df2_common], ignore_index=True)
        result_count = len(result_df)
        processing_time = time.time() - start_time
        
        summary = (f"Found {len(common_values)} common values. "
                  f"Result contains {result_count} rows from both files.")
        
        return OperationResult(
            result_data=result_df,
            original_count=original_count,
            result_count=result_count,
            operation_type='find_common_values',
            processing_time=processing_time,
            summary=summary
        )
    
    def find_unique_values(self, df1: pd.DataFrame, df2: pd.DataFrame,
                          col1: str, col2: str, case_sensitive: bool = True,
                          progress_callback: Optional[Callable[[float, str], None]] = None) -> OperationResult:
        """
        Find rows that exist in only one of the DataFrames based on the comparison columns.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            OperationResult containing the processed data and metadata
        """
        start_time = time.time()
        original_count = len(df1) + len(df2)
        
        # Validate column compatibility
        is_compatible, error_msg = self.validate_column_compatibility(df1, df2, col1, col2)
        if not is_compatible:
            raise ValueError(f"Column compatibility error: {error_msg}")
        
        # Prepare comparison values
        values1, values2 = self._prepare_comparison_values(df1, df2, col1, col2, case_sensitive)
        
        # Find values unique to each dataset
        unique_to_df1 = values1 - values2
        unique_to_df2 = values2 - values1
        
        # Get rows with unique values
        if case_sensitive:
            df1_unique = df1[df1[col1].isin(unique_to_df1)].copy()
            df2_unique = df2[df2[col2].isin(unique_to_df2)].copy()
        else:
            # For case-insensitive comparison
            if df1[col1].dtype == 'object' or str(df1[col1].dtype) == 'string':
                df1_lower = df1[col1].astype(str).str.lower()
                df1_unique = df1[df1_lower.isin(unique_to_df1)].copy()
            else:
                df1_unique = df1[df1[col1].isin(unique_to_df1)].copy()
                
            if df2[col2].dtype == 'object' or str(df2[col2].dtype) == 'string':
                df2_lower = df2[col2].astype(str).str.lower()
                df2_unique = df2[df2_lower.isin(unique_to_df2)].copy()
            else:
                df2_unique = df2[df2[col2].isin(unique_to_df2)].copy()
        
        # Add source column to identify which file each row came from
        df1_unique['_source_file'] = 'file1'
        df2_unique['_source_file'] = 'file2'
        
        # Combine results
        result_df = pd.concat([df1_unique, df2_unique], ignore_index=True)
        result_count = len(result_df)
        processing_time = time.time() - start_time
        
        summary = (f"Found {len(unique_to_df1)} values unique to file1 and "
                  f"{len(unique_to_df2)} values unique to file2. "
                  f"Result contains {result_count} rows.")
        
        return OperationResult(
            result_data=result_df,
            original_count=original_count,
            result_count=result_count,
            operation_type='find_unique_values',
            processing_time=processing_time,
            summary=summary
        )
    
    def cancel_operation(self):
        """Cancel the current operation."""
        self.cancelled = True
        if hasattr(self.performance_optimizer, 'cancel_operation'):
            self.performance_optimizer.cancel_operation()
    
    def reset_cancellation(self):
        """Reset cancellation state for new operations."""
        self.cancelled = False
        if hasattr(self.performance_optimizer, 'reset_cancellation'):
            self.performance_optimizer.reset_cancellation()
    
    def estimate_processing_time(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                               operation: str) -> float:
        """
        Estimate processing time for an operation.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            operation: Operation type
            
        Returns:
            Estimated time in seconds
        """
        return self.performance_optimizer.estimate_processing_time(df1, df2, operation)