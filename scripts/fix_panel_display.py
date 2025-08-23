#!/usr/bin/env python3
"""
Fix panel display issue
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def fix_panel_display():
    """Fix the panel display issue"""
    try:
        from gui.main_window import MainWindow
        from controllers.main_controller import MainController
        
        print("Testing panel display fix...")
        
        # Create GUI components
        main_window = MainWindow()
        controller = MainController(main_window)
        main_window.set_controller(controller)
        
        # Force update the layout
        main_window.root.update_idletasks()
        
        # Get the file selection panel
        file_panel = controller.panels.get(controller.current_state)
        
        if file_panel and hasattr(file_panel, 'panel'):
            print("File panel found, forcing display...")
            
            # Force the panel to be visible
            panel_widget = file_panel.panel
            
            # Make sure parent frames are configured
            content_frame = main_window.content_frame
            content_frame.grid_rowconfigure(0, weight=1)
            content_frame.grid_columnconfigure(0, weight=1)
            
            # Re-grid the panel
            panel_widget.grid_forget()  # Remove from grid
            panel_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            
            # Force update
            main_window.root.update_idletasks()
            
            # Check dimensions
            print(f"Panel dimensions after fix: {panel_widget.winfo_width()}x{panel_widget.winfo_height()}")
            print(f"Panel visible after fix: {panel_widget.winfo_viewable()}")
            
            # Test file loading
            print("Testing file loading...")
            file_panel._load_file("test_file1.csv", 1)
            
            # Force UI update
            main_window.root.update_idletasks()
            
            print(f"File 1 path display: '{file_panel.file1_path_var.get()}'")
            print(f"File 1 indicator: '{file_panel.file1_indicator_var.get()}'")
            
        # Show the window
        print("Showing window for 5 seconds...")
        main_window.root.after(5000, main_window.root.quit)
        main_window.root.mainloop()
        
        main_window.root.destroy()
        return True
        
    except Exception as e:
        print(f"Error during panel display fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_panel_display()