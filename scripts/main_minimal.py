#!/usr/bin/env python3
"""
Minimal version of main.py without controller
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Minimal main entry point."""
    try:
        print("=== MINIMAL MAIN ===")
        
        # Import just the MainWindow
        print("1. Importing MainWindow...")
        from gui.main_window import MainWindow
        
        # Create main window only
        print("2. Creating MainWindow...")
        main_window = MainWindow()
        
        # Add a simple test panel instead of using controller
        print("3. Adding test content...")
        test_panel = ttk.Frame(main_window.content_frame)
        
        title = ttk.Label(test_panel, text="File Comparison Tool - MINIMAL TEST", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        subtitle = ttk.Label(test_panel, text="This is a minimal test without the controller", 
                            font=('Arial', 12))
        subtitle.pack(pady=10)
        
        # File selection simulation
        file_frame = ttk.LabelFrame(test_panel, text="File Selection", padding="10")
        file_frame.pack(fill="x", pady=20, padx=20)
        
        ttk.Label(file_frame, text="First File:").pack(anchor="w")
        ttk.Button(file_frame, text="Browse for First File").pack(fill="x", pady=5)
        
        ttk.Label(file_frame, text="Second File:").pack(anchor="w", pady=(10,0))
        ttk.Button(file_frame, text="Browse for Second File").pack(fill="x", pady=5)
        
        # Show the test panel
        main_window.show_panel(test_panel)
        main_window.set_status("Minimal test - no controller")
        
        print("4. Test content added")
        print("5. Starting application...")
        
        # Force window visibility
        root = main_window.root
        root.lift()
        root.focus_force()
        root.deiconify()
        
        print("   Window should be visible with test content")
        
        # Run the application
        main_window.run()
        print("6. Application ended")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()