#!/usr/bin/env python3
"""
Debug version of main.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the application."""
    try:
        print("=== DEBUG MAIN ===")
        
        # Import GUI components
        print("1. Importing modules...")
        from gui.main_window import MainWindow
        from controllers.main_controller import MainController
        
        # Create and configure the main application
        print("2. Creating MainWindow...")
        main_window = MainWindow()
        print(f"   MainWindow created: {main_window}")
        
        print("3. Creating MainController...")
        controller = MainController(main_window)
        print(f"   Controller created: {controller}")
        
        # Set controller reference in main window for menu integration
        print("4. Setting controller reference...")
        main_window.set_controller(controller)
        
        # Set initial status
        print("5. Setting initial status...")
        main_window.set_status("File Comparison Tool ready - DEBUG MODE")
        
        # Force window to be visible
        print("6. Forcing window visibility...")
        root = main_window.root
        root.lift()
        root.attributes('-topmost', True)
        root.after(3000, lambda: root.attributes('-topmost', False))
        root.focus_force()
        root.deiconify()
        root.update()
        
        print("7. Window should be visible now!")
        print("   Title: File Comparison Tool")
        print("   Status: File Comparison Tool ready - DEBUG MODE")
        print("   You should see the file selection interface")
        
        # Override the closing handler to add debugging
        original_on_closing = main_window._on_closing
        def debug_on_closing():
            print("DEBUG: Window close requested")
            try:
                original_on_closing()
            except Exception as e:
                print(f"DEBUG: Error in close handler: {e}")
                root.quit()
        
        main_window._on_closing = debug_on_closing
        
        # Start the application
        print("8. Starting application mainloop...")
        main_window.run()
        print("9. Application mainloop ended")
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        print(f"ERROR: {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()