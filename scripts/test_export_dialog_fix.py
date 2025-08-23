#!/usr/bin/env python3
"""
Quick verification script for the export dialog fix.
Tests that the filedialog parameters are correct.
"""

import sys
import os
import re

def check_results_panel_fix():
    """Check that the results panel uses correct filedialog parameters."""
    print("Checking export dialog fix in results_panel.py...")
    
    results_panel_path = os.path.join('src', 'gui', 'results_panel.py')
    
    if not os.path.exists(results_panel_path):
        print(f"❌ File not found: {results_panel_path}")
        return False
    
    with open(results_panel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the correct parameter
    if 'initialfile=' in content:
        print("✅ Found 'initialfile=' parameter - CORRECT")
    else:
        print("❌ 'initialfile=' parameter not found")
        return False
    
    # Check that the incorrect parameter is not present
    if 'initialname=' in content:
        print("❌ Found 'initialname=' parameter - INCORRECT (should be removed)")
        return False
    else:
        print("✅ 'initialname=' parameter not found - CORRECT")
    
    # Check for the filedialog.asksaveasfilename call
    filedialog_pattern = r'filedialog\.asksaveasfilename\s*\('
    if re.search(filedialog_pattern, content):
        print("✅ Found filedialog.asksaveasfilename() call")
    else:
        print("❌ filedialog.asksaveasfilename() call not found")
        return False
    
    # Extract the filedialog call to verify parameters
    # Find the complete function call
    start_pattern = r'filedialog\.asksaveasfilename\s*\('
    match = re.search(start_pattern, content)
    if match:
        start_pos = match.start()
        # Find the matching closing parenthesis
        paren_count = 0
        pos = start_pos
        while pos < len(content):
            if content[pos] == '(':
                paren_count += 1
            elif content[pos] == ')':
                paren_count -= 1
                if paren_count == 0:
                    break
            pos += 1
        
        if paren_count == 0:
            call_text = content[start_pos:pos+1]
            
            # Check for required parameters
            required_params = ['title=', 'defaultextension=', 'filetypes=', 'initialfile=']
            for param in required_params:
                if param in call_text:
                    print(f"✅ Found required parameter: {param}")
                else:
                    print(f"❌ Missing required parameter: {param}")
                    return False
            
            # Check that initialname is not used
            if 'initialname=' in call_text:
                print("❌ Found 'initialname=' in filedialog call - should be 'initialfile='")
                return False
            else:
                print("✅ No 'initialname=' parameter in filedialog call")
    
    return True

def main():
    """Main verification function."""
    print("Export Dialog Fix Verification")
    print("=" * 40)
    
    success = check_results_panel_fix()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 EXPORT DIALOG FIX VERIFIED!")
        print("The filedialog now uses correct parameters.")
        print("\nFixed issue:")
        print("- Changed 'initialname=' to 'initialfile='")
        print("- This resolves the TclError about bad option")
    else:
        print("❌ EXPORT DIALOG FIX VERIFICATION FAILED!")
        print("Please check the results_panel.py file.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())