"""
Script to create sample test files for demonstrating the file comparison tool.
"""

import pandas as pd
import os

def create_sample_files():
    """Create sample CSV and Excel files for testing."""
    
    # Create test data directory
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Sample data 1 - Customer list
    customers_data = {
        'Name': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
        'Email': ['john.smith@email.com', 'jane.doe@email.com', 'bob.johnson@email.com', 
                 'alice.brown@email.com', 'charlie.wilson@email.com'],
        'Phone': ['555-0101', '555-0102', '555-0103', '555-0104', '555-0105'],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    }
    
    customers_df = pd.DataFrame(customers_data)
    
    # Save as CSV
    customers_df.to_csv(os.path.join(test_dir, 'customers.csv'), index=False)
    print(f"Created {test_dir}/customers.csv with {len(customers_df)} rows")
    
    # Save as Excel
    customers_df.to_excel(os.path.join(test_dir, 'customers.xlsx'), index=False)
    print(f"Created {test_dir}/customers.xlsx with {len(customers_df)} rows")
    
    # Sample data 2 - Subscribers list (with some overlap)
    subscribers_data = {
        'Full_Name': ['Jane Doe', 'Bob Johnson', 'David Miller', 'Emma Davis', 'Frank Taylor'],
        'Email_Address': ['jane.doe@email.com', 'bob.johnson@email.com', 'david.miller@email.com',
                         'emma.davis@email.com', 'frank.taylor@email.com'],
        'Subscription_Type': ['Premium', 'Basic', 'Premium', 'Basic', 'Premium'],
        'Join_Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12']
    }
    
    subscribers_df = pd.DataFrame(subscribers_data)
    
    # Save as CSV
    subscribers_df.to_csv(os.path.join(test_dir, 'subscribers.csv'), index=False)
    print(f"Created {test_dir}/subscribers.csv with {len(subscribers_df)} rows")
    
    # Save as Excel
    subscribers_df.to_excel(os.path.join(test_dir, 'subscribers.xlsx'), index=False)
    print(f"Created {test_dir}/subscribers.xlsx with {len(subscribers_df)} rows")
    
    # Sample data 3 - Large dataset for performance testing
    import random
    
    large_data = {
        'ID': range(1, 1001),
        'Name': [f'User_{i:04d}' for i in range(1, 1001)],
        'Email': [f'user{i:04d}@example.com' for i in range(1, 1001)],
        'Department': [random.choice(['Sales', 'Marketing', 'Engineering', 'HR', 'Finance']) for _ in range(1000)],
        'Salary': [random.randint(30000, 120000) for _ in range(1000)],
        'Join_Year': [random.randint(2015, 2023) for _ in range(1000)]
    }
    
    large_df = pd.DataFrame(large_data)
    
    # Save as CSV
    large_df.to_csv(os.path.join(test_dir, 'employees_large.csv'), index=False)
    print(f"Created {test_dir}/employees_large.csv with {len(large_df)} rows")
    
    print(f"\nTest files created in '{test_dir}' directory:")
    print("- customers.csv / customers.xlsx (5 rows)")
    print("- subscribers.csv / subscribers.xlsx (5 rows)")  
    print("- employees_large.csv (1000 rows)")
    print("\nYou can use these files to test the file selection panel!")

if __name__ == "__main__":
    create_sample_files()