#!/usr/bin/env python3
"""
Diagnose tkinter installation and display issues
"""

import sys
import os

def diagnose_tkinter():
    """Diagnose tkinter installation"""
    print("=== Tkinter Diagnostic ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check tkinter import
    try:
        import tkinter as tk
        print("✅ tkinter imported successfully")
    except ImportError as e:
        print(f"❌ tkinter import failed: {e}")
        return False
    
    # Check tkinter version
    try:
        print(f"Tkinter version: {tk.TkVersion}")
        print(f"Tcl version: {tk.TclVersion}")
    except Exception as e:
        print(f"⚠️  Could not get tkinter version: {e}")
    
    # Test basic window creation
    try:
        print("\\nTesting basic window creation...")
        root = tk.Tk()
        print("✅ Root window created")
        
        # Test window properties
        root.title("Diagnostic Test")
        root.geometry("300x200")
        print("✅ Window properties set")
        
        # Test widget creation
        label = tk.Label(root, text="Diagnostic Test")
        label.pack()
        print("✅ Widget created and packed")
        
        # Test window update
        root.update()
        print("✅ Window updated")
        
        # Check if window is mapped
        print(f"Window is mapped: {root.winfo_ismapped()}")
        print(f"Window is viewable: {root.winfo_viewable()}")
        print(f"Window geometry: {root.winfo_geometry()}")
        
        # Destroy window
        root.destroy()
        print("✅ Window destroyed successfully")
        
    except Exception as e:
        print(f"❌ Window creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test mainloop
    try:
        print("\\nTesting mainloop...")
        root = tk.Tk()
        root.title("Mainloop Test")
        root.geometry("300x200")
        
        label = tk.Label(root, text="Mainloop Test\\nThis window should stay open")
        label.pack(expand=True)
        
        # Set a timer to close the window automatically
        def auto_close():
            print("Auto-closing window after 2 seconds...")
            root.quit()
        
        root.after(2000, auto_close)  # Close after 2 seconds
        
        print("Starting mainloop (will auto-close in 2 seconds)...")
        root.mainloop()
        print("✅ Mainloop completed successfully")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Mainloop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\\n=== Diagnostic Summary ===")
    print("✅ All tkinter tests passed")
    print("✅ Your tkinter installation appears to be working correctly")
    print("\\nIf you still can't see GUI windows, the issue might be:")
    print("- Display driver problems")
    print("- Virtual environment or system configuration")
    print("- Windows display scaling or multiple monitor setup")
    print("- Antivirus or security software blocking GUI applications")
    
    return True

if __name__ == "__main__":
    diagnose_tkinter()