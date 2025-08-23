#!/usr/bin/env python3
"""
Fixed version of main.py using working approach
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the application."""
    try:
        print("Starting File Comparison Tool (Fixed Version)...")
        
        # Import GUI components
        from gui.main_window import MainWindow
        from controllers.main_controller import MainController
        
        # Create main window
        main_window = MainWindow()
        
        # Force window to be visible and properly configured
        root = main_window.root
        root.title("File Comparison Tool - Fixed")
        root.geometry("900x700")
        root.minsize(800, 600)
        
        # Force window to front and ensure it's visible
        root.lift()
        root.focus_force()
        root.deiconify()
        root.update()
        
        # Create controller
        controller = MainController(main_window)
        main_window.set_controller(controller)
        
        # Set initial status
        main_window.set_status("File Comparison Tool ready - Fixed version")
        
        # Override the problematic close handler with a simple one
        def simple_close():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                root.quit()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", simple_close)
        
        print("Application window should now be visible!")
        print("You should see:")
        print("- File Comparison Tool window")
        print("- File selection interface with Browse buttons")
        print("- Step indicators at the top")
        print("- Navigation buttons at the bottom")
        
        # Start the application with direct mainloop
        root.mainloop()
        
        print("Application ended normally")
        
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