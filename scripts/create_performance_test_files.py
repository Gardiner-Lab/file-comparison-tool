"""
Create large test files for performance testing.

This script generates large CSV and Excel files with various data patterns
to test the performance optimization features of the File Comparison Tool.
"""

import pandas as pd
import numpy as np
import os
import time
from typing import Tuple


def create_large_test_files():
    """Create large test files for performance testing."""
    print("Creating large test files for performance testing...")
    
    # Ensure test_data directory exists
    os.makedirs('test_data', exist_ok=True)
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Create large datasets with different characteristics
    datasets = [
        ("large_customers_50k.csv", 50000, "customers"),
        ("large_subscribers_75k.csv", 75000, "subscribers"),
        ("huge_dataset_100k.csv", 100000, "users"),
        ("performance_test_25k.xlsx", 25000, "contacts")
    ]
    
    for filename, size, prefix in datasets:
        print(f"Creating {filename} with {size:,} rows...")
        start_time = time.time()
        
        # Create dataset
        df = create_test_dataset(size, prefix)
        
        # Save file
        filepath = os.path.join('test_data', filename)
        if filename.endswith('.xlsx'):
            df.to_excel(filepath, index=False)
        else:
            df.to_csv(filepath, index=False)
            
        creation_time = time.time() - start_time
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        print(f"  Created in {creation_time:.2f}s, size: {file_size_mb:.1f}MB")
    
    # Create overlapping datasets for comparison testing
    print("\nCreating overlapping datasets for comparison testing...")
    create_overlapping_datasets()
    
    print("\nPerformance test files created successfully!")


def create_test_dataset(size: int, prefix: str) -> pd.DataFrame:
    """
    Create a test dataset with realistic data patterns.
    
    Args:
        size: Number of rows to create
        prefix: Prefix for generated data
        
    Returns:
        Generated DataFrame
    """
    # Generate email addresses with some duplicates
    unique_emails = int(size * 0.95)  # 5% duplicates
    base_emails = [f'{prefix}{i}@example.com' for i in range(unique_emails)]
    duplicate_emails = np.random.choice(base_emails, size - unique_emails)
    all_emails = base_emails + duplicate_emails.tolist()
    np.random.shuffle(all_emails)
    
    # Generate names
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    names = [
        f'{np.random.choice(first_names)} {np.random.choice(last_names)}'
        for _ in range(size)
    ]
    
    # Generate other realistic columns
    companies = ['TechCorp', 'DataSoft', 'CloudInc', 'WebSolutions', 'AppDev', 'SystemsPro']
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
    
    df = pd.DataFrame({
        'email': all_emails[:size],
        'name': names,
        'company': np.random.choice(companies, size),
        'department': np.random.choice(departments, size),
        'salary': np.random.randint(30000, 150000, size),
        'age': np.random.randint(22, 65, size),
        'join_date': pd.date_range('2020-01-01', '2024-12-31', periods=size),
        'active': np.random.choice([True, False], size, p=[0.8, 0.2]),
        'score': np.random.uniform(0, 100, size).round(2),
        'notes': [f'Note for {prefix} {i}' for i in range(size)]
    })
    
    return df


def create_overlapping_datasets():
    """Create datasets with controlled overlap for testing comparison operations."""
    
    # Dataset 1: 10,000 records
    size1 = 10000
    emails1 = [f'user{i}@test.com' for i in range(size1)]
    
    df1 = pd.DataFrame({
        'email': emails1,
        'name': [f'User {i}' for i in range(size1)],
        'type': 'customer',
        'value': np.random.randint(1, 1000, size1)
    })
    
    # Dataset 2: 15,000 records with 5,000 overlapping emails
    overlap_size = 5000
    unique_size2 = 10000
    
    # Overlapping emails (from middle of dataset 1)
    overlap_start = size1 // 2 - overlap_size // 2
    overlapping_emails = emails1[overlap_start:overlap_start + overlap_size]
    
    # Unique emails for dataset 2
    unique_emails2 = [f'subscriber{i}@test.com' for i in range(unique_size2)]
    
    # Combine for dataset 2
    all_emails2 = overlapping_emails + unique_emails2
    np.random.shuffle(all_emails2)
    
    df2 = pd.DataFrame({
        'email': all_emails2,
        'name': [f'Contact {i}' for i in range(len(all_emails2))],
        'type': 'subscriber',
        'value': np.random.randint(1, 1000, len(all_emails2))
    })
    
    # Save overlapping datasets
    df1.to_csv('test_data/overlap_dataset1_10k.csv', index=False)
    df2.to_csv('test_data/overlap_dataset2_15k.csv', index=False)
    
    print(f"Created overlapping datasets:")
    print(f"  Dataset 1: {len(df1):,} rows")
    print(f"  Dataset 2: {len(df2):,} rows")
    print(f"  Expected overlap: {overlap_size:,} emails")
    
    # Create very large overlapping datasets for stress testing
    create_stress_test_datasets()


