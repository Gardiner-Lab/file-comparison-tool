"""
Performance Optimizer for File Comparison Tool.

This module provides performance optimization utilities including chunked processing,
memory management, and efficient pandas operations for large datasets.
"""

import pandas as pd
import numpy as np
import gc
import time
import psutil
import os
from typing import Iterator, Tuple, Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    processing_time: float
    memory_peak_mb: float
    memory_start_mb: float
    memory_end_mb: float
    rows_processed: int
    chunks_processed: int
    average_chunk_time: float


class MemoryMonitor:
    """Monitor memory usage during operations."""
    
    def __init__(self):
        """Initialize memory monitor."""
        self.process = psutil.Process(os.getpid())
        self.peak_memory = 0
        self.start_memory = 0
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start memory monitoring in background thread."""
        self.start_memory = self.get_current_memory()
        self.peak_memory = self.start_memory
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                try:
                    current_memory = self.get_current_memory()
                    self.peak_memory = max(self.peak_memory, current_memory)
                    time.sleep(0.1)  # Check every 100ms
                except Exception:
                    break
                    
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> Tuple[float, float, float]:
        """
        Stop monitoring and return metrics.
        
        Returns:
            Tuple of (start_mb, peak_mb, end_mb)
        """
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
        end_memory = self.get_current_memory()
        return self.start_memory, self.peak_memory, end_memory
        
    def get_current_memory(self) -> float:
        """Get current memory usage in MB."""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0


class ChunkedProcessor:
    """
    Processor for handling large datasets in chunks to optimize memory usage.
    
    Provides chunked processing capabilities with progress tracking and
    memory management for large file operations.
    """
    
    def __init__(self, chunk_size: int = 10000, max_memory_mb: int = 500):
        """
        Initialize chunked processor.
        
        Args:
            chunk_size: Number of rows per chunk
            max_memory_mb: Maximum memory usage threshold in MB
        """
        self.chunk_size = chunk_size
        self.max_memory_mb = max_memory_mb
        self.memory_monitor = MemoryMonitor()
        
    def process_dataframe_chunks(self, df: pd.DataFrame, 
                                process_func: Callable[[pd.DataFrame], pd.DataFrame],
                                progress_callback: Optional[Callable[[float, str], None]] = None) -> pd.DataFrame:
        """
        Process a DataFrame in chunks.
        
        Args:
            df: DataFrame to process
            process_func: Function to apply to each chunk
            progress_callback: Optional progress callback function
            
        Returns:
            Processed DataFrame
        """
        if len(df) <= self.chunk_size:
            # Small dataset, process directly
            if progress_callback:
                progress_callback(0, "Processing data...")
            result = process_func(df)
            if progress_callback:
                progress_callback(100, "Processing complete")
            return result
            
        # Start memory monitoring
        self.memory_monitor.start_monitoring()
        start_time = time.time()
        
        try:
            # Calculate chunks
            total_chunks = (len(df) + self.chunk_size - 1) // self.chunk_size
            processed_chunks = []
            
            for i, chunk in enumerate(self._chunk_dataframe(df)):
                if progress_callback:
                    progress = (i / total_chunks) * 100
                    progress_callback(progress, f"Processing chunk {i + 1} of {total_chunks}...")
                
                # Process chunk
                processed_chunk = process_func(chunk)
                processed_chunks.append(processed_chunk)
                
                # Memory management
                self._manage_memory()
                
            # Combine results
            if progress_callback:
                progress_callback(95, "Combining results...")
                
            result = pd.concat(processed_chunks, ignore_index=True)
            
            if progress_callback:
                progress_callback(100, "Processing complete")
                
            return result
            
        finally:
            # Stop memory monitoring
            self.memory_monitor.stop_monitoring()
            
    def _chunk_dataframe(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        """
        Generate chunks from a DataFrame.
        
        Args:
            df: DataFrame to chunk
            
        Yields:
            DataFrame chunks
        """
        for i in range(0, len(df), self.chunk_size):
            yield df.iloc[i:i + self.chunk_size].copy()
            
    def _manage_memory(self):
        """Perform memory management operations."""
        # Force garbage collection
        gc.collect()
        
        # Check memory usage
        current_memory = self.memory_monitor.get_current_memory()
        if current_memory > self.max_memory_mb:
            # Additional cleanup if needed
            gc.collect()
            
    def get_optimal_chunk_size(self, df: pd.DataFrame, 
                              target_memory_mb: int = 100) -> int:
        """
        Calculate optimal chunk size based on DataFrame and memory target.
        
        Args:
            df: Sample DataFrame
            target_memory_mb: Target memory usage per chunk
            
        Returns:
            Optimal chunk size
        """
        if len(df) == 0:
            return self.chunk_size
            
        # Estimate memory per row
        sample_size = min(1000, len(df))
        sample_df = df.head(sample_size)
        
        # Get memory usage in bytes
        memory_usage = sample_df.memory_usage(deep=True).sum()
        memory_per_row = memory_usage / sample_size
        
        # Calculate optimal chunk size
        target_memory_bytes = target_memory_mb * 1024 * 1024
        optimal_size = int(target_memory_bytes / memory_per_row)
        
        # Ensure reasonable bounds
        optimal_size = max(1000, min(optimal_size, 50000))
        
        return optimal_size


class PerformanceOptimizer:
    """
    Main performance optimizer with various optimization strategies.
    
    Provides comprehensive performance optimization including chunked processing,
    efficient pandas operations, and memory management.
    """
    
    def __init__(self):
        """Initialize performance optimizer."""
        self.chunked_processor = ChunkedProcessor()
        self.memory_monitor = MemoryMonitor()
        
    def optimize_comparison_operation(self, df1: pd.DataFrame, df2: pd.DataFrame,
                                    col1: str, col2: str, operation: str,
                                    case_sensitive: bool = True,
                                    progress_callback: Optional[Callable[[float, str], None]] = None) -> pd.DataFrame:
        """
        Perform optimized comparison operation with chunked processing.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            col1: Column name in first DataFrame
            col2: Column name in second DataFrame
            operation: Operation type
            case_sensitive: Whether comparison is case sensitive
            progress_callback: Progress callback function
            
        Returns:
            Result DataFrame
        """
        # Start performance monitoring
        start_time = time.time()
        self.memory_monitor.start_monitoring()
        
        try:
            # Determine if chunked processing is needed
            total_rows = len(df1) + len(df2)
            use_chunked = total_rows > 50000  # Threshold for chunked processing
            
            if progress_callback:
                progress_callback(5, "Preparing data for comparison...")
            
            # Optimize DataFrames
            df1_opt = self._optimize_dataframe(df1, [col1])
            df2_opt = self._optimize_dataframe(df2, [col2])
            
            if progress_callback:
                progress_callback(15, "Optimizing comparison columns...")
            
            # Pre-process comparison columns for efficiency
            lookup_set = self._create_optimized_lookup(df1_opt, col1, case_sensitive)
            
            if progress_callback:
                progress_callback(25, f"Performing {operation} operation...")
            
            # Perform operation based on type
            if operation == 'remove_matches':
                result = self._optimized_remove_matches(
                    df2_opt, col2, lookup_set, case_sensitive, 
                    use_chunked, progress_callback
                )
            elif operation == 'keep_matches':
                result = self._optimized_keep_matches(
                    df2_opt, col2, lookup_set, case_sensitive,
                    use_chunked, progress_callback
                )
            elif operation == 'find_common':
                result = self._optimized_find_common(
                    df1_opt, df2_opt, col1, col2, lookup_set, case_sensitive,
                    use_chunked, progress_callback
                )
            elif operation == 'find_unique':
                result = self._optimized_find_unique(
                    df1_opt, df2_opt, col1, col2, lookup_set, case_sensitive,
                    use_chunked, progress_callback
                )
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
            if progress_callback:
                progress_callback(95, "Finalizing results...")
            
            # Final cleanup
            gc.collect()
            
            if progress_callback:
                progress_callback(100, "Operation completed")
                
            return result
            
        finally:
            # Stop monitoring and collect metrics
            start_mem, peak_mem, end_mem = self.memory_monitor.stop_monitoring()
            processing_time = time.time() - start_time
            
    def _optimize_dataframe(self, df: pd.DataFrame, 
                           important_columns: List[str]) -> pd.DataFrame:
        """
        Optimize DataFrame for memory and performance.
        
        Args:
            df: DataFrame to optimize
            important_columns: Columns that will be used in operations
            
        Returns:
            Optimized DataFrame
        """
        df_opt = df.copy()
        
        # Optimize data types for important columns
        for col in important_columns:
            if col in df_opt.columns:
                # Convert object columns to category if beneficial
                if df_opt[col].dtype == 'object':
                    unique_ratio = df_opt[col].nunique() / len(df_opt)
                    if unique_ratio < 0.5:  # Less than 50% unique values
                        df_opt[col] = df_opt[col].astype('category')
                        
        return df_opt
        
    def _create_optimized_lookup(self, df: pd.DataFrame, col: str, 
                               case_sensitive: bool) -> set:
        """
        Create optimized lookup set for comparison operations.
        
        Args:
            df: DataFrame containing lookup values
            col: Column name for lookup
            case_sensitive: Whether lookup is case sensitive
            
        Returns:
            Optimized lookup set
        """
        values = df[col].dropna()
        
        if not case_sensitive and values.dtype == 'object':
            values = values.astype(str).str.lower()
            
        return set(values)
        
    def _optimized_remove_matches(self, df: pd.DataFrame, col: str, 
                                lookup_set: set, case_sensitive: bool,
                                use_chunked: bool,
                                progress_callback: Optional[Callable[[float, str], None]] = None) -> pd.DataFrame:
        """Optimized remove matches operation."""
        if not use_chunked:
            # Direct operation for smaller datasets
            if case_sensitive:
                mask = ~df[col].isin(lookup_set)
            else:
                df_values = df[col].astype(str).str.lower() if df[col].dtype == 'object' else df[col]
                mask = ~df_values.isin(lookup_set)
            return df[mask].copy()
        
        # Chunked processing for large datasets
        def process_chunk(chunk):
            if case_sensitive:
                mask = ~chunk[col].isin(lookup_set)
            else:
                chunk_values = chunk[col].astype(str).str.lower() if chunk[col].dtype == 'object' else chunk[col]
                mask = ~chunk_values.isin(lookup_set)
            return chunk[mask].copy()
            
        return self.chunked_processor.process_dataframe_chunks(
            df, process_chunk, progress_callback
        )
        
    def _optimized_keep_matches(self, df: pd.DataFrame, col: str,
                              lookup_set: set, case_sensitive: bool,
                              use_chunked: bool,
                              progress_callback: Optional[Callable[[float, str], None]] = None) -> pd.DataFrame:
        """Optimized keep matches operation."""
        if not use_chunked:
            # Direct operation for smaller datasets
            if case_sensitive:
                mask = df[col].isin(lookup_set)
            else:
                df_values = df[col].astype(str).str.lower() if df[col].dtype == 'object' else df[col]
                mask = df_values.isin(lookup_set)
            return df[mask].copy()
        
        # Chunked processing for large datasets
        def process_chunk(chunk):
            if case_sensitive:
                mask = chunk[col].isin(lookup_set)
            else:
                chunk_values = chunk[col].astype(str).str.lower() if chunk[col].dtype == 'object' else chunk[col]
                mask = chunk_values.isin(lookup_set)
            return chunk[mask].copy()
            
        return self.chunked_processor.process_dataframe_chunks(
            df, process_chunk, progress_callback
        )
        
    def _optimized_find_common(self, df1: pd.DataFrame, df2: pd.DataFrame,
                             col1: str, col2: str, lookup_set: set,
                             case_sensitive: bool, use_chunked: bool,
                             progress_callback: Optional[Callable[[float, str], None]] = None) -> pd.DataFrame:
        """Optimized find common values operation."""
        # Create lookup set from df2 as well
        df2_values = df2[col2].dropna()
        if not case_sensitive and df2_values.dtype == 'object':
            df2_values = df2_values.astype(str).str.lower()
        df2_set = set(df2_values)
        
        # Find intersection
        common_values = lookup_set.intersection(df2_set)
        
        # Get matching rows from both DataFrames
        if case_sensitive:
            df1_common = df1[df1[col1].isin(common_values)].copy()
            df2_common = df2[df2[col2].isin(common_values)].copy()
        else:
            df1_values = df1[col1].astype(str).str.lower() if df1[col1].dtype == 'object' else df1[col1]
            df2_values = df2[col2].astype(str).str.lower() if df2[col2].dtype == 'object' else df2[col2]
            df1_common = df1[df1_values.isin(common_values)].copy()
            df2_common = df2[df2_values.isin(common_values)].copy()
            
        # Add source indicators
        df1_common['_source_file'] = 'file1'
        df2_common['_source_file'] = 'file2'
        
        return pd.concat([df1_common, df2_common], ignore_index=True)
        
    def _optimized_find_unique(self, df1: pd.DataFrame, df2: pd.DataFrame,
                             col1: str, col2: str, lookup_set: set,
                             case_sensitive: bool, use_chunked: bool,
                             progress_callback: Optional[Callable[[float, str], None]] = None) -> pd.DataFrame:
        """Optimized find unique values operation."""
        # Create lookup set from df2
        df2_values = df2[col2].dropna()
        if not case_sensitive and df2_values.dtype == 'object':
            df2_values = df2_values.astype(str).str.lower()
        df2_set = set(df2_values)
        
        # Find unique values
        unique_to_df1 = lookup_set - df2_set
        unique_to_df2 = df2_set - lookup_set
        
        # Get matching rows
        if case_sensitive:
            df1_unique = df1[df1[col1].isin(unique_to_df1)].copy()
            df2_unique = df2[df2[col2].isin(unique_to_df2)].copy()
        else:
            df1_values = df1[col1].astype(str).str.lower() if df1[col1].dtype == 'object' else df1[col1]
            df2_values = df2[col2].astype(str).str.lower() if df2[col2].dtype == 'object' else df2[col2]
            df1_unique = df1[df1_values.isin(unique_to_df1)].copy()
            df2_unique = df2[df2_values.isin(unique_to_df2)].copy()
            
        # Add source indicators
        df1_unique['_source_file'] = 'file1'
        df2_unique['_source_file'] = 'file2'
        
        return pd.concat([df1_unique, df2_unique], ignore_index=True)
        
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
        total_rows = len(df1) + len(df2)
        
        # Base processing rates (rows per second) - these are rough estimates
        base_rates = {
            'remove_matches': 100000,
            'keep_matches': 100000,
            'find_common': 80000,
            'find_unique': 80000
        }
        
        base_rate = base_rates.get(operation, 50000)
        
        # Adjust for complexity
        if total_rows > 100000:
            base_rate *= 0.8  # Slower for very large datasets
        if total_rows > 500000:
            base_rate *= 0.6  # Even slower for huge datasets
            
        estimated_time = total_rows / base_rate
        return max(1.0, estimated_time)  # Minimum 1 second