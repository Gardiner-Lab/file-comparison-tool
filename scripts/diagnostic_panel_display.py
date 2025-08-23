#!/usr/bin/env python3
"""
Diagnostic Analysis Script for Panel Display Issues

This script tests MainWindow panel display independently and compares it with
the working simplified version to identify the root cause of display issues.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_version():
    """Test the working simple version for reference."""
    print("=" * 60)
    print("TESTING SIMPLE VERSION (WORKING REFERENCE)")
    print("=" * 60)
    
    try:
        from simple_file_tool import SimpleFileComparisonTool
        
        print("✓ Simple version imports successfully")
        
        # Create and test simple version
        app = SimpleFileComparisonTool()
        
        # Check key components
        print(f"✓ Root window created: {app.root}")
        print(f"✓ Content frame created: {app.content_frame}")
        print(f"✓ Content frame geometry manager: {app.content_frame.winfo_manager()}")
        print(f"✓ Content frame pack info: {app.content_frame.pack_info()}")
        
        # Check if content is visible
        app.root.update_idletasks()
        content_children = app.content_frame.winfo_children()
        print(f"✓ Content frame has {len(content_children)} child widgets")
        
        for i, child in enumerate(content_children):
            print(f"  - Child {i}: {child.__class__.__name__} - {child.winfo_manager()}")
            if hasattr(child, 'winfo_viewable'):
                print(f"    Viewable: {child.winfo_viewable()}")
        
        # Don't start mainloop for testing
        app.root.destroy()
        print("✓ Simple version test completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing simple version: {e}")
        import traceback
        traceback.print_exc()

def test_mainwindow_standalone():
    """Test MainWindow class independently."""
    print("\n" + "=" * 60)
    print("TESTING MAINWINDOW STANDALONE")
    print("=" * 60)
    
    try:
        from gui.main_window import MainWindow
        
        print("✓ MainWindow imports successfully")
        
        # Create MainWindow
        main_window = MainWindow()
        
        print(f"✓ MainWindow created: {main_window}")
        print(f"✓ Root window: {main_window.root}")
        print(f"✓ Content frame: {main_window.content_frame}")
        print(f"✓ Content frame geometry manager: {main_window.content_frame.winfo_manager()}")
        print(f"✓ Content frame grid info: {main_window.content_frame.grid_info()}")
        
        # Check grid configuration
        content_frame = main_window.content_frame
        print(f"✓ Content frame grid weights:")
        print(f"  - Row 0 weight: {content_frame.grid_rowconfigure(0)['weight']}")
        print(f"  - Column 0 weight: {content_frame.grid_columnconfigure(0)['weight']}")
        
        # Create a test panel
        test_panel = ttk.Frame(content_frame)
        test_label = ttk.Label(test_panel, text="Test Panel Content", 
                              font=('Arial', 16), anchor="center")
        test_label.pack(expand=True, fill="both")
        
        print("✓ Test panel created")
        
        # Show the test panel
        main_window.show_panel(test_panel)
        print("✓ Test panel shown via show_panel()")
        
        # Force layout update
        main_window.root.update_idletasks()
        
        # Check if panel is visible
        print(f"✓ Test panel grid info: {test_panel.grid_info()}")
        print(f"✓ Test panel viewable: {test_panel.winfo_viewable()}")
        print(f"✓ Test label viewable: {test_label.winfo_viewable()}")
        
        # Check content frame children
        content_children = content_frame.winfo_children()
        print(f"✓ Content frame has {len(content_children)} child widgets")
        
        for i, child in enumerate(content_children):
            print(f"  - Child {i}: {child.__class__.__name__}")
            print(f"    Manager: {child.winfo_manager()}")
            print(f"    Viewable: {child.winfo_viewable()}")
            if child.winfo_manager() == 'grid':
                print(f"    Grid info: {child.grid_info()}")
        
        # Don't start mainloop for testing
        main_window.root.destroy()
        print("✓ MainWindow standalone test completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing MainWindow standalone: {e}")
        import traceback
        traceback.print_exc()

def test_file_selection_panel_standalone():
    """Test FileSelectionPanel independently."""
    print("\n" + "=" * 60)
    print("TESTING FILE SELECTION PANEL STANDALONE")
    print("=" * 60)
    
    try:
        from gui.file_selection_panel import FileSelectionPanel
        
        print("✓ FileSelectionPanel imports successfully")
        
        # Create a test window
        root = tk.Tk()
        root.title("FileSelectionPanel Test")
        root.geometry("800x600")
        
        # Create a parent frame
        parent_frame = ttk.Frame(root)
        parent_frame.pack(fill="both", expand=True, padx=10, pady=10)
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        print("✓ Test window and parent frame created")
        
        # Create FileSelectionPanel
        def on_files_changed(file1, file2):
            print(f"Files changed callback: {file1}, {file2}")
        
        panel = FileSelectionPanel(parent_frame, on_files_changed=on_files_changed)
        
        print("✓ FileSelectionPanel created")
        print(f"✓ Panel widget: {panel.panel}")
        print(f"✓ Panel geometry manager: {panel.panel.winfo_manager()}")
        print(f"✓ Panel grid info: {panel.panel.grid_info()}")
        
        # Force layout update
        root.update_idletasks()
        
        # Check panel visibility
        print(f"✓ Panel viewable: {panel.panel.winfo_viewable()}")
        
        # Check panel children
        panel_children = panel.panel.winfo_children()
        print(f"✓ Panel has {len(panel_children)} child widgets")
        
        for i, child in enumerate(panel_children):
            print(f"  - Child {i}: {child.__class__.__name__}")
            print(f"    Manager: {child.winfo_manager()}")
            print(f"    Viewable: {child.winfo_viewable()}")
            if hasattr(child, 'cget') and 'text' in child.keys():
                try:
                    text = child.cget('text')
                    if text:
                        print(f"    Text: '{text}'")
                except:
                    pass
        
        # Don't start mainloop for testing
        root.destroy()
        print("✓ FileSelectionPanel standalone test completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing FileSelectionPanel standalone: {e}")
        import traceback
        traceback.print_exc()

def test_mainwindow_with_file_selection_panel():
    """Test MainWindow with FileSelectionPanel integration."""
    print("\n" + "=" * 60)
    print("TESTING MAINWINDOW WITH FILE SELECTION PANEL")
    print("=" * 60)
    
    try:
        from gui.main_window import MainWindow
        from gui.file_selection_panel import FileSelectionPanel
        
        print("✓ Both classes import successfully")
        
        # Create MainWindow
        main_window = MainWindow()
        
        # Create FileSelectionPanel
        def on_files_changed(file1, file2):
            print(f"Files changed in integration test: {file1}, {file2}")
        
        file_panel = FileSelectionPanel(
            main_window.content_frame, 
            on_files_changed=on_files_changed
        )
        
        print("✓ FileSelectionPanel created with MainWindow content_frame as parent")
        
        # Show the panel
        main_window.show_panel(file_panel.panel)
        print("✓ Panel shown via MainWindow.show_panel()")
        
        # Force layout update
        main_window.root.update_idletasks()
        
        # Check integration
        print(f"✓ Panel in content_frame: {file_panel.panel.winfo_parent() == str(main_window.content_frame)}")
        print(f"✓ Panel grid info: {file_panel.panel.grid_info()}")
        print(f"✓ Panel viewable: {file_panel.panel.winfo_viewable()}")
        
        # Check current_panel reference
        print(f"✓ MainWindow current_panel: {main_window.current_panel}")
        print(f"✓ Current panel matches file panel: {main_window.current_panel == file_panel.panel}")
        
        # Check content frame state
        content_children = main_window.content_frame.winfo_children()
        print(f"✓ Content frame children count: {len(content_children)}")
        
        visible_children = [child for child in content_children if child.winfo_viewable()]
        print(f"✓ Visible children count: {len(visible_children)}")
        
        # Don't start mainloop for testing
        main_window.root.destroy()
        print("✓ MainWindow + FileSelectionPanel integration test completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing MainWindow + FileSelectionPanel integration: {e}")
        import traceback
        traceback.print_exc()

def compare_layout_configurations():
    """Compare layout configurations between simple and complex versions."""
    print("\n" + "=" * 60)
    print("COMPARING LAYOUT CONFIGURATIONS")
    print("=" * 60)
    
    print("SIMPLE VERSION LAYOUT:")
    print("- Uses pack() geometry manager")
    print("- Content frame: pack(fill='both', expand=True)")
    print("- Direct widget creation and packing")
    print("- Simple hierarchy: root -> main_frame -> content_frame -> widgets")
    
    print("\nCOMPLEX VERSION LAYOUT:")
    print("- Uses grid() geometry manager")
    print("- Content frame: grid(row=1, column=0, sticky='nsew')")
    print("- Panel widgets: grid(row=0, column=0, sticky='nsew')")
    print("- Complex hierarchy: root -> main_frame -> content_frame -> panel -> widgets")
    
    print("\nKEY DIFFERENCES:")
    print("1. Geometry manager: pack() vs grid()")
    print("2. Widget hierarchy depth")
    print("3. Layout configuration complexity")
    print("4. Panel abstraction layer")

def run_visual_test():
    """Run a visual test to see both versions side by side."""
    print("\n" + "=" * 60)
    print("RUNNING VISUAL COMPARISON TEST")
    print("=" * 60)
    
    try:
        # Test simple version visually
        print("Creating simple version window...")
        from simple_file_tool import SimpleFileComparisonTool
        simple_app = SimpleFileComparisonTool()
        simple_app.root.title("Simple Version (Working)")
        simple_app.root.geometry("400x500+100+100")
        
        # Test complex version visually
        print("Creating complex version window...")
        from gui.main_window import MainWindow
        from gui.file_selection_panel import FileSelectionPanel
        
        complex_window = MainWindow()
        complex_window.root.title("Complex Version (Testing)")
        complex_window.root.geometry("400x500+600+100")
        
        # Create and show file selection panel
        def on_files_changed(file1, file2):
            pass
        
        file_panel = FileSelectionPanel(
            complex_window.content_frame,
            on_files_changed=on_files_changed
        )
        complex_window.show_panel(file_panel.panel)
        
        print("✓ Both windows created")
        print("✓ Simple version should show file selection interface")
        print("✓ Complex version should show file selection panel")
        print("\nVisual comparison windows are ready.")
        print("Close both windows to continue with the diagnostic...")
        
        # Run both windows
        def on_simple_close():
            simple_app.root.quit()
            
        def on_complex_close():
            complex_window.root.quit()
            
        simple_app.root.protocol("WM_DELETE_WINDOW", on_simple_close)
        complex_window.root.protocol("WM_DELETE_WINDOW", on_complex_close)
        
        # Start simple version
        simple_app.root.mainloop()
        
        # Start complex version
        complex_window.root.mainloop()
        
        print("✓ Visual comparison completed")
        
    except Exception as e:
        print(f"✗ Error in visual test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all diagnostic tests."""
    print("FILE COMPARISON TOOL - PANEL DISPLAY DIAGNOSTIC")
    print("=" * 60)
    print("This script analyzes the differences between the working simple version")
    print("and the complex MainWindow implementation to identify display issues.")
    print("=" * 60)
    
    # Run all tests
    test_simple_version()
    test_mainwindow_standalone()
    test_file_selection_panel_standalone()
    test_mainwindow_with_file_selection_panel()
    compare_layout_configurations()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("All diagnostic tests completed.")
    print("Check the output above for any ✗ errors or issues.")
    print("Key areas to investigate:")
    print("1. Grid vs Pack geometry manager differences")
    print("2. Widget hierarchy and parent-child relationships")
    print("3. Layout configuration and weights")
    print("4. Panel visibility and viewable state")
    
    # Ask if user wants visual test
    try:
        response = input("\nRun visual comparison test? (y/n): ").lower().strip()
        if response == 'y':
            run_visual_test()
    except KeyboardInterrupt:
        print("\nDiagnostic completed.")

if __name__ == "__main__":
    main()