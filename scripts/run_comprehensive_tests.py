#!/usr/bin/env python3
"""
Comprehensive test runner script for the file comparison tool.
Executes all test categories and generates detailed reports.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_comprehensive_suite import ComprehensiveTestSuite
from tests.test_data_generator import TestDataGenerator


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive test suite')
    parser.add_argument('--category', choices=['unit', 'integration', 'gui', 'performance', 'all'], 
                       default='all', help='Test category to run')
    parser.add_argument('--generate-data', action='store_true', 
                       help='Generate test data files before running tests')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick tests only (skip performance tests)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("File Comparison Tool - Comprehensive Test Suite")
    print("=" * 50)
    
    # Generate test data if requested
    if args.generate_data:
        print("Generating test data files...")
        generator = TestDataGenerator('test_data')
        generator.generate_all_test_files()
        print("Test data generation complete.\n")
    
    # Initialize test suite
    suite = ComprehensiveTestSuite()
    
    try:
        if args.category == 'all':
            # Run complete suite
            report = suite.run_comprehensive_suite()
        else:
            # Run specific category
            suite.setup_test_environment()
            
            if args.category == 'unit':
                result = suite.run_unit_tests()
            elif args.category == 'integration':
                result = suite.run_integration_tests()
            elif args.category == 'gui':
                result = suite.run_gui_tests()
            elif args.category == 'performance':
                result = suite.run_performance_tests()
            
            print(f"\n{args.category.title()} Tests Results:")
            print(f"Tests Run: {result['tests_run']}")
            print(f"Failures: {result['failures']}")
            print(f"Errors: {result['errors']}")
            print(f"Success Rate: {result['success_rate']:.1f}%")
        
        print("\nTest execution completed successfully!")
        return 0
        
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())