def create_stress_test_datasets():
    """Create very large datasets for stress testing."""
    print("Creating stress test datasets...")
    
    # Large dataset 1: 50,000 records
    size1 = 50000
    emails1 = [f'large_user{i}@company.com' for i in range(size1)]
    
    df1 = pd.DataFrame({
        'email': emails1,
        'employee_id': [f'EMP{i:06d}' for i in range(size1)],
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'], size1),
        'salary': np.random.randint(40000, 200000, size1),
        'hire_date': pd.date_range('2015-01-01', '2024-12-31', periods=size1)
    })
    
    # Large dataset 2: 75,000 records with 25,000 overlapping
    overlap_size = 25000
    unique_size2 = 50000
    
    # Overlapping emails
    overlapping_emails = emails1[:overlap_size]
    
    # Unique emails for dataset 2
    unique_emails2 = [f'external_contact{i}@partner.com' for i in range(unique_size2)]
    
    # Combine
    all_emails2 = overlapping_emails + unique_emails2
    np.random.shuffle(all_emails2)
    
    df2 = pd.DataFrame({
        'email': all_emails2,
        'contact_id': [f'CNT{i:06d}' for i in range(len(all_emails2))],
        'company': np.random.choice(['PartnerA', 'PartnerB', 'PartnerC', 'ClientX', 'ClientY'], len(all_emails2)),
        'relationship': np.random.choice(['customer', 'vendor', 'partner'], len(all_emails2)),
        'last_contact': pd.date_range('2023-01-01', '2024-12-31', periods=len(all_emails2))
    })
    
    # Save stress test datasets
    df1.to_csv('test_data/stress_employees_50k.csv', index=False)
    df2.to_csv('test_data/stress_contacts_75k.csv', index=False)
    
    print(f"Created stress test datasets:")
    print(f"  Employees: {len(df1):,} rows")
    print(f"  Contacts: {len(df2):,} rows")
    print(f"  Expected overlap: {overlap_size:,} emails")


def create_memory_test_datasets():
    """Create datasets specifically for memory usage testing."""
    print("Creating memory test datasets...")
    
    # Dataset with wide columns (many columns)
    size = 20000
    
    # Base data
    emails = [f'memory_test{i}@example.com' for i in range(size)]
    
    # Create DataFrame with many columns
    data = {'email': emails}
    
    # Add many text columns
    for i in range(50):
        data[f'text_col_{i}'] = [f'Text data {i} for row {j}' for j in range(size)]
    
    # Add many numeric columns
    for i in range(30):
        data[f'num_col_{i}'] = np.random.randint(1, 10000, size)
    
    # Add many date columns
    for i in range(10):
        data[f'date_col_{i}'] = pd.date_range('2020-01-01', periods=size, freq='D')
    
    df = pd.DataFrame(data)
    
    # Save memory test dataset
    df.to_csv('test_data/memory_test_wide_20k.csv', index=False)
    
    print(f"Created memory test dataset: {len(df):,} rows x {len(df.columns)} columns")
    
    # Create dataset with very long text fields
    long_text_data = {
        'email': emails[:10000],
        'description': [f'Very long description text ' * 100 + f' for record {i}' for i in range(10000)],
        'notes': [f'Extended notes field ' * 50 + f' record {i}' for i in range(10000)],
        'comments': [f'Detailed comments ' * 75 + f' item {i}' for i in range(10000)]
    }
    
    df_long = pd.DataFrame(long_text_data)
    df_long.to_csv('test_data/memory_test_long_text_10k.csv', index=False)
    
    print(f"Created long text dataset: {len(df_long):,} rows with long text fields")


def benchmark_file_operations():
    """Benchmark file creation and loading operations."""
    print("\nBenchmarking file operations...")
    
    test_files = [
        'test_data/large_customers_50k.csv',
        'test_data/overlap_dataset1_10k.csv',
        'test_data/stress_employees_50k.csv'
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"\nTesting {os.path.basename(filepath)}:")
            
            # Test loading time
            start_time = time.time()
            df = pd.read_csv(filepath)
            load_time = time.time() - start_time
            
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            
            print(f"  File size: {file_size_mb:.1f}MB")
            print(f"  Load time: {load_time:.2f}s")
            print(f"  Memory usage: {memory_usage_mb:.1f}MB")
            print(f"  Rows: {len(df):,}, Columns: {len(df.columns)}")


if __name__ == '__main__':
    print("Performance Test File Generator")
    print("=" * 40)
    
    start_time = time.time()
    
    # Create all test files
    create_large_test_files()
    create_memory_test_datasets()
    
    # Benchmark operations
    benchmark_file_operations()
    
    total_time = time.time() - start_time
    print(f"\nTotal generation time: {total_time:.2f}s")
    
    # List all created files
    print("\nCreated files:")
    test_data_dir = 'test_data'
    if os.path.exists(test_data_dir):
        for filename in sorted(os.listdir(test_data_dir)):
            if filename.endswith(('.csv', '.xlsx')):
                filepath = os.path.join(test_data_dir, filename)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  {filename}: {size_mb:.1f}MB")
    
    print("\nPerformance test files are ready!")
    print("Use these files to test:")
    print("- Progress indicators with large datasets")
    print("- Memory optimization with chunked processing")
    print("- Cancellation during long operations")
    print("- Performance benchmarks")