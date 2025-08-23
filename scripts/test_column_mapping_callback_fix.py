#!/usr/bin/env python3
"""
Quick verification script for the column mapping callback fix.
Tests that the callback is called with the correct arguments.
"""

import sys
import os
import re

def check_column_mapping_callback_fix():
    """Check that the column mapping callback passes correct arguments."""
    print("Checking column mapping callback fix...")
    
    column_mapping_path = os.path.join('src', 'gui', 'column_mapping_panel.py')
    
    if not os.path.exists(column_mapping_path):
        print(f"❌ File not found: {column_mapping_path}")
        return False
    
    with open(column_mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the correct callback invocation
    correct_callback_pattern = r'self\.on_mapping_changed\(self\.selected_file1_column,\s*self\.selected_file2_column\)'
    if re.search(correct_callback_pattern, content):
        print("✅ Found correct callback invocation with arguments")
    else:
        print("❌ Correct callback invocation not found")
        return False
    
    # Check that the incorrect callback (without arguments) is not present
    incorrect_callback_pattern = r'self\.on_mapping_changed\(\s*\)'
    if re.search(incorrect_callback_pattern, content):
        print("❌ Found incorrect callback invocation without arguments")
        return False
    else:
        print("✅ No incorrect callback invocation found")
    
    # Check for the callback check
    callback_check_pattern = r'if self\.on_mapping_changed:'
    if re.search(callback_check_pattern, content):
        print("✅ Found callback existence check")
    else:
        print("❌ Callback existence check not found")
        return False
    
    # Check that selected columns are properly set
    column_assignment_pattern = r'self\.selected_file\d_column\s*=.*\.get\(\)'
    matches = re.findall(column_assignment_pattern, content)
    if len(matches) >= 2:
        print("✅ Found column assignment statements")
    else:
        print("❌ Column assignment statements not found or incomplete")
        return False
    
    return True

def check_controller_callback_signature():
    """Check that the controller callback has the correct signature."""
    print("\nChecking controller callback signature...")
    
    controller_path = os.path.join('src', 'controllers', 'main_controller.py')
    
    if not os.path.exists(controller_path):
        print(f"❌ File not found: {controller_path}")
        return False
    
    with open(controller_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the correct method signature
    method_signature_pattern = r'def _handle_mapping_changed\(self,\s*file1_column:\s*str,\s*file2_column:\s*str\)'
    if re.search(method_signature_pattern, content):
        print("✅ Found correct controller method signature")
    else:
        print("❌ Controller method signature not found or incorrect")
        return False
    
    return True

def main():
    """Main verification function."""
    print("Column Mapping Callback Fix Verification")
    print("=" * 45)
    
    success1 = check_column_mapping_callback_fix()
    success2 = check_controller_callback_signature()
    
    overall_success = success1 and success2
    
    print("\n" + "=" * 45)
    if overall_success:
        print("🎉 COLUMN MAPPING CALLBACK FIX VERIFIED!")
        print("The callback now passes correct arguments.")
        print("\nFixed issue:")
        print("- Changed 'self.on_mapping_changed()' to")
        print("  'self.on_mapping_changed(self.selected_file1_column, self.selected_file2_column)'")
        print("- This resolves the TypeError about missing positional arguments")
    else:
        print("❌ COLUMN MAPPING CALLBACK FIX VERIFICATION FAILED!")
        print("Please check the column_mapping_panel.py file.")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())