"""
Main application window for the File Comparison Tool.

This module contains the MainWindow class which serves as the primary GUI container
with menu bar, status bar, and responsive layout for all application panels.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import os
import sys

from services.help_service import HelpService


class MainWindow:
    """
    Main application window with menu bar, status bar, and panel navigation.
    
    Provides the primary GUI container for the file comparison tool with
    responsive layout and navigation between different workflow steps.
    """
    
    def __init__(self):
        """Initialize the main window with all GUI components."""
        self.root = tk.Tk()
        self.current_panel = None
        self.panels = {}
        
        # Initialize help service
        self.help_service = HelpService()
        
        # Initialize navigation state first
        self.current_step = 0
        self.steps = [
            "File Selection",
            "Column Mapping", 
            "Operation Config",
            "Results"
        ]
        
        # Window configuration
        self._setup_window()
        self._create_menu_bar()
        self._create_main_layout()
        self._create_status_bar()
        self._setup_keyboard_shortcuts()
        self._add_tooltips()
        
    def _setup_window(self):
        """Configure main window properties and styling."""
        # Window title and icon
        self.root.title("File Comparison Tool")
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # Continue without icon if not available
        
        # Window size and positioning
        window_width = 1000
        window_height = 700
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom styles
        self.style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Step.TLabel', font=('Arial', 10))
        self.style.configure('Status.TLabel', font=('Arial', 9))
        
    def _create_menu_bar(self):
        """Create the application menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Comparison", command=self._new_comparison)
        file_menu.add_separator()
        file_menu.add_command(label="Select First File...", command=self._select_first_file, accelerator="Ctrl+1")
        file_menu.add_command(label="Select Second File...", command=self._select_second_file, accelerator="Ctrl+2")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", command=self._clear_all)
        edit_menu.add_command(label="Reset", command=self._reset_workflow)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_user_guide, accelerator="F1")
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_keyboard_shortcuts, accelerator="Ctrl+?")
        help_menu.add_separator()
        help_menu.add_command(label="File Selection Help", command=lambda: self._show_contextual_help('file_selection'))
        help_menu.add_command(label="Column Mapping Help", command=lambda: self._show_contextual_help('column_mapping'))
        help_menu.add_command(label="Operation Config Help", command=lambda: self._show_contextual_help('operation_config'))
        help_menu.add_command(label="Results Help", command=lambda: self._show_contextual_help('results'))
        help_menu.add_separator()
        help_menu.add_command(label="Troubleshooting", command=lambda: self._show_contextual_help('troubleshooting'))
        help_menu.add_command(label="Operation Examples", command=lambda: self._show_contextual_help('operations_detailed'))
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        
    def _create_main_layout(self):
        """Create the main application layout with navigation and content areas."""
        # Main container frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Navigation header
        self._create_navigation_header()
        
        # Content area - configured for proper child widget expansion
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        # Configure content frame grid weights for child widget expansion
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Navigation buttons frame
        self._create_navigation_buttons()
        
        # Help button in navigation
        self._add_help_button()
        
    def _create_navigation_header(self):
        """Create the step navigation header."""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        nav_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(nav_frame, text="File Comparison Tool", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # Step indicator
        self.step_frame = ttk.Frame(nav_frame)
        self.step_frame.grid(row=0, column=1, sticky="e")
        
        self.step_labels = []
        for i, step in enumerate(self.steps):
            # Step number circle
            step_circle = ttk.Label(self.step_frame, text=str(i + 1), 
                                  width=3, anchor="center",
                                  relief="solid", borderwidth=1)
            step_circle.grid(row=0, column=i*2, padx=(5, 2))
            
            # Step name
            step_label = ttk.Label(self.step_frame, text=step, style='Step.TLabel')
            step_label.grid(row=0, column=i*2+1, padx=(2, 10))
            
            self.step_labels.append((step_circle, step_label))
            
            # Arrow between steps (except for last step)
            if i < len(self.steps) - 1:
                arrow_label = ttk.Label(self.step_frame, text="→")
                arrow_label.grid(row=0, column=i*2+2, padx=2)
        
        self._update_step_indicator()
        
    def _create_navigation_buttons(self):
        """Create navigation buttons for moving between steps."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Previous button
        self.prev_button = ttk.Button(button_frame, text="← Previous", 
                                     command=self._previous_step, state="disabled")
        self.prev_button.grid(row=0, column=0, sticky="w")
        
        # Next button
        self.next_button = ttk.Button(button_frame, text="Next →", 
                                     command=self._next_step)
        self.next_button.grid(row=0, column=2, sticky="e")
        
    def _create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        self.status_frame = ttk.Frame(self.root, relief="sunken", borderwidth=1)
        self.status_frame.grid(row=2, column=0, sticky="ew")
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                     style='Status.TLabel')
        self.status_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # Progress indicator (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var,
                                          length=200, mode='determinate')
        
        # Right side status info
        self.info_label = ttk.Label(self.status_frame, text="", style='Status.TLabel')
        self.info_label.grid(row=0, column=2, sticky="e", padx=5, pady=2)
        
    def _update_step_indicator(self):
        """Update the visual step indicator based on current step."""
        for i, (circle, label) in enumerate(self.step_labels):
            if i == self.current_step:
                # Current step - highlighted
                circle.configure(background="#007ACC", foreground="white")
                label.configure(foreground="#007ACC")
            elif i < self.current_step:
                # Completed step - green
                circle.configure(background="#28A745", foreground="white")
                label.configure(foreground="#28A745")
            else:
                # Future step - default
                circle.configure(background="", foreground="")
                label.configure(foreground="")
                
    def show_panel(self, panel_widget):
        """
        Display a panel in the content area.
        
        Args:
            panel_widget: The tkinter widget to display as the main content
        """
        # Hide current panel using grid_remove() instead of destroy
        if self.current_panel:
            self.current_panel.grid_remove()
            
        # Show new panel with proper grid configuration
        self.current_panel = panel_widget
        self.current_panel.grid(row=0, column=0, sticky="nsew")
        
        # Ensure content frame is properly configured for child widget expansion
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Force layout updates with update_idletasks() calls
        self.content_frame.update_idletasks()
        self.root.update_idletasks()
        
    def set_status(self, message: str, info: str = ""):
        """
        Update the status bar message.
        
        Args:
            message: Main status message
            info: Additional info to display on the right side
        """
        self.status_var.set(message)
        self.info_label.configure(text=info)
        self.root.update_idletasks()
        
    def show_progress(self, show: bool = True):
        """
        Show or hide the progress bar.
        
        Args:
            show: Whether to show the progress bar
        """
        if show:
            self.progress_bar.grid(row=0, column=1, sticky="e", padx=10, pady=2)
        else:
            self.progress_bar.grid_remove()
            
    def update_progress(self, value: float):
        """
        Update the progress bar value.
        
        Args:
            value: Progress value between 0 and 100
        """
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def _next_step(self):
        """Navigate to the next step."""
        # Delegate to controller if available
        if hasattr(self, 'controller') and self.controller:
            self.controller._handle_next_step()
        else:
            # Fallback to basic navigation
            if self.current_step < len(self.steps) - 1:
                self.current_step += 1
                self._update_step_indicator()
                self._update_navigation_buttons()
            
    def _previous_step(self):
        """Navigate to the previous step."""
        # Delegate to controller if available
        if hasattr(self, 'controller') and self.controller:
            self.controller._handle_previous_step()
        else:
            # Fallback to basic navigation
            if self.current_step > 0:
                self.current_step -= 1
                self._update_step_indicator()
                self._update_navigation_buttons()
            
    def _update_navigation_buttons(self):
        """Update navigation button states based on current step."""
        # Previous button
        if self.current_step == 0:
            self.prev_button.configure(state="disabled")
        else:
            self.prev_button.configure(state="normal")
            
        # Next button
        if self.current_step == len(self.steps) - 1:
            self.next_button.configure(text="Finish", state="disabled")
        else:
            self.next_button.configure(text="Next →", state="normal")
            
    def _new_comparison(self):
        """Start a new comparison workflow."""
        self.current_step = 0
        self._update_step_indicator()
        self._update_navigation_buttons()
        self.set_status("Ready for new comparison")
        
    def _clear_all(self):
        """Clear all current data and reset the interface."""
        result = messagebox.askyesno("Clear All", 
                                   "This will clear all current data. Continue?")
        if result:
            self._reset_workflow()
            
    def _reset_workflow(self):
        """Reset the workflow to the beginning."""
        self.current_step = 0
        self._update_step_indicator()
        self._update_navigation_buttons()
        self.set_status("Workflow reset")
        
    def _add_help_button(self):
        """Add contextual help button to navigation area."""
        help_button = ttk.Button(self.main_frame, text="? Help", 
                                command=self._show_current_step_help,
                                style="Help.TButton")
        help_button.grid(row=2, column=0, sticky="w", pady=(10, 0))
        
        # Configure help button style
        self.style.configure('Help.TButton', foreground='blue')
        
        # Add tooltip
        self.help_service.add_tooltip(help_button, "Get help for the current step (F1)")
        
    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for the application."""
        # Global shortcuts
        self.root.bind('<F1>', lambda e: self._show_current_step_help())
        self.root.bind('<Control-question>', lambda e: self.help_service.show_keyboard_shortcuts(self.root))
        self.root.bind('<Control-n>', lambda e: self._new_comparison())
        self.root.bind('<Control-r>', lambda e: self._reset_workflow())
        self.root.bind('<F5>', lambda e: self._refresh_current_step())
        
        # Navigation shortcuts
        self.root.bind('<Control-Right>', lambda e: self._next_step())
        self.root.bind('<Control-Left>', lambda e: self._previous_step())
        self.root.bind('<Control-Key-1>', lambda e: self._go_to_step(0))
        self.root.bind('<Control-Key-2>', lambda e: self._go_to_step(1))
        self.root.bind('<Control-Key-3>', lambda e: self._go_to_step(2))
        self.root.bind('<Control-Key-4>', lambda e: self._go_to_step(3))
        
    def _add_tooltips(self):
        """Add tooltips to main window components."""
        # Navigation tooltips
        for i, (circle, label) in enumerate(self.step_labels):
            step_name = self.steps[i]
            tooltip_text = f"Step {i+1}: {step_name}\nClick to jump to this step"
            self.help_service.add_tooltip(circle, tooltip_text)
            self.help_service.add_tooltip(label, tooltip_text)
            
        # Button tooltips
        self.help_service.add_tooltip(self.prev_button, "Go to previous step (Ctrl+Left)")
        self.help_service.add_tooltip(self.next_button, "Go to next step (Ctrl+Right)")
        
    def _show_about(self):
        """Show the about dialog."""
        self.help_service.show_about_dialog(self.root)
        
    def _show_user_guide(self):
        """Show the user guide."""
        self.help_service.open_user_guide()
        
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        self.help_service.show_keyboard_shortcuts(self.root)
        
    def _show_contextual_help(self, topic: str):
        """Show contextual help for a specific topic."""
        self.help_service.show_contextual_help(topic, self.root)
        
    def _show_current_step_help(self):
        """Show help for the current step."""
        step_topics = {
            0: 'file_selection',
            1: 'column_mapping', 
            2: 'operation_config',
            3: 'results'
        }
        
        topic = step_topics.get(self.current_step, 'file_selection')
        self._show_contextual_help(topic)
        
    def _go_to_step(self, step_index: int):
        """Navigate directly to a specific step."""
        if 0 <= step_index < len(self.steps):
            self.current_step = step_index
            self._update_step_indicator()
            self._update_navigation_buttons()
            
    def _refresh_current_step(self):
        """Refresh the current step (placeholder for future functionality)."""
        self.set_status(f"Refreshed {self.steps[self.current_step]} step")
        
    def _select_first_file(self):
        """Handle selecting the first file for comparison."""
        # Delegate to controller if available
        if hasattr(self, 'controller') and self.controller:
            self.controller._trigger_file_selection(1)
        else:
            # Fallback to basic file dialog
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select First File",
                filetypes=[
                    ("Supported files", "*.csv;*.xlsx;*.xls"),
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx;*.xls"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.set_status(f"First file selected: {os.path.basename(filename)}")
            
    def _select_second_file(self):
        """Handle selecting the second file for comparison."""
        # Delegate to controller if available
        if hasattr(self, 'controller') and self.controller:
            self.controller._trigger_file_selection(2)
        else:
            # Fallback to basic file dialog
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select Second File",
                filetypes=[
                    ("Supported files", "*.csv;*.xlsx;*.xls"),
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx;*.xls"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.set_status(f"Second file selected: {os.path.basename(filename)}")
                
    def set_controller(self, controller):
        """Set the controller reference for menu integration."""
        self.controller = controller
        
    def _on_closing(self):
        """Handle window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
            
    def run(self):
        """Start the main application loop."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
        
    def get_root(self):
        """
        Get the root tkinter window.
        
        Returns:
            tk.Tk: The root window instance
        """
        return self.root


if __name__ == "__main__":
    # For testing the main window independently
    app = MainWindow()
    
    # Create a simple test panel
    test_panel = ttk.Frame(app.content_frame)
    test_label = ttk.Label(test_panel, text="Main Window Test", 
                          font=('Arial', 16), anchor="center")
    test_label.pack(expand=True)
    
    app.show_panel(test_panel)
    app.set_status("Testing main window layout")
    
    app.run()