"""
Enhanced Progress Dialog for File Comparison Tool.

This module provides a comprehensive progress dialog with cancellation support,
detailed status messages, and performance monitoring capabilities.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Callable, Dict, Any


class ProgressDialog:
    """
    Enhanced progress dialog with cancellation and detailed progress tracking.
    
    Features:
    - Progress bar with percentage display
    - Detailed status messages
    - Cancellation support with cleanup
    - Time estimation and performance metrics
    - Memory usage monitoring
    """
    
    def __init__(self, parent: tk.Tk, title: str = "Processing"):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
        """
        self.parent = parent
        self.title = title
        self.dialog = None
        self.cancelled = False
        self.cancel_callback = None
        self.start_time = None
        
        # Progress tracking
        self.current_progress = 0.0
        self.current_message = ""
        self.estimated_time_remaining = None
        
        # Performance metrics
        self.performance_metrics = {
            'start_time': None,
            'last_update_time': None,
            'progress_history': [],
            'memory_usage': []
        }
        
    def show(self, initial_message: str = "Processing...", 
             allow_cancel: bool = True, 
             cancel_callback: Optional[Callable] = None) -> 'ProgressDialog':
        """
        Show the progress dialog.
        
        Args:
            initial_message: Initial status message
            allow_cancel: Whether to show cancel button
            cancel_callback: Function to call when cancelled
            
        Returns:
            Self for method chaining
        """
        self.cancel_callback = cancel_callback
        self.start_time = time.time()
        self.performance_metrics['start_time'] = self.start_time
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        
        # Center on parent
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create UI components
        self._create_ui(initial_message, allow_cancel)
        
        # Start performance monitoring
        self._start_performance_monitoring()
        
        return self
        
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 450
        dialog_height = 200
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
    def _create_ui(self, initial_message: str, allow_cancel: bool):
        """Create the dialog UI components."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title label
        title_label = ttk.Label(main_frame, text=self.title, 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Status message
        self.status_var = tk.StringVar(value=initial_message)
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                     wraplength=400)
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                          length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 5))
        
        # Progress percentage
        self.percentage_var = tk.StringVar(value="0%")
        self.percentage_label = ttk.Label(main_frame, textvariable=self.percentage_var,
                                         font=('Arial', 9))
        self.percentage_label.pack()
        
        # Time information frame
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill="x", pady=(10, 0))
        
        # Elapsed time
        self.elapsed_var = tk.StringVar(value="Elapsed: 0:00")
        self.elapsed_label = ttk.Label(time_frame, textvariable=self.elapsed_var,
                                      font=('Arial', 8))
        self.elapsed_label.pack(side="left")
        
        # Estimated time remaining
        self.remaining_var = tk.StringVar(value="")
        self.remaining_label = ttk.Label(time_frame, textvariable=self.remaining_var,
                                        font=('Arial', 8))
        self.remaining_label.pack(side="right")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        if allow_cancel:
            self.cancel_button = ttk.Button(button_frame, text="Cancel",
                                           command=self._handle_cancel)
            self.cancel_button.pack(side="right")
        
        # Start time updates
        self._update_time_display()
        
    def _start_performance_monitoring(self):
        """Start monitoring performance metrics."""
        def monitor():
            while self.dialog and not self.cancelled:
                try:
                    # Record memory usage (simplified)
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    
                    self.performance_metrics['memory_usage'].append({
                        'time': time.time(),
                        'memory_mb': memory_mb
                    })
                    
                    # Keep only recent history
                    if len(self.performance_metrics['memory_usage']) > 100:
                        self.performance_metrics['memory_usage'] = \
                            self.performance_metrics['memory_usage'][-50:]
                            
                except ImportError:
                    # psutil not available, skip memory monitoring
                    pass
                except Exception:
                    # Ignore monitoring errors
                    pass
                    
                time.sleep(1)  # Monitor every second
                
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def _update_time_display(self):
        """Update elapsed time and estimated remaining time."""
        if not self.dialog or self.cancelled:
            return
            
        try:
            # Update elapsed time
            if self.start_time:
                elapsed_seconds = time.time() - self.start_time
                elapsed_minutes = int(elapsed_seconds // 60)
                elapsed_secs = int(elapsed_seconds % 60)
                self.elapsed_var.set(f"Elapsed: {elapsed_minutes}:{elapsed_secs:02d}")
                
                # Calculate estimated remaining time
                if self.current_progress > 5:  # Only estimate after 5% progress
                    progress_rate = self.current_progress / elapsed_seconds
                    if progress_rate > 0:
                        remaining_progress = 100 - self.current_progress
                        remaining_seconds = remaining_progress / progress_rate
                        remaining_minutes = int(remaining_seconds // 60)
                        remaining_secs = int(remaining_seconds % 60)
                        self.remaining_var.set(f"Remaining: ~{remaining_minutes}:{remaining_secs:02d}")
                        
            # Schedule next update
            self.dialog.after(1000, self._update_time_display)
            
        except Exception:
            # Ignore time update errors
            pass
            
    def update_progress(self, progress: float, message: str = ""):
        """
        Update progress and status message.
        
        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        if not self.dialog or self.cancelled:
            return
            
        try:
            # Update progress tracking
            self.current_progress = max(0, min(100, progress))
            if message:
                self.current_message = message
                
            # Record progress history for rate calculation
            current_time = time.time()
            self.performance_metrics['progress_history'].append({
                'time': current_time,
                'progress': self.current_progress
            })
            self.performance_metrics['last_update_time'] = current_time
            
            # Keep only recent history
            if len(self.performance_metrics['progress_history']) > 50:
                self.performance_metrics['progress_history'] = \
                    self.performance_metrics['progress_history'][-25:]
            
            # Update UI on main thread
            def update_ui():
                if self.dialog and not self.cancelled:
                    self.progress_var.set(self.current_progress)
                    self.percentage_var.set(f"{self.current_progress:.1f}%")
                    if message:
                        self.status_var.set(message)
                        
            self.dialog.after(0, update_ui)
            
        except Exception:
            # Ignore update errors
            pass
            
    def set_indeterminate(self, message: str = "Processing..."):
        """
        Switch to indeterminate progress mode.
        
        Args:
            message: Status message
        """
        if not self.dialog or self.cancelled:
            return
            
        try:
            def update_ui():
                if self.dialog and not self.cancelled:
                    self.progress_bar.configure(mode='indeterminate')
                    self.progress_bar.start()
                    self.percentage_var.set("")
                    self.status_var.set(message)
                    
            self.dialog.after(0, update_ui)
            
        except Exception:
            pass
            
    def set_determinate(self):
        """Switch back to determinate progress mode."""
        if not self.dialog or self.cancelled:
            return
            
        try:
            def update_ui():
                if self.dialog and not self.cancelled:
                    self.progress_bar.stop()
                    self.progress_bar.configure(mode='determinate')
                    
            self.dialog.after(0, update_ui)
            
        except Exception:
            pass
            
    def _handle_cancel(self):
        """Handle cancel button click."""
        try:
            # Confirm cancellation
            result = tk.messagebox.askyesno(
                "Cancel Operation",
                "Are you sure you want to cancel this operation?",
                parent=self.dialog
            )
            
            if result:
                self.cancelled = True
                self.status_var.set("Cancelling operation...")
                self.cancel_button.configure(state="disabled", text="Cancelling...")
                
                # Call cancel callback if provided
                if self.cancel_callback:
                    # Run callback in separate thread to avoid blocking UI
                    cancel_thread = threading.Thread(
                        target=self.cancel_callback, 
                        daemon=True
                    )
                    cancel_thread.start()
                    
        except Exception:
            # Force close on error
            self.cancelled = True
            
    def is_cancelled(self) -> bool:
        """
        Check if the operation was cancelled.
        
        Returns:
            bool: True if cancelled
        """
        return self.cancelled
        
    def close(self):
        """Close the progress dialog."""
        try:
            if self.dialog:
                self.dialog.grab_release()
                self.dialog.destroy()
                self.dialog = None
                
        except Exception:
            pass
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics collected during operation.
        
        Returns:
            Dict containing performance data
        """
        if self.start_time:
            total_time = time.time() - self.start_time
        else:
            total_time = 0
            
        return {
            'total_time': total_time,
            'final_progress': self.current_progress,
            'progress_history': self.performance_metrics['progress_history'].copy(),
            'memory_usage': self.performance_metrics['memory_usage'].copy(),
            'cancelled': self.cancelled
        }


class BatchProgressDialog(ProgressDialog):
    """
    Extended progress dialog for batch operations with multiple steps.
    
    Provides additional features for operations that have multiple distinct phases.
    """
    
    def __init__(self, parent: tk.Tk, title: str = "Processing", 
                 total_steps: int = 1):
        """
        Initialize batch progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            total_steps: Total number of steps in the operation
        """
        super().__init__(parent, title)
        self.total_steps = total_steps
        self.current_step = 0
        self.step_progress = 0.0
        
    def update_step(self, step: int, step_name: str, step_progress: float = 0.0):
        """
        Update current step information.
        
        Args:
            step: Current step number (0-based)
            step_name: Name of current step
            step_progress: Progress within current step (0-100)
        """
        self.current_step = step
        self.step_progress = step_progress
        
        # Calculate overall progress
        if self.total_steps > 0:
            step_weight = 100.0 / self.total_steps
            overall_progress = (step * step_weight) + (step_progress * step_weight / 100.0)
        else:
            overall_progress = step_progress
            
        message = f"Step {step + 1} of {self.total_steps}: {step_name}"
        self.update_progress(overall_progress, message)
        
    def update_step_progress(self, step_progress: float, detail: str = ""):
        """
        Update progress within current step.
        
        Args:
            step_progress: Progress within current step (0-100)
            detail: Additional detail message
        """
        self.step_progress = step_progress
        
        # Calculate overall progress
        if self.total_steps > 0:
            step_weight = 100.0 / self.total_steps
            overall_progress = (self.current_step * step_weight) + (step_progress * step_weight / 100.0)
        else:
            overall_progress = step_progress
            
        base_message = f"Step {self.current_step + 1} of {self.total_steps}"
        if detail:
            message = f"{base_message}: {detail}"
        else:
            message = base_message
            
        self.update_progress(overall_progress, message)