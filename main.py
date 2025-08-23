#!/usr/bin/env python3
"""
File Comparison Tool - Main Entry Point

This is the main entry point for the File Comparison Tool application.
Run this file to start the GUI application.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Application metadata
__version__ = "1.0.0"
__author__ = "File Comparison Tool Team"
__description__ = "A GUI application for comparing Excel and CSV files with various operations"
__license__ = "MIT"

def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import openpyxl
    except ImportError:
        missing_deps.append("openpyxl")
    
    if missing_deps:
        error_msg = f"Missing required dependencies: {', '.join(missing_deps)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += f"pip install {' '.join(missing_deps)}"
        
        # Show error in GUI if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Missing Dependencies", error_msg)
            root.destroy()
        except:
            print(f"ERROR: {error_msg}")
        
        return False
    
    return True

def main():
    """Main entry point for the application."""
    try:
        # Check dependencies first
        if not check_dependencies():
            sys.exit(1)
        
        # Import GUI components after dependency check
        from gui.main_window import MainWindow
        from controllers.main_controller import MainController
        
        # Create and configure the main application
        main_window = MainWindow()
        controller = MainController(main_window)
        
        # Set controller reference in main window for menu integration
        main_window.set_controller(controller)
        
        # Set initial status
        main_window.set_status("File Comparison Tool ready")
        
        # Force window visibility and proper configuration
        root = main_window.root
        root.lift()
        root.focus_force()
        root.deiconify()
        root.update()
        
        # Use direct mainloop instead of MainWindow.run()
        print(f"Starting File Comparison Tool v{__version__}")
        root.protocol("WM_DELETE_WINDOW", main_window._on_closing)
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"Failed to import required modules: {str(e)}\n\n"
        error_msg += "Please ensure all application files are present and dependencies are installed."
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", error_msg)
            root.destroy()
        except:
            print(f"ERROR: {error_msg}")
        
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}\n\n"
        error_msg += "Please check the console for more details."
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
            root.destroy()
        except:
            pass
        
        print(f"ERROR: {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()