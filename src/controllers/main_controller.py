"""
Main controller for the File Comparison Tool.

This module contains the MainController class which coordinates between the GUI
and business logic services, handles all user interactions, manages workflow state,
and provides progress tracking throughout the application.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import logging
import os
from typing import Optional, Dict, Any, Callable
from enum import Enum

from models.data_models import FileInfo, ComparisonConfig, OperationResult
from models.exceptions import (
    FileComparisonError, FileParsingError, InvalidFileFormatError,
    ComparisonOperationError, ExportError, ValidationError
)
# Import services directly to avoid relative import issues
try:
    from services.file_parser_service import FileParserService
except ImportError:
    FileParserService = None
    
try:
    from services.comparison_engine import ComparisonEngine
except ImportError:
    ComparisonEngine = None
    
try:
    from services.export_service import ExportService
except ImportError:
    ExportService = None

try:
    from services.error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None

from gui.main_window import MainWindow
from gui.error_dialogs import ErrorDialog
from gui.progress_dialog import ProgressDialog, BatchProgressDialog


class WorkflowState(Enum):
    """Enumeration of workflow states."""
    FILE_SELECTION = 0
    COLUMN_MAPPING = 1
    OPERATION_CONFIG = 2
    RESULTS = 3


class MainController:
    """
    Main controller coordinating between GUI and services.
    
    Manages the complete workflow from file selection through result export,
    handling all user interactions, validation, and progress tracking.
    """
    
    def __init__(self, main_window=None):
        """Initialize the main controller with all services and GUI components."""
        # Initialize comprehensive error tracking
        self.initialization_errors = []
        self.critical_errors = []
        self.recovery_attempts = {}
        
        # Initialize services with comprehensive error handling
        try:
            self.file_parser = FileParserService() if FileParserService else None
            if not self.file_parser:
                self.initialization_errors.append("FileParserService not available")
        except Exception as e:
            self.initialization_errors.append(f"FileParserService initialization failed: {e}")
            self.file_parser = None
            
        try:
            self.comparison_engine = ComparisonEngine() if ComparisonEngine else None
            if not self.comparison_engine:
                self.initialization_errors.append("ComparisonEngine not available")
        except Exception as e:
            self.initialization_errors.append(f"ComparisonEngine initialization failed: {e}")
            self.comparison_engine = None
            
        try:
            self.export_service = ExportService() if ExportService else None
            if not self.export_service:
                self.initialization_errors.append("ExportService not available")
        except Exception as e:
            self.initialization_errors.append(f"ExportService initialization failed: {e}")
            self.export_service = None
            
        try:
            self.error_handler = ErrorHandler() if ErrorHandler else None
            if not self.error_handler:
                self.initialization_errors.append("ErrorHandler not available - using fallback error handling")
        except Exception as e:
            self.initialization_errors.append(f"ErrorHandler initialization failed: {e}")
            self.error_handler = None
        
        # Progress dialog for long operations
        self.progress_dialog = None
        
        # Progress tracking
        self.current_operation = None
        self.operation_cancelled = False
        
        try:
            # STEP 1: Set workflow state FIRST before any other operations
            # This ensures the correct initial state is established before GUI initialization
            self.current_state = WorkflowState.FILE_SELECTION
            self.workflow_data = {
                'file1_info': None,
                'file2_info': None,
                'file1_data': None,
                'file2_data': None,
                'comparison_config': None,
                'operation_result': None
            }
            
            # GUI panels - initialize empty dictionary before GUI creation
            self.panels = {}
            
            # STEP 2: Initialize GUI after workflow state is set with error handling
            # This ensures the main window is created with proper initial state
            try:
                self.main_window = main_window if main_window else MainWindow()
            except Exception as gui_error:
                self.critical_errors.append(f"Main window initialization failed: {gui_error}")
                raise RuntimeError(f"Cannot initialize main window: {gui_error}")
            
            # Ensure initial workflow state is properly set as per requirements (after main_window is available)
            self._ensure_initial_workflow_state()
            
            # STEP 3: Setup event handlers after GUI is ready but before panel initialization
            try:
                self._setup_event_handlers()
            except Exception as handler_error:
                self.initialization_errors.append(f"Event handler setup failed: {handler_error}")
                # Continue as this might not be critical
            
            # STEP 4: Initialize panels after state, GUI, and handlers are set with comprehensive error handling
            # This ensures proper initialization order: state → GUI → handlers → panels
            try:
                self._initialize_panels()
            except Exception as panel_init_error:
                self.critical_errors.append(f"Panel initialization failed: {panel_init_error}")
                # Try to create fallback panels
                try:
                    self._create_fallback_panels()
                except Exception as fallback_error:
                    self.critical_errors.append(f"Fallback panel creation failed: {fallback_error}")
                    raise RuntimeError("Cannot initialize any panels - application cannot start")
            
            # STEP 5: Validate panels are ready before display with enhanced error handling
            # Add comprehensive validation to prevent premature panel display
            try:
                if not self._validate_panel_initialization():
                    # Create fallback panels if validation fails
                    try:
                        self._create_fallback_panels()
                        # Re-validate after fallback creation
                        if not self._validate_panel_initialization():
                            raise RuntimeError("Panel validation failed even after fallback creation")
                    except Exception as fallback_error:
                        self.critical_errors.append(f"Fallback panel creation during validation failed: {fallback_error}")
                        raise RuntimeError("Panel initialization failed - cannot display interface")
            except Exception as validation_error:
                self.critical_errors.append(f"Panel validation failed: {validation_error}")
                raise RuntimeError(f"Panel validation failed: {validation_error}")
            
            # STEP 6: Display the correct initial panel only after validation with error handling
            # Ensure we start with FILE_SELECTION panel as per requirements
            try:
                self._show_current_panel()
            except Exception as display_error:
                self.critical_errors.append(f"Initial panel display failed: {display_error}")
                # Try recovery by showing minimal interface
                try:
                    self._show_minimal_error_panel(f"Initial panel display failed: {display_error}")
                except Exception as minimal_error:
                    self.critical_errors.append(f"Minimal error panel creation failed: {minimal_error}")
                    raise RuntimeError("Cannot display any interface - application cannot start")
            
            # STEP 7: Update navigation button states correctly on initialization (requirements 2.1, 2.2)
            try:
                self._update_navigation_button_states()
            except Exception as nav_error:
                self.initialization_errors.append(f"Navigation button state update failed: {nav_error}")
                # Continue as this is not critical for basic functionality
                
            # Log initialization summary
            self._log_initialization_summary()
            
        except Exception as init_error:
            self.critical_errors.append(f"Critical initialization error: {init_error}")
            # Try to show error to user if possible
            try:
                if hasattr(self, 'main_window') and self.main_window:
                    messagebox.showerror("Initialization Error", 
                                       f"Application failed to initialize properly:\n{init_error}\n\nSome features may not work correctly.")
                else:
                    print(f"CRITICAL INITIALIZATION ERROR: {init_error}")
            except:
                print(f"CRITICAL INITIALIZATION ERROR: {init_error}")
            raise
        
    def _initialize_panels(self):
        """Initialize all GUI panels with their event handlers in proper order."""
        # Setup logging for panel initialization
        logger = logging.getLogger('FileComparisonTool.MainController')
        logger.info("Starting panel initialization...")
        
        # Track panel readiness state
        self.panel_states = {}
        
        # Ensure content frame is available before creating panels
        if not hasattr(self.main_window, 'content_frame') or not self.main_window.content_frame:
            error_msg = "Main window content frame not available for panel initialization"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info("Content frame validated successfully")
        
        # Initialize panels in dependency order (FILE_SELECTION first as per requirements)
        panel_configs = [
            (WorkflowState.FILE_SELECTION, 'gui.file_selection_panel', 'FileSelectionPanel', self._handle_files_changed),
            (WorkflowState.COLUMN_MAPPING, 'gui.column_mapping_panel', 'ColumnMappingPanel', self._handle_mapping_changed),
            (WorkflowState.OPERATION_CONFIG, 'gui.operation_config_panel', 'OperationConfigPanel', self._handle_config_changed),
            (WorkflowState.RESULTS, 'gui.results_panel', 'ResultsPanel', self._handle_export_request)
        ]
        
        successful_panels = 0
        failed_panels = []
        
        for state, module_name, class_name, callback in panel_configs:
            panel_state = {
                'initialized': False,
                'ready_for_display': False,
                'error_message': None,
                'fallback_created': False
            }
            
            try:
                logger.info(f"Creating panel for {state.name}...")
                
                # Validate module and class names
                if not module_name or not class_name:
                    raise ValueError(f"Invalid module or class name for {state.name}")
                
                # Dynamic import with specific error handling
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    logger.debug(f"Successfully imported module {module_name}")
                except ImportError as import_error:
                    error_msg = f"Failed to import module {module_name}: {import_error}"
                    logger.error(error_msg)
                    panel_state['error_message'] = error_msg
                    failed_panels.append((state, error_msg))
                    self.panel_states[state] = panel_state
                    continue
                
                # Get panel class
                try:
                    panel_class = getattr(module, class_name)
                    logger.debug(f"Successfully retrieved class {class_name}")
                except AttributeError as attr_error:
                    error_msg = f"Class {class_name} not found in module {module_name}: {attr_error}"
                    logger.error(error_msg)
                    panel_state['error_message'] = error_msg
                    failed_panels.append((state, error_msg))
                    self.panel_states[state] = panel_state
                    continue
                
                # Create panel with proper callback and error handling
                panel = None
                try:
                    if callback:
                        if state == WorkflowState.FILE_SELECTION:
                            panel = panel_class(
                                self.main_window.content_frame,
                                on_files_changed=callback
                            )
                        elif state == WorkflowState.COLUMN_MAPPING:
                            panel = panel_class(
                                self.main_window.content_frame,
                                on_mapping_changed=callback
                            )
                        elif state == WorkflowState.OPERATION_CONFIG:
                            panel = panel_class(
                                self.main_window.content_frame,
                                on_config_changed=callback
                            )
                        elif state == WorkflowState.RESULTS:
                            panel = panel_class(
                                self.main_window.content_frame,
                                on_export_complete=callback
                            )
                    else:
                        panel = panel_class(self.main_window.content_frame)
                    
                    logger.debug(f"Panel instance created for {state.name}")
                    
                except Exception as creation_error:
                    error_msg = f"Failed to create panel instance for {state.name}: {creation_error}"
                    logger.error(error_msg)
                    panel_state['error_message'] = error_msg
                    failed_panels.append((state, error_msg))
                    self.panel_states[state] = panel_state
                    continue
                
                # Validate panel structure and readiness
                if not self._validate_panel_structure(panel, state):
                    error_msg = f"Panel structure validation failed for {state.name}"
                    logger.error(error_msg)
                    panel_state['error_message'] = error_msg
                    failed_panels.append((state, error_msg))
                    self.panel_states[state] = panel_state
                    continue
                
                # Store panel and mark as ready
                self.panels[state] = panel
                panel_state['initialized'] = True
                panel_state['ready_for_display'] = True
                successful_panels += 1
                
                logger.info(f"Successfully created and validated panel for {state.name}")
                
            except Exception as e:
                error_msg = f"Unexpected error creating panel for {state.name}: {e}"
                logger.error(error_msg, exc_info=True)
                panel_state['error_message'] = error_msg
                failed_panels.append((state, error_msg))
            
            finally:
                self.panel_states[state] = panel_state
        
        # Log summary of panel initialization
        logger.info(f"Panel initialization complete. Successfully created {successful_panels}/{len(panel_configs)} panels")
        
        if failed_panels:
            logger.warning(f"Failed to create {len(failed_panels)} panels:")
            for state, error in failed_panels:
                logger.warning(f"  - {state.name}: {error}")
        
        # Ensure at least the FILE_SELECTION panel is available (critical requirement)
        if WorkflowState.FILE_SELECTION not in self.panels or not self.panel_states[WorkflowState.FILE_SELECTION]['ready_for_display']:
            logger.critical("FILE_SELECTION panel failed to initialize - this is a critical error")
            
    def _validate_panel_structure(self, panel, state: WorkflowState) -> bool:
        """
        Validate that a panel has the expected structure and is ready for display.
        
        Args:
            panel: The panel instance to validate
            state: The workflow state this panel represents
            
        Returns:
            bool: True if panel structure is valid, False otherwise
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Check panel is not None
            if not panel:
                logger.error(f"Panel for {state.name} is None")
                return False
            
            # Check panel has required widget structure
            panel_widget = getattr(panel, 'panel', panel)
            if not panel_widget:
                logger.error(f"Panel widget for {state.name} is invalid or missing")
                return False
            
            # Validate panel widget is a tkinter widget
            if not hasattr(panel_widget, 'grid'):
                logger.error(f"Panel widget for {state.name} is not a valid tkinter widget (missing grid method)")
                return False
            
            # Check for common panel methods (optional but recommended)
            expected_methods = ['reset']
            missing_methods = []
            for method in expected_methods:
                if not hasattr(panel, method):
                    missing_methods.append(method)
            
            if missing_methods:
                logger.warning(f"Panel for {state.name} is missing recommended methods: {missing_methods}")
            
            # Validate panel can be properly configured for grid layout
            try:
                # Test that the panel widget can be configured (without actually showing it)
                panel_widget.grid_configure()
                logger.debug(f"Panel widget for {state.name} passed grid configuration test")
            except Exception as grid_error:
                logger.error(f"Panel widget for {state.name} failed grid configuration test: {grid_error}")
                return False
            
            logger.debug(f"Panel structure validation passed for {state.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error during panel structure validation for {state.name}: {e}")
            return False
        
    def _validate_panel_initialization(self) -> bool:
        """
        Validate that panels are properly initialized before display.
        
        Returns:
            bool: True if panels are ready for display, False otherwise
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Starting panel initialization validation...")
            
            # Ensure main window and content frame are ready first
            if not hasattr(self.main_window, 'content_frame') or not self.main_window.content_frame:
                error_msg = "Main window content frame not available"
                logger.error(error_msg)
                return False
            
            logger.debug("Main window content frame validation passed")
            
            # Check panel states if available
            if hasattr(self, 'panel_states'):
                logger.debug("Using panel state tracking for validation")
                
                # Check that all required workflow states have ready panels
                missing_panels = []
                failed_panels = []
                
                for state in WorkflowState:
                    panel_state = self.panel_states.get(state, {})
                    
                    # Check if panel exists in panels dictionary
                    if state not in self.panels:
                        missing_panels.append(state.name)
                        logger.error(f"Missing panel for workflow state {state.name}")
                        continue
                    
                    # Check panel state readiness
                    if not panel_state.get('ready_for_display', False):
                        failed_panels.append((state.name, panel_state.get('error_message', 'Unknown error')))
                        logger.error(f"Panel for {state.name} not ready for display: {panel_state.get('error_message', 'Unknown error')}")
                        continue
                    
                    # Validate panel object exists and is valid
                    panel = self.panels[state]
                    if not panel:
                        failed_panels.append((state.name, "Panel object is None"))
                        logger.error(f"Panel object for state {state.name} is None")
                        continue
                    
                    logger.debug(f"Panel validation passed for {state.name}")
                
                # Report validation results
                if missing_panels:
                    logger.error(f"Missing panels: {', '.join(missing_panels)}")
                
                if failed_panels:
                    logger.error("Failed panel validations:")
                    for panel_name, error in failed_panels:
                        logger.error(f"  - {panel_name}: {error}")
                
                # Check if critical panels are available
                critical_panels = [WorkflowState.FILE_SELECTION]
                critical_missing = [state for state in critical_panels if state not in self.panels or not self.panel_states.get(state, {}).get('ready_for_display', False)]
                
                if critical_missing:
                    logger.critical(f"Critical panels missing or not ready: {[state.name for state in critical_missing]}")
                    return False
                
                # If we have at least the critical panels, we can proceed
                if missing_panels or failed_panels:
                    logger.warning("Some panels failed validation but critical panels are available")
                    return True  # Allow partial success if critical panels work
                
            else:
                # Fallback to original validation logic if panel states not available
                logger.warning("Panel state tracking not available, using fallback validation")
                
                # Check that all required workflow states have panels
                for state in WorkflowState:
                    if state not in self.panels:
                        logger.error(f"Missing panel for workflow state {state.name}")
                        return False
                        
                    # Validate each panel has proper structure
                    panel = self.panels[state]
                    if not panel:
                        logger.error(f"Panel for state {state.name} is None")
                        return False
                        
                    # Check that the panel has the expected widget structure
                    panel_widget = getattr(panel, 'panel', panel)
                    if not panel_widget:
                        logger.error(f"Panel widget for state {state.name} is invalid")
                        return False
                        
                    # Validate panel widget is a tkinter widget
                    if not hasattr(panel_widget, 'grid'):
                        logger.error(f"Panel widget for state {state.name} is not a valid tkinter widget")
                        return False
            
            # Validate that the initial state panel exists and is accessible
            initial_panel = self.panels.get(self.current_state)
            if not initial_panel:
                logger.error(f"Initial panel for state {self.current_state.name} not found")
                return False
            
            # Ensure current state is set to FILE_SELECTION as per requirements
            if self.current_state != WorkflowState.FILE_SELECTION:
                logger.warning(f"Current state is {self.current_state.name}, resetting to FILE_SELECTION as per requirements")
                self.current_state = WorkflowState.FILE_SELECTION
            
            logger.info("Panel initialization validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during panel validation: {e}", exc_info=True)
            return False
            
    def _create_fallback_panels(self):
        """
        Create fallback placeholder panels for any missing panels.
        This ensures the application can still function even if panel imports fail.
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Creating fallback panels for missing or failed panels...")
            
            fallback_count = 0
            
            # Create simple placeholder panels for any missing workflow states
            for state in WorkflowState:
                needs_fallback = False
                
                # Check if panel is missing or failed
                if state not in self.panels or not self.panels[state]:
                    needs_fallback = True
                    logger.warning(f"Panel missing for {state.name}, creating fallback")
                elif hasattr(self, 'panel_states') and not self.panel_states.get(state, {}).get('ready_for_display', False):
                    needs_fallback = True
                    error_msg = self.panel_states.get(state, {}).get('error_message', 'Unknown error')
                    logger.warning(f"Panel failed for {state.name} ({error_msg}), creating fallback")
                
                if needs_fallback:
                    try:
                        logger.info(f"Creating fallback panel for {state.name}")
                        
                        # Create a functional placeholder panel with better styling
                        placeholder_frame = tk.Frame(
                            self.main_window.content_frame, 
                            bg='#f8f9fa',
                            relief='solid',
                            borderwidth=1
                        )
                        
                        # Add padding container
                        content_frame = tk.Frame(placeholder_frame, bg='#f8f9fa')
                        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
                        
                        # Add icon or indicator
                        icon_label = tk.Label(
                            content_frame,
                            text="⚠️",
                            font=('Arial', 24),
                            bg='#f8f9fa',
                            fg='#ffc107'
                        )
                        icon_label.pack(pady=(0, 10))
                        
                        # Add title
                        title_label = tk.Label(
                            content_frame, 
                            text=f"{state.name.replace('_', ' ').title()} Panel",
                            font=('Arial', 16, 'bold'),
                            bg='#f8f9fa',
                            fg='#212529'
                        )
                        title_label.pack(pady=(0, 10))
                        
                        # Add status message
                        status_text = "This panel is temporarily unavailable."
                        if hasattr(self, 'panel_states') and state in self.panel_states:
                            error_msg = self.panel_states[state].get('error_message')
                            if error_msg:
                                status_text += f"\n\nError: {error_msg}"
                        
                        status_text += "\n\nPlease check the application logs for more details."
                        
                        status_label = tk.Label(
                            content_frame,
                            text=status_text,
                            font=('Arial', 10),
                            bg='#f8f9fa',
                            fg='#6c757d',
                            justify='center',
                            wraplength=400
                        )
                        status_label.pack(pady=(0, 20))
                        
                        # Add basic functionality for critical panels
                        if state == WorkflowState.FILE_SELECTION:
                            # Add basic file selection functionality
                            button_frame = tk.Frame(content_frame, bg='#f8f9fa')
                            button_frame.pack()
                            
                            def select_file1():
                                messagebox.showinfo("Fallback Mode", "File selection is in fallback mode. Please restart the application.")
                            
                            def select_file2():
                                messagebox.showinfo("Fallback Mode", "File selection is in fallback mode. Please restart the application.")
                            
                            tk.Button(
                                button_frame,
                                text="Select File 1 (Fallback)",
                                command=select_file1,
                                state='disabled'
                            ).pack(side='left', padx=5)
                            
                            tk.Button(
                                button_frame,
                                text="Select File 2 (Fallback)",
                                command=select_file2,
                                state='disabled'
                            ).pack(side='left', padx=5)
                        
                        # Create a panel object with the required structure and enhanced methods
                        class FallbackPanel:
                            def __init__(self, frame):
                                self.panel = frame
                                self.is_fallback = True
                            
                            def reset(self):
                                """Reset method for compatibility"""
                                logger.debug(f"Reset called on fallback panel for {state.name}")
                            
                            def get_selected_columns(self):
                                """Fallback method for column mapping panels"""
                                return None, None
                            
                            def get_operation_config(self):
                                """Fallback method for operation config panels"""
                                return {}
                            
                            def set_file_info(self, file1_info, file2_info):
                                """Fallback method for panels that need file info"""
                                pass
                        
                        panel_obj = FallbackPanel(placeholder_frame)
                        self.panels[state] = panel_obj
                        
                        # Update panel state
                        if hasattr(self, 'panel_states'):
                            self.panel_states[state] = {
                                'initialized': True,
                                'ready_for_display': True,
                                'error_message': self.panel_states.get(state, {}).get('error_message'),
                                'fallback_created': True
                            }
                        
                        fallback_count += 1
                        logger.info(f"Successfully created fallback panel for {state.name}")
                        
                    except Exception as fallback_error:
                        logger.error(f"Failed to create fallback panel for {state.name}: {fallback_error}")
                        
                        # Create absolute minimal panel as last resort
                        try:
                            minimal_frame = tk.Frame(self.main_window.content_frame, bg='white')
                            minimal_label = tk.Label(
                                minimal_frame, 
                                text=f"Minimal {state.name.replace('_', ' ')} Panel\n(Error in fallback creation)",
                                font=('Arial', 12),
                                bg='white',
                                justify='center'
                            )
                            minimal_label.pack(expand=True)
                            
                            class MinimalPanel:
                                def __init__(self, frame):
                                    self.panel = frame
                                    self.is_minimal = True
                                
                                def reset(self):
                                    pass
                            
                            self.panels[state] = MinimalPanel(minimal_frame)
                            logger.warning(f"Created minimal panel for {state.name} as last resort")
                            
                        except Exception as minimal_error:
                            logger.critical(f"Failed to create even minimal panel for {state.name}: {minimal_error}")
            
            if fallback_count > 0:
                logger.info(f"Successfully created {fallback_count} fallback panels")
            else:
                logger.info("No fallback panels needed - all panels initialized successfully")
                
        except Exception as e:
            logger.error(f"Error in fallback panel creation process: {e}", exc_info=True)
            
            # Emergency fallback - create minimal panels for any still missing
            try:
                for state in WorkflowState:
                    if state not in self.panels:
                        emergency_frame = tk.Frame(self.main_window.content_frame)
                        emergency_label = tk.Label(emergency_frame, text=f"Emergency {state.name}")
                        emergency_label.pack()
                        
                        class EmergencyPanel:
                            def __init__(self, frame):
                                self.panel = frame
                            def reset(self):
                                pass
                        
                        self.panels[state] = EmergencyPanel(emergency_frame)
                        logger.warning(f"Created emergency panel for {state.name}")
                        
            except Exception as emergency_error:
                logger.critical(f"Emergency panel creation failed: {emergency_error}")
        
    def _setup_event_handlers(self):
        """Setup event handlers for main window navigation."""
        # Override main window navigation methods
        self.main_window._next_step = self._handle_next_step
        self.main_window._previous_step = self._handle_previous_step
        self.main_window._new_comparison = self._handle_new_comparison
        self.main_window._reset_workflow = self._handle_reset_workflow
        
    def _show_current_panel(self):
        """Display the panel corresponding to the current workflow state with validation."""
        try:
            print(f"Attempting to show panel for state: {self.current_state.name}")
            
            # Validate that we're not trying to display before initialization is complete
            if not self.panels:
                print("Error: Panels not initialized yet - cannot display panel")
                return
                
            # Ensure we start with FILE_SELECTION as per requirements 1.1 and 1.2
            if self.current_state != WorkflowState.FILE_SELECTION:
                print(f"Warning: Current state is {self.current_state.name}, resetting to FILE_SELECTION as per requirements")
                self.current_state = WorkflowState.FILE_SELECTION
            
            # Validate that the current state has a corresponding panel
            if self.current_state not in self.panels:
                print(f"Error: No panel found for workflow state {self.current_state.name}")
                return
                
            current_panel = self.panels[self.current_state]
            if not current_panel:
                print(f"Error: Panel for state {self.current_state.name} is None")
                return
                
            # Get the panel widget with proper validation
            panel_widget = getattr(current_panel, 'panel', current_panel)
            if not panel_widget:
                print(f"Error: Panel widget for state {self.current_state.name} is invalid")
                return
                
            # Validate panel widget is a proper tkinter widget
            if not hasattr(panel_widget, 'grid'):
                print(f"Error: Panel widget for state {self.current_state.name} is not a valid tkinter widget")
                return
            
            # Validate main window is ready before showing panel
            if not hasattr(self.main_window, 'show_panel'):
                print("Error: Main window show_panel method not available")
                return
                
            if not hasattr(self.main_window, 'content_frame') or not self.main_window.content_frame:
                print("Error: Main window content frame not available")
                return
            
            # Display the panel
            print(f"Displaying panel for {self.current_state.name}")
            self.main_window.show_panel(panel_widget)
            
            # Update main window step indicator (ensure current_step matches current_state)
            self.main_window.current_step = self.current_state.value
            
            # Update navigation button states using enhanced method
            self._update_navigation_button_states()
            
            # Update status based on current state as per requirements
            status_messages = {
                WorkflowState.FILE_SELECTION: "Select two files to compare",
                WorkflowState.COLUMN_MAPPING: "Choose columns to compare between files",
                WorkflowState.OPERATION_CONFIG: "Configure comparison operation",
                WorkflowState.RESULTS: "View and export comparison results"
            }
            
            if hasattr(self.main_window, 'set_status'):
                self.main_window.set_status(status_messages[self.current_state])
            
            print(f"Successfully displayed panel for {self.current_state.name}")
            
        except Exception as e:
            print(f"Error displaying panel for state {self.current_state.name}: {e}")
            
            # Attempt recovery by ensuring we're in the correct initial state
            if self.current_state != WorkflowState.FILE_SELECTION:
                print("Attempting to recover by resetting to FILE_SELECTION state")
                self.current_state = WorkflowState.FILE_SELECTION
                
            # Try to show the file selection panel if it exists
            if WorkflowState.FILE_SELECTION in self.panels:
                try:
                    panel = self.panels[WorkflowState.FILE_SELECTION]
                    panel_widget = getattr(panel, 'panel', panel)
                    if hasattr(self.main_window, 'show_panel') and panel_widget:
                        self.main_window.show_panel(panel_widget)
                        print("Recovery successful - showing FILE_SELECTION panel")
                    else:
                        print("Recovery failed - main window or panel widget not available")
                except Exception as recovery_error:
                    print(f"Recovery attempt failed: {recovery_error}")
            else:
                print("Recovery failed - FILE_SELECTION panel not available")
        
    def _handle_next_step(self):
        """Handle navigation to the next workflow step."""
        try:
            # Validate current step before proceeding
            if not self._validate_current_step():
                return
                
            # Validate workflow state transition before proceeding
            if not self._validate_workflow_transition(forward=True):
                return
                
            # Move to next state if not at the end
            if self.current_state.value < len(WorkflowState) - 1:
                next_state = WorkflowState(self.current_state.value + 1)
                
                # Special handling for transitions
                if self.current_state == WorkflowState.COLUMN_MAPPING:
                    self._prepare_operation_config()
                elif self.current_state == WorkflowState.OPERATION_CONFIG:
                    self._execute_comparison()
                    
                # Update workflow state with validation
                self._update_workflow_state(next_state)
                
        except Exception as e:
            self._handle_error(e, "Error navigating to next step")
            
    def _handle_previous_step(self):
        """Handle navigation to the previous workflow step."""
        try:
            # Validate workflow state transition before proceeding
            if not self._validate_workflow_transition(forward=False):
                return
                
            # Move to previous state if not at the beginning
            if self.current_state.value > 0:
                prev_state = WorkflowState(self.current_state.value - 1)
                
                # Update workflow state with validation
                self._update_workflow_state(prev_state)
                
        except Exception as e:
            self._handle_error(e, "Error navigating to previous step")
            
    def _handle_new_comparison(self):
        """Handle starting a new comparison workflow."""
        try:
            # Perform proper workflow reset
            self._reset_workflow_state()
            
        except Exception as e:
            self._handle_error(e, "Error starting new comparison")
            
    def _handle_reset_workflow(self):
        """Handle resetting the current workflow."""
        try:
            result = messagebox.askyesno(
                "Reset Workflow", 
                "This will reset all current progress. Continue?"
            )
            if result:
                self._handle_new_comparison()
                
        except Exception as e:
            self._handle_error(e, "Error resetting workflow")
            
    def _validate_current_step(self) -> bool:
        """
        Validate the current step before allowing navigation.
        
        Returns:
            bool: True if current step is valid, False otherwise
        """
        try:
            if self.current_state == WorkflowState.FILE_SELECTION:
                return self._validate_file_selection()
            elif self.current_state == WorkflowState.COLUMN_MAPPING:
                return self._validate_column_mapping()
            elif self.current_state == WorkflowState.OPERATION_CONFIG:
                return self._validate_operation_config()
            elif self.current_state == WorkflowState.RESULTS:
                return True  # Results step is always valid
                
            return False
            
        except Exception as e:
            self._handle_error(e, "Error validating current step")
            return False
            
    def _validate_file_selection(self) -> bool:
        """Validate that both files are selected and valid."""
        if not self.workflow_data['file1_info'] or not self.workflow_data['file2_info']:
            messagebox.showerror("Validation Error", "Please select both files before proceeding.")
            return False
            
        return True
        
    def _validate_column_mapping(self) -> bool:
        """Validate that columns are selected and compatible."""
        panel = self.panels.get(WorkflowState.COLUMN_MAPPING)
        
        if not panel or not hasattr(panel, 'get_selected_columns'):
            return True  # Skip validation if panel not available
            
        file1_col, file2_col = panel.get_selected_columns()
        
        if not file1_col or not file2_col:
            messagebox.showerror("Validation Error", "Please select columns from both files.")
            return False
            
        return True
        
    def _validate_operation_config(self) -> bool:
        """Validate that operation is configured properly."""
        panel = self.panels.get(WorkflowState.OPERATION_CONFIG)
        
        if not panel or not hasattr(panel, 'get_operation_config'):
            return True  # Skip validation if panel not available
            
        config = panel.get_operation_config()
        
        if not config or not config.get('operation'):
            messagebox.showerror("Validation Error", "Please select a comparison operation.")
            return False
            
        return True
        
    def _validate_workflow_transition(self, forward: bool = True) -> bool:
        """
        Validate that a workflow state transition is allowed.
        
        Args:
            forward: True for forward transition, False for backward
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            current_value = self.current_state.value
            
            if forward:
                # Validate forward transition
                if current_value >= len(WorkflowState) - 1:
                    logger.warning("Cannot move forward from final workflow state")
                    return False
                    
                # Additional validation for specific transitions
                if self.current_state == WorkflowState.FILE_SELECTION:
                    if not self._validate_file_selection():
                        logger.info("File selection validation failed - cannot proceed")
                        return False
                        
                elif self.current_state == WorkflowState.COLUMN_MAPPING:
                    if not self._validate_column_mapping():
                        logger.info("Column mapping validation failed - cannot proceed")
                        return False
                        
                elif self.current_state == WorkflowState.OPERATION_CONFIG:
                    if not self._validate_operation_config():
                        logger.info("Operation config validation failed - cannot proceed")
                        return False
                        
            else:
                # Validate backward transition
                if current_value <= 0:
                    logger.warning("Cannot move backward from initial workflow state")
                    return False
                    
            logger.debug(f"Workflow transition validation passed for {self.current_state.name} ({'forward' if forward else 'backward'})")
            return True
            
        except Exception as e:
            logger.error(f"Error validating workflow transition: {e}")
            return False
            
    def _update_workflow_state(self, new_state: WorkflowState):
        """
        Update the workflow state with proper validation and UI updates.
        
        Args:
            new_state: The new workflow state to transition to
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Validate new state is valid
            if not isinstance(new_state, WorkflowState):
                raise ValueError(f"Invalid workflow state: {new_state}")
                
            # Log state transition
            logger.info(f"Transitioning workflow state from {self.current_state.name} to {new_state.name}")
            
            # Update current state
            old_state = self.current_state
            self.current_state = new_state
            
            # Update main window step indicator
            if hasattr(self.main_window, 'current_step'):
                self.main_window.current_step = new_state.value
                
            # Show the new panel
            self._show_current_panel()
            
            # Update navigation button states correctly on state change
            self._update_navigation_button_states()
            
            logger.debug(f"Workflow state successfully updated to {new_state.name}")
            
        except Exception as e:
            logger.error(f"Error updating workflow state to {new_state}: {e}")
            # Revert to previous state on error
            self.current_state = old_state if 'old_state' in locals() else WorkflowState.FILE_SELECTION
            raise
            
    def _reset_workflow_state(self):
        """
        Implement proper state reset functionality as per requirements.
        Ensures initial workflow state is set to FILE_SELECTION.
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Resetting workflow state to initial state")
            
            # Reset workflow data
            self.workflow_data = {
                'file1_info': None,
                'file2_info': None,
                'file1_data': None,
                'file2_data': None,
                'comparison_config': None,
                'operation_result': None
            }
            
            # Ensure initial workflow state is set to FILE_SELECTION as per requirements
            self.current_state = WorkflowState.FILE_SELECTION
            
            # Update main window step indicator
            if hasattr(self.main_window, 'current_step'):
                self.main_window.current_step = 0  # FILE_SELECTION is step 0
                
            # Reset all panels
            for state, panel in self.panels.items():
                try:
                    # Try reset_component first (standard interface method), then reset (fallback)
                    if hasattr(panel, 'reset_component'):
                        panel.reset_component()
                        logger.debug(f"Reset panel for {state.name} using reset_component")
                    elif hasattr(panel, 'reset'):
                        panel.reset()
                        logger.debug(f"Reset panel for {state.name} using reset")
                except Exception as panel_error:
                    logger.warning(f"Error resetting panel for {state.name}: {panel_error}")
                    
            # Show the file selection panel
            self._show_current_panel()
            
            # Update navigation button states correctly on initialization
            self._update_navigation_button_states()
            
            # Update status
            self.main_window.set_status("Ready for new comparison")
            
            logger.info("Workflow state reset completed successfully")
            
        except Exception as e:
            logger.error(f"Error resetting workflow state: {e}")
            # Ensure we're at least in a valid state
            self.current_state = WorkflowState.FILE_SELECTION
            if hasattr(self.main_window, 'current_step'):
                self.main_window.current_step = 0
            raise
            
    def _update_navigation_button_states(self):
        """
        Update navigation button states correctly based on current workflow state.
        Ensures proper button states as per requirements 2.1 and 2.2.
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Update step indicator if method exists
            if hasattr(self.main_window, '_update_step_indicator'):
                self.main_window._update_step_indicator()
                logger.debug("Step indicator updated")
                
            # Update navigation buttons if method exists
            if hasattr(self.main_window, '_update_navigation_buttons'):
                self.main_window._update_navigation_buttons()
                logger.debug("Navigation buttons updated")
                
            # Additional validation for initial state as per requirements
            if self.current_state == WorkflowState.FILE_SELECTION:
                # Ensure "Previous" button is disabled at start (requirement 2.1)
                if hasattr(self.main_window, 'prev_button'):
                    self.main_window.prev_button.configure(state="disabled")
                    
                # Ensure "Next" button shows correct text and state (requirement 2.2)
                if hasattr(self.main_window, 'next_button'):
                    self.main_window.next_button.configure(text="Next →", state="normal")
                    
                logger.debug("Initial navigation button states set correctly")
                
        except Exception as e:
            logger.error(f"Error updating navigation button states: {e}")
            
    def _log_initialization_summary(self):
        """Log a summary of initialization results and any errors encountered."""
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Log initialization status
            if not self.initialization_errors and not self.critical_errors:
                logger.info("MainController initialization completed successfully")
            else:
                logger.warning("MainController initialization completed with issues")
                
            # Log initialization errors
            if self.initialization_errors:
                logger.warning(f"Initialization warnings ({len(self.initialization_errors)}):")
                for i, error in enumerate(self.initialization_errors, 1):
                    logger.warning(f"  {i}. {error}")
                    
            # Log critical errors
            if self.critical_errors:
                logger.error(f"Critical initialization errors ({len(self.critical_errors)}):")
                for i, error in enumerate(self.critical_errors, 1):
                    logger.error(f"  {i}. {error}")
                    
            # Log service availability
            services = {
                'FileParserService': self.file_parser is not None,
                'ComparisonEngine': self.comparison_engine is not None,
                'ExportService': self.export_service is not None,
                'ErrorHandler': self.error_handler is not None
            }
            
            available_services = [name for name, available in services.items() if available]
            unavailable_services = [name for name, available in services.items() if not available]
            
            logger.info(f"Available services: {', '.join(available_services) if available_services else 'None'}")
            if unavailable_services:
                logger.warning(f"Unavailable services: {', '.join(unavailable_services)}")
                
            # Log panel status
            if hasattr(self, 'panels') and self.panels:
                panel_count = len(self.panels)
                logger.info(f"Initialized {panel_count} panels: {', '.join([state.name for state in self.panels.keys()])}")
                
                if hasattr(self, 'panel_states'):
                    fallback_panels = [state.name for state, info in self.panel_states.items() 
                                     if info.get('fallback_created', False)]
                    if fallback_panels:
                        logger.warning(f"Fallback panels created: {', '.join(fallback_panels)}")
            else:
                logger.error("No panels initialized")
                
        except Exception as e:
            logger.error(f"Error logging initialization summary: {e}")

    def _ensure_initial_workflow_state(self):
        """
        Ensure initial workflow state is set to FILE_SELECTION as per requirement 1.1.
        This method is called during initialization to guarantee proper initial state.
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Ensure initial workflow state is set to FILE_SELECTION (requirement 1.1)
            if not hasattr(self, 'current_state') or self.current_state != WorkflowState.FILE_SELECTION:
                logger.info("Setting initial workflow state to FILE_SELECTION")
                self.current_state = WorkflowState.FILE_SELECTION
                
            # Ensure main window step is synchronized
            if hasattr(self.main_window, 'current_step'):
                if self.main_window.current_step != 0:
                    logger.info("Synchronizing main window step with workflow state")
                    self.main_window.current_step = 0
                    
            logger.debug("Initial workflow state validation completed")
            
        except Exception as e:
            logger.error(f"Error ensuring initial workflow state: {e}")
            self.initialization_errors.append(f"Workflow state initialization failed: {e}")
            # Force to FILE_SELECTION as fallback
            try:
                self.current_state = WorkflowState.FILE_SELECTION
                if hasattr(self.main_window, 'current_step'):
                    self.main_window.current_step = 0
                logger.info("Fallback workflow state set successfully")
            except Exception as fallback_error:
                self.critical_errors.append(f"Fallback workflow state setting failed: {fallback_error}")
                raise RuntimeError(f"Cannot set initial workflow state: {fallback_error}")
        
    def _prepare_operation_config(self):
        """Prepare the operation config panel with current data."""
        try:
            panel = self.panels.get(WorkflowState.OPERATION_CONFIG)
            
            if panel and hasattr(panel, 'set_file_info'):
                panel.set_file_info(
                    self.workflow_data['file1_info'],
                    self.workflow_data['file2_info']
                )
                
        except Exception as e:
            self._handle_error(e, "Error preparing operation configuration")
            
    def _execute_comparison(self):
        """Execute the comparison operation in a separate thread with comprehensive error handling."""
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Starting comparison execution process")
            
            # Validate comparison engine availability
            if not self.comparison_engine:
                raise RuntimeError("Comparison engine service not available")
            
            # Validate required data is available
            file1_empty = (self.workflow_data['file1_data'] is None or 
                          (hasattr(self.workflow_data['file1_data'], 'empty') and self.workflow_data['file1_data'].empty))
            file2_empty = (self.workflow_data['file2_data'] is None or 
                          (hasattr(self.workflow_data['file2_data'], 'empty') and self.workflow_data['file2_data'].empty))
            
            if file1_empty or file2_empty:
                raise ValidationError("File data not available for comparison")
            
            # Get operation configuration with comprehensive validation
            try:
                config_panel = self.panels.get(WorkflowState.OPERATION_CONFIG)
                if not config_panel:
                    raise ValidationError("Operation configuration panel not available")
                
                if not hasattr(config_panel, 'get_operation_config'):
                    raise ValidationError("Operation configuration panel missing required method")
                
                operation_config = config_panel.get_operation_config()
                if not operation_config:
                    raise ValidationError("No operation configuration provided")
                
                if not operation_config.get('operation'):
                    raise ValidationError("No comparison operation selected")
                
                logger.info(f"Operation configuration retrieved: {operation_config['operation']}")
                
            except Exception as config_error:
                logger.error(f"Error getting operation configuration: {config_error}")
                self._handle_error(
                    ValidationError(f"Operation configuration error: {config_error}"),
                    "Configuration Error"
                )
                return
            
            # Get column mapping with comprehensive validation
            try:
                mapping_panel = self.panels.get(WorkflowState.COLUMN_MAPPING)
                if not mapping_panel:
                    raise ValidationError("Column mapping panel not available")
                
                if not hasattr(mapping_panel, 'get_selected_columns'):
                    raise ValidationError("Column mapping panel missing required method")
                
                file1_col, file2_col = mapping_panel.get_selected_columns()
                
                if not file1_col or not file2_col:
                    raise ValidationError("Column mapping not complete - please select columns from both files")
                
                # Validate columns exist in data
                if (self.workflow_data['file1_data'] is not None and 
                    not (hasattr(self.workflow_data['file1_data'], 'empty') and self.workflow_data['file1_data'].empty)):
                    # Check if it's a DataFrame with columns
                    if hasattr(self.workflow_data['file1_data'], 'columns'):
                        if file1_col not in self.workflow_data['file1_data'].columns:
                            raise ValidationError(f"Selected column '{file1_col}' not found in file 1")
                    # Check if it's a list of dictionaries
                    elif (isinstance(self.workflow_data['file1_data'], list) and 
                          len(self.workflow_data['file1_data']) > 0 and
                          file1_col not in self.workflow_data['file1_data'][0]):
                        raise ValidationError(f"Selected column '{file1_col}' not found in file 1")
                
                if (self.workflow_data['file2_data'] is not None and 
                    not (hasattr(self.workflow_data['file2_data'], 'empty') and self.workflow_data['file2_data'].empty)):
                    # Check if it's a DataFrame with columns
                    if hasattr(self.workflow_data['file2_data'], 'columns'):
                        if file2_col not in self.workflow_data['file2_data'].columns:
                            raise ValidationError(f"Selected column '{file2_col}' not found in file 2")
                    # Check if it's a list of dictionaries
                    elif (isinstance(self.workflow_data['file2_data'], list) and 
                          len(self.workflow_data['file2_data']) > 0 and
                          file2_col not in self.workflow_data['file2_data'][0]):
                        raise ValidationError(f"Selected column '{file2_col}' not found in file 2")
                
                logger.info(f"Column mapping retrieved: {file1_col} <-> {file2_col}")
                
            except Exception as mapping_error:
                logger.error(f"Error getting column mapping: {mapping_error}")
                self._handle_error(
                    ValidationError(f"Column mapping error: {mapping_error}"),
                    "Configuration Error"
                )
                return
            
            # Create comparison config with validation
            try:
                comparison_config = ComparisonConfig(
                    file1_path=self.workflow_data['file1_info'].file_path,
                    file2_path=self.workflow_data['file2_info'].file_path,
                    file1_column=file1_col,
                    file2_column=file2_col,
                    operation=operation_config['operation'],
                    output_format=operation_config.get('output_format', 'csv'),
                    case_sensitive=operation_config.get('case_sensitive', False)
                )
                
                self.workflow_data['comparison_config'] = comparison_config
                logger.info("Comparison configuration created successfully")
                
            except Exception as config_creation_error:
                logger.error(f"Error creating comparison configuration: {config_creation_error}")
                self._handle_error(
                    ValidationError(f"Configuration creation error: {config_creation_error}"),
                    "Configuration Error"
                )
                return
            
            # Estimate processing time with error handling
            try:
                estimated_time = self.comparison_engine.estimate_processing_time(
                    self.workflow_data['file1_data'], 
                    self.workflow_data['file2_data'], 
                    comparison_config.operation
                )
                logger.info(f"Estimated processing time: {estimated_time:.1f}s")
                
            except Exception as estimation_error:
                logger.warning(f"Could not estimate processing time: {estimation_error}")
                estimated_time = 10.0  # Default estimate
            
            # Show enhanced progress dialog with error handling
            try:
                dialog_title = f"Processing {operation_config['operation'].replace('_', ' ').title()}"
                
                # Check if ProgressDialog is available
                if 'ProgressDialog' not in globals():
                    logger.warning("ProgressDialog not available, using basic progress indication")
                    try:
                        self.main_window.show_progress(True)
                        self.main_window.set_status(f"Processing comparison... (estimated: {estimated_time:.1f}s)")
                    except Exception as basic_progress_error:
                        logger.warning(f"Basic progress indication failed: {basic_progress_error}")
                else:
                    self.progress_dialog = ProgressDialog(
                        self.main_window.root, 
                        dialog_title
                    ).show(
                        f"Preparing comparison operation... (estimated time: {estimated_time:.1f}s)",
                        allow_cancel=True,
                        cancel_callback=self.cancel_operation
                    )
                    
            except Exception as progress_error:
                logger.warning(f"Progress dialog creation failed: {progress_error}")
                # Continue without progress dialog
                try:
                    self.main_window.set_status("Processing comparison...")
                except:
                    pass
            
            # Execute in separate thread to avoid blocking GUI with comprehensive error handling
            try:
                self.operation_cancelled = False
                operation_thread = threading.Thread(
                    target=self._run_comparison_operation_safe,
                    args=(comparison_config,),
                    name="ComparisonOperation"
                )
                operation_thread.daemon = True
                operation_thread.start()
                
                logger.info("Comparison operation thread started successfully")
                
            except Exception as thread_error:
                logger.error(f"Error starting comparison thread: {thread_error}")
                
                # Clean up progress dialog
                if self.progress_dialog:
                    try:
                        self.progress_dialog.close()
                    except:
                        pass
                    self.progress_dialog = None
                
                self._handle_error(
                    RuntimeError(f"Could not start comparison operation: {thread_error}"),
                    "Threading Error",
                    allow_retry=True,
                    retry_callback=self._execute_comparison
                )
            
        except Exception as e:
            logger.error(f"Comparison execution process failed: {e}")
            
            # Clean up any progress indicators
            if self.progress_dialog:
                try:
                    self.progress_dialog.close()
                except:
                    pass
                self.progress_dialog = None
            
            try:
                self.main_window.show_progress(False)
            except:
                pass
            
            self._handle_error(
                e, "Error executing comparison",
                allow_retry=True,
                retry_callback=self._execute_comparison,
                show_recovery_options=True
            )
            
    def _run_comparison_operation_safe(self, config: ComparisonConfig):
        """
        Safely run the comparison operation with comprehensive error handling.
        
        Args:
            config: The comparison configuration
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Starting safe comparison operation execution")
            self._run_comparison_operation(config)
            
        except Exception as e:
            logger.error(f"Error in comparison operation: {e}")
            # Handle error on main thread - capture exception properly
            error = e  # Capture the exception in a local variable
            self.main_window.root.after(0, lambda error=error: self._on_comparison_error(error))
            
    def _run_comparison_operation(self, config: ComparisonConfig):
        """
        Run the comparison operation in a background thread.
        
        Args:
            config: The comparison configuration
        """
        try:
            start_time = time.time()
            
            # Update progress
            if self.progress_dialog:
                self.main_window.root.after(0, lambda: self.progress_dialog.update_progress(10, "Loading data..."))
            
            # Get data
            file1_data = self.workflow_data['file1_data']
            file2_data = self.workflow_data['file2_data']
            
            if self.progress_dialog:
                self.main_window.root.after(0, lambda: self.progress_dialog.update_progress(30, "Preparing comparison..."))
            
            # Check for cancellation
            if self.operation_cancelled or (self.progress_dialog and self.progress_dialog.is_cancelled()):
                return
                
            # Update progress for operation start
            operation_names = {
                'remove_matches': 'Removing matching rows',
                'keep_matches': 'Keeping only matching rows',
                'find_common': 'Finding common values',
                'find_unique': 'Finding unique values'
            }
            operation_message = operation_names.get(config.operation, 'Processing comparison')
            
            if self.progress_dialog:
                self.main_window.root.after(0, lambda: self.progress_dialog.update_progress(50, operation_message + "..."))
            
            # Create progress callback
            def progress_callback(progress: float, message: str):
                if self.progress_dialog and not self.operation_cancelled:
                    # Capture variables properly for lambda
                    self.main_window.root.after(0, lambda p=progress, m=message: self.progress_dialog.update_progress(p, m))
            
            # Reset cancellation state
            self.comparison_engine.reset_cancellation()
            
            # Execute comparison with progress tracking
            if config.operation == 'remove_matches':
                result_data = self.comparison_engine.remove_matches(
                    file1_data, file2_data, config.file1_column, config.file2_column,
                    case_sensitive=config.case_sensitive, progress_callback=progress_callback
                )
            elif config.operation == 'keep_matches':
                result_data = self.comparison_engine.keep_only_matches(
                    file1_data, file2_data, config.file1_column, config.file2_column,
                    case_sensitive=config.case_sensitive, progress_callback=progress_callback
                )
            elif config.operation == 'find_common':
                result_data = self.comparison_engine.find_common_values(
                    file1_data, file2_data, config.file1_column, config.file2_column,
                    case_sensitive=config.case_sensitive, progress_callback=progress_callback
                )
            elif config.operation == 'find_unique':
                result_data = self.comparison_engine.find_unique_values(
                    file1_data, file2_data, config.file1_column, config.file2_column,
                    case_sensitive=config.case_sensitive, progress_callback=progress_callback
                )
            else:
                raise ComparisonOperationError(f"Unknown operation: {config.operation}")
                
            if self.progress_dialog:
                self.main_window.root.after(0, lambda: self.progress_dialog.update_progress(80, "Finalizing results..."))
            
            # Check for cancellation
            if self.operation_cancelled or (self.progress_dialog and self.progress_dialog.is_cancelled()):
                return
                
            # Create operation result
            processing_time = time.time() - start_time
            
            # result_data is already an OperationResult from comparison engine
            # Extract the actual DataFrame and metadata
            if isinstance(result_data, OperationResult):
                operation_result = result_data
            else:
                # Fallback for backward compatibility
                original_count = len(file2_data)  # Usually comparing against file2
                result_count = len(result_data)
                
                summary = self._generate_operation_summary(
                    config.operation, original_count, result_count, processing_time
                )
                
                operation_result = OperationResult(
                    result_data=result_data,
                    original_count=original_count,
                    result_count=result_count,
                    operation_type=config.operation,
                    processing_time=processing_time,
                    summary=summary
                )
            
            self.workflow_data['operation_result'] = operation_result
            
            if self.progress_dialog:
                self.main_window.root.after(0, lambda: self.progress_dialog.update_progress(100, "Comparison completed!"))
            
            # Update GUI on main thread
            self.main_window.root.after(0, self._on_comparison_complete)
            
        except InterruptedError:
            # Handle cancellation
            self.main_window.root.after(0, self._on_comparison_cancelled)
        except Exception as e:
            # Handle error on main thread - capture exception properly
            error = e  # Capture the exception in a local variable
            self.main_window.root.after(0, lambda error=error: self._on_comparison_error(error))
    
    def cancel_operation(self):
        """Cancel the current operation."""
        try:
            self.operation_cancelled = True
            
            # Cancel comparison engine operation
            if self.comparison_engine:
                self.comparison_engine.cancel_operation()
                
            # Update progress dialog
            if self.progress_dialog:
                self.progress_dialog.update_progress(
                    self.progress_dialog.current_progress,
                    "Cancelling operation..."
                )
                
        except Exception as e:
            print(f"Error during cancellation: {e}")
    
    def _on_comparison_cancelled(self):
        """Handle cancellation of comparison operation."""
        try:
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
                
            self.main_window.show_progress(False)
            self.main_window.set_status("Operation cancelled by user")
            
            # Reset cancellation flag
            self.operation_cancelled = False
            
        except Exception as e:
            self._handle_error(e, "Error handling operation cancellation")
            
    def _on_comparison_complete(self):
        """Handle completion of comparison operation."""
        try:
            # Close progress dialog
            if self.progress_dialog:
                # Small delay to show completion
                self.main_window.root.after(1000, self.progress_dialog.close)
                self.progress_dialog = None
                
            self.main_window.show_progress(False)
            self.main_window.set_status("Comparison completed successfully")
            
            # Transition to results state and show results panel
            self._update_workflow_state(WorkflowState.RESULTS)
            
            # Update results panel with data
            results_panel = self.panels.get(WorkflowState.RESULTS)
            if results_panel and hasattr(results_panel, 'display_results'):
                results_panel.display_results(self.workflow_data['operation_result'])
                
        except Exception as e:
            self._handle_error(e, "Error handling comparison completion")
            
    def _on_comparison_error(self, error: Exception):
        """Handle error during comparison operation."""
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
            
        self.main_window.show_progress(False)
        self._handle_error(
            error, "Error during comparison operation",
            allow_retry=True,
            retry_callback=self._execute_comparison
        )
        
    def _generate_operation_summary(self, operation: str, original_count: int, 
                                  result_count: int, processing_time: float) -> str:
        """
        Generate a human-readable summary of the operation results.
        
        Args:
            operation: The operation type
            original_count: Original number of rows
            result_count: Resulting number of rows
            processing_time: Time taken for processing
            
        Returns:
            str: Human-readable summary
        """
        operation_names = {
            'remove_matches': 'Remove Matches',
            'keep_matches': 'Keep Only Matches',
            'find_common': 'Find Common Values',
            'find_unique': 'Find Unique Values'
        }
        
        op_name = operation_names.get(operation, operation)
        
        return (f"{op_name} operation completed in {processing_time:.2f} seconds. "
                f"Processed {original_count:,} rows, resulting in {result_count:,} rows.")
        
    # Event handlers for panel interactions
    def _handle_files_changed(self, file1_info: Optional[FileInfo], 
                            file2_info: Optional[FileInfo]):
        """
        Handle file selection changes.
        
        Args:
            file1_info: Information about the first selected file
            file2_info: Information about the second selected file
        """
        try:
            self.workflow_data['file1_info'] = file1_info
            self.workflow_data['file2_info'] = file2_info
            
            # Load file data if both files are selected
            if file1_info and file2_info:
                self._load_file_data()
                
        except Exception as e:
            self._handle_error(e, "Error handling file selection")
            
    def _load_file_data(self):
        """Load data from selected files with comprehensive error handling and recovery."""
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Starting file data loading process")
            
            # Validate file parser availability
            if not self.file_parser:
                raise RuntimeError("File parser service not available")
            
            # Validate file information
            if not self.workflow_data['file1_info'] and not self.workflow_data['file2_info']:
                raise ValidationError("No files selected for loading")
            
            # Update status
            try:
                self.main_window.set_status("Loading file data...")
            except Exception as status_error:
                logger.warning(f"Could not update status: {status_error}")
            
            # Load file 1 with comprehensive error handling
            if self.workflow_data['file1_info']:
                try:
                    logger.info(f"Loading file 1: {self.workflow_data['file1_info'].file_path}")
                    
                    # Validate file exists and is accessible
                    file_path = self.workflow_data['file1_info'].file_path
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"File 1 not found: {file_path}")
                    
                    if not os.access(file_path, os.R_OK):
                        raise PermissionError(f"Cannot read file 1: {file_path}")
                    
                    # Parse file with progress indication
                    try:
                        self.main_window.set_status("Loading file 1...")
                    except:
                        pass
                        
                    self.workflow_data['file1_data'] = self.file_parser.parse_file(file_path)
                    
                    # Validate loaded data
                    if self.workflow_data['file1_data'] is None:
                        raise FileParsingError("File 1 parsing returned no data")
                    
                    # Check if data is empty (works for both DataFrames and lists)
                    if (hasattr(self.workflow_data['file1_data'], 'empty') and self.workflow_data['file1_data'].empty) or len(self.workflow_data['file1_data']) == 0:
                        raise FileParsingError("File 1 contains no data rows")
                    
                    logger.info(f"File 1 loaded successfully: {len(self.workflow_data['file1_data'])} rows")
                    
                except Exception as file1_error:
                    logger.error(f"Error loading file 1: {file1_error}")
                    
                    # Clear file 1 data on error
                    self.workflow_data['file1_data'] = None
                    
                    # Provide specific error handling for file 1
                    if isinstance(file1_error, (FileNotFoundError, PermissionError)):
                        # File access error - suggest reselection
                        result = messagebox.askyesno(
                            "File 1 Access Error",
                            f"Cannot access file 1:\n{file1_error}\n\nWould you like to select a different file?"
                        )
                        if result:
                            # Trigger file reselection
                            try:
                                self._trigger_file_selection(1)
                                return  # Exit early, reselection will trigger reload
                            except Exception as reselect_error:
                                logger.error(f"File reselection failed: {reselect_error}")
                        raise file1_error
                    else:
                        # Parsing error - offer retry or different file
                        raise FileParsingError(f"Error parsing file 1: {file1_error}")
                
            # Load file 2 with comprehensive error handling
            if self.workflow_data['file2_info']:
                try:
                    logger.info(f"Loading file 2: {self.workflow_data['file2_info'].file_path}")
                    
                    # Validate file exists and is accessible
                    file_path = self.workflow_data['file2_info'].file_path
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"File 2 not found: {file_path}")
                    
                    if not os.access(file_path, os.R_OK):
                        raise PermissionError(f"Cannot read file 2: {file_path}")
                    
                    # Parse file with progress indication
                    try:
                        self.main_window.set_status("Loading file 2...")
                    except:
                        pass
                        
                    self.workflow_data['file2_data'] = self.file_parser.parse_file(file_path)
                    
                    # Validate loaded data
                    if self.workflow_data['file2_data'] is None:
                        raise FileParsingError("File 2 parsing returned no data")
                    
                    # Check if data is empty (works for both DataFrames and lists)
                    if (hasattr(self.workflow_data['file2_data'], 'empty') and self.workflow_data['file2_data'].empty) or len(self.workflow_data['file2_data']) == 0:
                        raise FileParsingError("File 2 contains no data rows")
                    
                    logger.info(f"File 2 loaded successfully: {len(self.workflow_data['file2_data'])} rows")
                    
                except Exception as file2_error:
                    logger.error(f"Error loading file 2: {file2_error}")
                    
                    # Clear file 2 data on error
                    self.workflow_data['file2_data'] = None
                    
                    # Provide specific error handling for file 2
                    if isinstance(file2_error, (FileNotFoundError, PermissionError)):
                        # File access error - suggest reselection
                        result = messagebox.askyesno(
                            "File 2 Access Error",
                            f"Cannot access file 2:\n{file2_error}\n\nWould you like to select a different file?"
                        )
                        if result:
                            # Trigger file reselection
                            try:
                                self._trigger_file_selection(2)
                                return  # Exit early, reselection will trigger reload
                            except Exception as reselect_error:
                                logger.error(f"File reselection failed: {reselect_error}")
                        raise file2_error
                    else:
                        # Parsing error - offer retry or different file
                        raise FileParsingError(f"Error parsing file 2: {file2_error}")
            
            # Validate that we have data to work with
            file1_empty = (self.workflow_data['file1_data'] is None or 
                          (hasattr(self.workflow_data['file1_data'], 'empty') and self.workflow_data['file1_data'].empty))
            file2_empty = (self.workflow_data['file2_data'] is None or 
                          (hasattr(self.workflow_data['file2_data'], 'empty') and self.workflow_data['file2_data'].empty))
            
            if file1_empty and file2_empty:
                raise ValidationError("No file data was successfully loaded")
            
            # Update column mapping panel with comprehensive error handling
            if (self.workflow_data['file1_data'] is not None and 
                self.workflow_data['file2_data'] is not None):
                
                try:
                    logger.info("Updating column mapping panel with loaded data")
                    
                    mapping_panel = self.panels.get(WorkflowState.COLUMN_MAPPING)
                    if mapping_panel and hasattr(mapping_panel, 'set_file_data'):
                        mapping_panel.set_file_data(
                            self.workflow_data['file1_info'],
                            self.workflow_data['file2_info'],
                            self.workflow_data['file1_data'],
                            self.workflow_data['file2_data']
                        )
                        logger.info("Column mapping panel updated successfully")
                    else:
                        logger.warning("Column mapping panel not available or missing set_file_data method")
                        
                except Exception as mapping_error:
                    logger.error(f"Error updating column mapping panel: {mapping_error}")
                    # Don't fail the entire load process for mapping panel errors
                    try:
                        self.main_window.set_status("Files loaded, but column mapping update failed")
                    except:
                        pass
            
            # Update status with success message
            try:
                file1_rows = len(self.workflow_data['file1_data']) if self.workflow_data['file1_data'] else 0
                file2_rows = len(self.workflow_data['file2_data']) if self.workflow_data['file2_data'] else 0
                
                if file1_rows > 0 and file2_rows > 0:
                    status_msg = f"Files loaded successfully: {file1_rows} + {file2_rows} rows"
                elif file1_rows > 0:
                    status_msg = f"File 1 loaded successfully: {file1_rows} rows (File 2 failed)"
                elif file2_rows > 0:
                    status_msg = f"File 2 loaded successfully: {file2_rows} rows (File 1 failed)"
                else:
                    status_msg = "File loading completed with errors"
                    
                self.main_window.set_status(status_msg)
                logger.info(f"File loading completed: {status_msg}")
                
            except Exception as status_error:
                logger.warning(f"Could not update final status: {status_error}")
            
        except Exception as e:
            logger.error(f"File loading process failed: {e}")
            
            # Clear any partially loaded data
            if isinstance(e, (FileParsingError, FileNotFoundError, PermissionError)):
                # Don't clear data for specific file errors as they're handled above
                pass
            else:
                # Clear all data for general errors
                self.workflow_data['file1_data'] = None
                self.workflow_data['file2_data'] = None
            
            # Update status with error
            try:
                self.main_window.set_status("File loading failed - see error dialog")
            except:
                pass
            
            # Handle error with retry option and enhanced recovery
            self._handle_error(
                e, "Error loading file data", 
                allow_retry=True, 
                retry_callback=self._load_file_data,
                show_recovery_options=True
            )
            
    def _handle_mapping_changed(self, file1_column: str, file2_column: str):
        """
        Handle column mapping changes.
        
        Args:
            file1_column: Selected column from first file
            file2_column: Selected column from second file
        """
        try:
            # Store mapping information for later use
            self.workflow_data['column_mapping'] = {
                'file1_column': file1_column,
                'file2_column': file2_column
            }
            
        except Exception as e:
            self._handle_error(e, "Error handling column mapping")
            
    def _handle_config_changed(self, config: Dict[str, Any]):
        """
        Handle operation configuration changes.
        
        Args:
            config: Operation configuration dictionary
        """
        try:
            # Store configuration for later use
            self.workflow_data['operation_config'] = config
            
        except Exception as e:
            self._handle_error(e, "Error handling configuration change")
            
    def _trigger_file_selection(self, file_num: int):
        """
        Trigger file selection from menu for a specific file.
        
        Args:
            file_num: File number (1 or 2)
        """
        try:
            # Navigate to file selection step if not already there
            if self.current_state != WorkflowState.FILE_SELECTION:
                self.current_state = WorkflowState.FILE_SELECTION
                self._show_current_panel()
            
            # Get the file selection panel
            file_panel = self.panels.get(WorkflowState.FILE_SELECTION)
            if file_panel and hasattr(file_panel, '_browse_file'):
                # Trigger the browse file method directly
                file_panel._browse_file(file_num)
            else:
                # Fallback to basic file dialog
                from tkinter import filedialog
                filetypes = [
                    ("Supported files", "*.csv;*.xlsx;*.xls"),
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx;*.xls"),
                    ("All files", "*.*")
                ]
                
                filename = filedialog.askopenfilename(
                    title=f"Select File {file_num}",
                    filetypes=filetypes
                )
                
                if filename and file_panel and hasattr(file_panel, '_load_file'):
                    file_panel._load_file(filename, file_num)
                    
        except Exception as e:
            self._handle_error(e, f"Error selecting file {file_num}")

    def _show_current_panel(self):
        """
        Display the panel corresponding to the current workflow state.
        
        This method implements proper panel display logic with comprehensive validation,
        error handling, and proper grid management as per requirements 3.1, 3.3, 4.3.
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info(f"Attempting to show panel for state: {self.current_state.name}")
            
            # Enhanced Validation 1: Comprehensive panel existence check (Requirement 3.1)
            if not hasattr(self, 'panels') or not self.panels:
                error_msg = "Panel dictionary not initialized"
                logger.error(error_msg)
                self._handle_panel_display_error(error_msg, "Panel System Error")
                return False
            
            if self.current_state not in self.panels:
                error_msg = f"Panel for state {self.current_state.name} does not exist in panels dictionary"
                logger.error(error_msg)
                # Log available panels for debugging
                available_panels = list(self.panels.keys())
                logger.debug(f"Available panels: {[state.name for state in available_panels]}")
                self._handle_panel_display_error(error_msg, "Missing Panel")
                return False
            
            panel = self.panels[self.current_state]
            if not panel:
                error_msg = f"Panel for state {self.current_state.name} is None"
                logger.error(error_msg)
                self._handle_panel_display_error(error_msg, "Invalid Panel")
                return False
            
            # Enhanced Validation 2: Comprehensive panel readiness check
            if hasattr(self, 'panel_states') and self.current_state in self.panel_states:
                panel_state = self.panel_states[self.current_state]
                if not panel_state.get('initialized', False):
                    error_msg = f"Panel for state {self.current_state.name} was not properly initialized"
                    logger.error(error_msg)
                    self._handle_panel_display_error(error_msg, "Panel Not Initialized")
                    return False
                    
                if not panel_state.get('ready_for_display', False):
                    error_msg = f"Panel for state {self.current_state.name} is not ready for display: {panel_state.get('error_message', 'Unknown error')}"
                    logger.warning(error_msg)
                    # Only proceed with fallback panel if available
                    if not panel_state.get('fallback_created', False):
                        self._handle_panel_display_error(error_msg, "Panel Not Ready")
                        return False
                    else:
                        logger.info(f"Proceeding with fallback panel for {self.current_state.name}")
            
            # Enhanced Validation 3: Content frame validation and configuration (Requirement 3.3)
            if not hasattr(self.main_window, 'content_frame') or not self.main_window.content_frame:
                error_msg = "Main window content frame not available for panel display"
                logger.error(error_msg)
                self._handle_panel_display_error(error_msg, "Content Frame Error")
                return False
            
            # Validate content frame is properly configured
            try:
                # Test content frame accessibility
                content_frame = self.main_window.content_frame
                if not content_frame.winfo_exists():
                    error_msg = "Content frame widget no longer exists"
                    logger.error(error_msg)
                    self._handle_panel_display_error(error_msg, "Content Frame Destroyed")
                    return False
                    
                # Ensure content frame has proper parent
                if not content_frame.winfo_parent():
                    error_msg = "Content frame has no parent widget"
                    logger.error(error_msg)
                    self._handle_panel_display_error(error_msg, "Content Frame Orphaned")
                    return False
                    
            except tk.TclError as tcl_error:
                error_msg = f"Content frame validation failed: {tcl_error}"
                logger.error(error_msg)
                self._handle_panel_display_error(error_msg, "Content Frame Invalid")
                return False
            
            # Enhanced Validation 4: Panel widget structure validation
            panel_widget = getattr(panel, 'panel', panel)
            if not panel_widget:
                error_msg = f"Panel widget for state {self.current_state.name} is invalid or missing"
                logger.error(error_msg)
                self._handle_panel_display_error(error_msg, "Invalid Panel Widget")
                return False
            
            # Validate panel widget integrity
            try:
                if not panel_widget.winfo_exists():
                    error_msg = f"Panel widget for state {self.current_state.name} no longer exists"
                    logger.error(error_msg)
                    self._handle_panel_display_error(error_msg, "Panel Widget Destroyed")
                    return False
                    
                # Ensure panel widget has required grid methods
                if not hasattr(panel_widget, 'grid') or not hasattr(panel_widget, 'grid_remove'):
                    error_msg = f"Panel widget for state {self.current_state.name} does not support required grid methods"
                    logger.error(error_msg)
                    self._handle_panel_display_error(error_msg, "Grid Layout Not Supported")
                    return False
                    
                # Test grid configuration capability
                try:
                    panel_widget.grid_info()  # This will raise an error if widget can't be gridded
                except tk.TclError:
                    # Widget might not be gridded yet, which is fine
                    pass
                    
            except tk.TclError as tcl_error:
                error_msg = f"Panel widget validation failed for {self.current_state.name}: {tcl_error}"
                logger.error(error_msg)
                self._handle_panel_display_error(error_msg, "Panel Widget Invalid")
                return False
            
            logger.debug(f"All panel validations passed for {self.current_state.name}")
            
            # Enhanced panel hiding/showing with proper grid management (Requirement 3.3)
            try:
                logger.debug("Starting panel display sequence")
                
                # Step 1: Properly hide current panel if one is displayed
                if hasattr(self.main_window, 'current_panel') and self.main_window.current_panel:
                    current_panel = self.main_window.current_panel
                    logger.debug(f"Hiding current panel: {current_panel}")
                    
                    try:
                        # Use grid_remove to hide but preserve configuration
                        current_panel.grid_remove()
                        logger.debug("Current panel hidden successfully")
                    except tk.TclError as hide_error:
                        logger.warning(f"Error hiding current panel: {hide_error}")
                        # Try alternative hiding method
                        try:
                            current_panel.grid_forget()
                            logger.debug("Current panel hidden using grid_forget")
                        except tk.TclError:
                            logger.warning("Could not hide current panel, proceeding anyway")
                
                # Step 2: Configure content frame for proper child widget expansion
                content_frame = self.main_window.content_frame
                logger.debug("Configuring content frame grid weights")
                
                try:
                    # Clear any existing grid configuration
                    for child in content_frame.winfo_children():
                        try:
                            child.grid_remove()
                        except tk.TclError:
                            pass  # Child might not be gridded
                    
                    # Configure content frame for single child expansion
                    content_frame.grid_rowconfigure(0, weight=1, minsize=0)
                    content_frame.grid_columnconfigure(0, weight=1, minsize=0)
                    
                    # Clear any other row/column configurations
                    for i in range(1, 10):  # Clear up to 10 rows/columns
                        try:
                            content_frame.grid_rowconfigure(i, weight=0, minsize=0)
                            content_frame.grid_columnconfigure(i, weight=0, minsize=0)
                        except tk.TclError:
                            break  # No more configurations to clear
                            
                    logger.debug("Content frame grid configuration completed")
                    
                except tk.TclError as config_error:
                    logger.warning(f"Content frame configuration warning: {config_error}")
                    # Continue anyway as this might not be critical
                
                # Step 3: Configure panel widget for proper display
                logger.debug(f"Configuring panel widget for {self.current_state.name}")
                
                try:
                    # Ensure panel widget is properly configured for grid
                    panel_widget.grid_configure(row=0, column=0, sticky='nsew', padx=0, pady=0)
                    logger.debug("Panel widget grid configuration set")
                    
                except tk.TclError as panel_config_error:
                    logger.warning(f"Panel widget configuration warning: {panel_config_error}")
                    # Try basic grid configuration
                    try:
                        panel_widget.grid(row=0, column=0, sticky='nsew')
                        logger.debug("Panel widget basic grid configuration applied")
                    except tk.TclError as basic_error:
                        error_msg = f"Cannot configure panel widget for grid display: {basic_error}"
                        logger.error(error_msg)
                        self._handle_panel_display_error(error_msg, "Panel Configuration Error", basic_error)
                        return False
                
                # Step 4: Show new panel using MainWindow's show_panel method
                logger.debug(f"Displaying panel for {self.current_state.name}")
                
                try:
                    self.main_window.show_panel(panel_widget)
                    logger.debug("MainWindow show_panel method called successfully")
                except Exception as show_error:
                    logger.warning(f"MainWindow show_panel method failed: {show_error}")
                    # Fallback to direct display
                    try:
                        self.main_window.current_panel = panel_widget
                        panel_widget.tkraise()  # Bring to front
                        logger.debug("Fallback panel display method used")
                    except Exception as fallback_error:
                        error_msg = f"Both primary and fallback panel display methods failed: {fallback_error}"
                        logger.error(error_msg)
                        self._handle_panel_display_error(error_msg, "Panel Display Failed", fallback_error)
                        return False
                
                # Step 5: Update main window state and indicators
                logger.debug("Updating main window state indicators")
                
                try:
                    # Update main window step indicator to match current state
                    self.main_window.current_step = self.current_state.value
                    
                    # Update step indicator if method exists
                    if hasattr(self.main_window, '_update_step_indicator'):
                        self.main_window._update_step_indicator()
                        logger.debug("Step indicator updated")
                    
                    # Update navigation button states using enhanced method
                    self._update_navigation_button_states()
                        
                except Exception as update_error:
                    logger.warning(f"Error updating main window indicators: {update_error}")
                    # Continue as this is not critical for panel display
                
                # Step 6: Force layout updates to ensure proper display
                logger.debug("Forcing layout updates")
                
                try:
                    # Update content frame first
                    content_frame.update_idletasks()
                    
                    # Update panel widget
                    panel_widget.update_idletasks()
                    
                    # Update main window
                    self.main_window.root.update_idletasks()
                    
                    logger.debug("Layout updates completed")
                    
                except tk.TclError as update_error:
                    logger.warning(f"Layout update warning: {update_error}")
                    # Continue as updates might not be critical
                
                logger.info(f"Successfully displayed panel for {self.current_state.name}")
                
                # Step 7: Update status message based on current state
                try:
                    status_messages = {
                        WorkflowState.FILE_SELECTION: "Select files for comparison",
                        WorkflowState.COLUMN_MAPPING: "Map columns between files",
                        WorkflowState.OPERATION_CONFIG: "Configure comparison operation",
                        WorkflowState.RESULTS: "View comparison results"
                    }
                    
                    status_msg = status_messages.get(self.current_state, f"Current step: {self.current_state.name}")
                    
                    if hasattr(self.main_window, 'set_status'):
                        self.main_window.set_status(status_msg)
                        logger.debug(f"Status message updated: {status_msg}")
                    
                except Exception as status_error:
                    logger.warning(f"Error updating status message: {status_error}")
                    # Continue as this is not critical
                
                return True
                
            except Exception as display_error:
                error_msg = f"Error during panel display sequence for {self.current_state.name}: {display_error}"
                logger.error(error_msg, exc_info=True)
                self._handle_panel_display_error(error_msg, "Display Sequence Error", display_error)
                return False
                
        except Exception as e:
            error_msg = f"Unexpected error in _show_current_panel for state {self.current_state.name}: {e}"
            logger.error(error_msg, exc_info=True)
            self._handle_panel_display_error(error_msg, "Critical Display Error", e)
            return False
    
    def _handle_panel_display_error(self, error_msg: str, error_title: str, exception: Exception = None):
        """
        Handle errors that occur during panel display with recovery options.
        
        Args:
            error_msg: Detailed error message
            error_title: Short error title for user display
            exception: Optional exception object for detailed logging
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.error(f"Panel display error: {error_msg}")
            
            # Try recovery strategies
            recovery_attempted = False
            
            # Recovery 1: Try to create fallback panel if missing
            if "does not exist" in error_msg or "is None" in error_msg:
                logger.info("Attempting to create fallback panel for recovery")
                try:
                    self._create_fallback_panels()
                    # Retry display after fallback creation
                    if self.current_state in self.panels and self.panels[self.current_state]:
                        logger.info("Retrying panel display after fallback creation")
                        return self._show_current_panel()
                    recovery_attempted = True
                except Exception as fallback_error:
                    logger.error(f"Fallback panel creation failed: {fallback_error}")
            
            # Recovery 2: Try to reset to FILE_SELECTION state if current state is problematic
            if self.current_state != WorkflowState.FILE_SELECTION:
                logger.info("Attempting to reset to FILE_SELECTION state for recovery")
                try:
                    self.current_state = WorkflowState.FILE_SELECTION
                    if WorkflowState.FILE_SELECTION in self.panels and self.panels[WorkflowState.FILE_SELECTION]:
                        logger.info("Retrying panel display with FILE_SELECTION state")
                        return self._show_current_panel()
                    recovery_attempted = True
                except Exception as reset_error:
                    logger.error(f"State reset recovery failed: {reset_error}")
            
            # Recovery 3: Show minimal error panel as last resort
            if not recovery_attempted:
                logger.info("Creating minimal error panel as last resort")
                try:
                    self._show_minimal_error_panel(error_msg)
                    recovery_attempted = True
                except Exception as minimal_error:
                    logger.error(f"Minimal error panel creation failed: {minimal_error}")
            
            # Show user-friendly error message
            user_message = f"Unable to display the {self.current_state.name.replace('_', ' ').lower()} panel."
            if recovery_attempted:
                user_message += "\n\nA recovery attempt was made. Please try restarting the application if problems persist."
            else:
                user_message += "\n\nPlease restart the application."
            
            # Use error handler if available, otherwise show basic messagebox
            if self.error_handler:
                self.error_handler.handle_error(
                    exception or Exception(error_msg),
                    error_title,
                    self.main_window.root,
                    show_dialog=True
                )
            else:
                messagebox.showerror(error_title, user_message)
                
        except Exception as handler_error:
            logger.critical(f"Error in panel display error handler: {handler_error}")
            # Last resort - basic error display
            try:
                messagebox.showerror("Critical Error", f"A critical error occurred: {error_msg}")
            except:
                print(f"CRITICAL ERROR: {error_msg}")
    
    def _show_minimal_error_panel(self, error_message: str):
        """
        Show a minimal error panel when normal panel display fails.
        
        Args:
            error_message: The error message to display
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Creating minimal error panel")
            
            # Create minimal error display
            error_frame = tk.Frame(self.main_window.content_frame, bg='#f8f8f8', relief='solid', borderwidth=1)
            
            # Error content
            content_frame = tk.Frame(error_frame, bg='#f8f8f8')
            content_frame.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Error icon
            icon_label = tk.Label(content_frame, text="⚠️", font=('Arial', 32), bg='#f8f8f8', fg='#dc3545')
            icon_label.pack(pady=(0, 15))
            
            # Error title
            title_label = tk.Label(
                content_frame,
                text="Panel Display Error",
                font=('Arial', 16, 'bold'),
                bg='#f8f8f8',
                fg='#212529'
            )
            title_label.pack(pady=(0, 10))
            
            # Error message
            message_label = tk.Label(
                content_frame,
                text=f"Unable to display the current panel.\n\n{error_message}",
                font=('Arial', 10),
                bg='#f8f8f8',
                fg='#6c757d',
                justify='center',
                wraplength=400
            )
            message_label.pack(pady=(0, 20))
            
            # Action buttons
            button_frame = tk.Frame(content_frame, bg='#f8f8f8')
            button_frame.pack()
            
            def retry_display():
                try:
                    self._show_current_panel()
                except Exception as retry_error:
                    logger.error(f"Retry failed: {retry_error}")
                    messagebox.showerror("Retry Failed", "Unable to recover. Please restart the application.")
            
            def reset_to_start():
                try:
                    self.current_state = WorkflowState.FILE_SELECTION
                    self._show_current_panel()
                except Exception as reset_error:
                    logger.error(f"Reset failed: {reset_error}")
                    messagebox.showerror("Reset Failed", "Unable to reset. Please restart the application.")
            
            retry_button = tk.Button(button_frame, text="Retry", command=retry_display)
            retry_button.pack(side='left', padx=5)
            
            reset_button = tk.Button(button_frame, text="Reset to Start", command=reset_to_start)
            reset_button.pack(side='left', padx=5)
            
            # Show the error panel
            self.main_window.show_panel(error_frame)
            self.main_window.set_status("Panel display error - see main area for details")
            
            logger.info("Minimal error panel displayed successfully")
            
        except Exception as e:
            logger.critical(f"Failed to create minimal error panel: {e}")
            raise

    def _handle_export_request(self, export_config: Dict[str, Any]):
        """
        Handle export request from results panel.
        
        Args:
            export_config: Export configuration including format and path
        """
        try:
            if not self.workflow_data['operation_result']:
                messagebox.showerror("Export Error", "No results available to export.")
                return
                
            # Get export path from user if not provided
            export_path = export_config.get('path')
            if not export_path:
                export_format = export_config.get('format', 'csv')
                filetypes = [("CSV files", "*.csv")] if export_format == 'csv' else [("Excel files", "*.xlsx")]
                export_path = filedialog.asksaveasfilename(
                    title="Save Results As",
                    filetypes=filetypes,
                    defaultextension=f".{export_format}"
                )
                
            if not export_path:
                return  # User cancelled
                
            # Show progress
            self.main_window.set_status("Exporting results...")
            
            # Export results
            result_data = self.workflow_data['operation_result'].result_data
            
            if export_config.get('format', 'csv') == 'csv':
                success = self.export_service.export_to_csv(result_data, export_path)
            else:
                success = self.export_service.export_to_excel(result_data, export_path)
                
            if success:
                self.main_window.set_status(f"Results exported to {export_path}")
                messagebox.showinfo("Export Complete", f"Results successfully exported to:\n{export_path}")
            else:
                messagebox.showerror("Export Error", "Failed to export results.")
                
        except Exception as e:
            self._handle_error(e, "Error exporting results")
            
    def _handle_error(self, error: Exception, context: str = "", 
                     allow_retry: bool = False, retry_callback: Optional[Callable] = None,
                     show_recovery_options: bool = True):
        """
        Handle errors with comprehensive error handling and user feedback.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            allow_retry: Whether to offer retry option
            retry_callback: Function to call for retry
            show_recovery_options: Whether to show recovery options to user
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.error(f"Error in {context}: {error}", exc_info=True)
            
            # Track error for recovery analysis
            error_key = f"{context}:{type(error).__name__}"
            if error_key not in self.recovery_attempts:
                self.recovery_attempts[error_key] = 0
            self.recovery_attempts[error_key] += 1
            
            # Hide progress if showing
            try:
                if hasattr(self.main_window, 'show_progress'):
                    self.main_window.show_progress(False)
                if self.progress_dialog:
                    self.progress_dialog.close()
                    self.progress_dialog = None
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up progress indicators: {cleanup_error}")
            
            # Determine if automatic recovery should be attempted
            should_auto_recover = (
                self.recovery_attempts[error_key] <= 3 and  # Limit retry attempts
                self._is_recoverable_error(error) and
                retry_callback is not None
            )
            
            # Attempt automatic recovery for certain error types
            if should_auto_recover:
                logger.info(f"Attempting automatic recovery for {error_key} (attempt {self.recovery_attempts[error_key]})")
                try:
                    # Add delay for transient errors
                    if self._is_transient_error(error):
                        import time
                        time.sleep(0.5)
                    
                    retry_callback()
                    logger.info(f"Automatic recovery successful for {error_key}")
                    
                    # Update status with recovery message
                    if hasattr(self.main_window, 'set_status'):
                        self.main_window.set_status("Recovered from error - operation completed")
                    return
                    
                except Exception as recovery_error:
                    logger.error(f"Automatic recovery failed for {error_key}: {recovery_error}")
                    # Continue to manual error handling
            
            # Use enhanced error handler if available
            if self.error_handler:
                try:
                    retry_attempted = self.error_handler.handle_error(
                        error, context, self.main_window.root, 
                        show_dialog=True, allow_retry=allow_retry, 
                        retry_callback=retry_callback
                    )
                    
                    if retry_attempted and retry_callback:
                        try:
                            retry_callback()
                            logger.info(f"Manual retry successful for {error_key}")
                            return
                        except Exception as retry_error:
                            logger.error(f"Manual retry failed for {error_key}: {retry_error}")
                            # Handle retry failure with enhanced context
                            self._handle_error(retry_error, f"Retry failed for: {context}", 
                                             allow_retry=False, show_recovery_options=False)
                            return
                            
                except Exception as handler_error:
                    logger.error(f"Error handler failed: {handler_error}")
                    # Fall back to basic error handling
                    self._handle_error_fallback(error, context, show_recovery_options)
                    
            else:
                # Fallback to enhanced basic error handling
                self._handle_error_fallback(error, context, show_recovery_options)
                
            # Update status with appropriate message
            try:
                if hasattr(self.main_window, 'set_status'):
                    if self.recovery_attempts[error_key] > 1:
                        self.main_window.set_status(f"Error occurred (attempt {self.recovery_attempts[error_key]}) - see error dialog")
                    else:
                        self.main_window.set_status("Error occurred - see error dialog for details")
            except Exception as status_error:
                logger.warning(f"Could not update status: {status_error}")
            
        except Exception as nested_error:
            logger.critical(f"Critical error in error handler: {nested_error}")
            # Critical error fallback
            self._handle_critical_error(nested_error, error, context)
            
    def _is_recoverable_error(self, error: Exception) -> bool:
        """
        Determine if an error is potentially recoverable through retry.
        
        Args:
            error: The exception to check
            
        Returns:
            bool: True if error might be recoverable
        """
        recoverable_types = (
            FileParsingError,
            tk.TclError,  # GUI-related errors that might be transient
            OSError,      # File system errors that might be temporary
            PermissionError,
            TimeoutError
        )
        
        # Check for specific error messages that indicate recoverable conditions
        error_str = str(error).lower()
        recoverable_messages = [
            'temporarily unavailable',
            'resource busy',
            'connection',
            'timeout',
            'permission denied',
            'file not found',
            'access denied'
        ]
        
        return (isinstance(error, recoverable_types) or 
                any(msg in error_str for msg in recoverable_messages))
    
    def _is_transient_error(self, error: Exception) -> bool:
        """
        Determine if an error is likely transient and might resolve with a brief delay.
        
        Args:
            error: The exception to check
            
        Returns:
            bool: True if error is likely transient
        """
        transient_types = (tk.TclError, OSError, PermissionError)
        error_str = str(error).lower()
        transient_messages = ['busy', 'temporarily', 'timeout', 'connection']
        
        return (isinstance(error, transient_types) or 
                any(msg in error_str for msg in transient_messages))
            
    def _handle_error_fallback(self, error: Exception, context: str = "", show_recovery_options: bool = True):
        """
        Enhanced fallback error handling when ErrorHandler is not available.
        
        Args:
            error: The exception that occurred
            context: Additional context
            show_recovery_options: Whether to show recovery options
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Generate user-friendly error message with enhanced details
            if isinstance(error, FileParsingError):
                message = f"Error reading file: {str(error)}"
                suggestions = "• Check that the file is not corrupted\n• Ensure the file is not open in another application\n• Try selecting a different file"
            elif isinstance(error, InvalidFileFormatError):
                message = f"Invalid file format: {str(error)}"
                suggestions = "• Ensure the file is a supported format (CSV, Excel)\n• Check that the file contains valid data\n• Try converting the file to CSV format"
            elif isinstance(error, ComparisonOperationError):
                message = f"Comparison error: {str(error)}"
                suggestions = "• Check that both files have data in the selected columns\n• Ensure column mappings are correct\n• Try a different comparison operation"
            elif isinstance(error, ExportError):
                message = f"Export error: {str(error)}"
                suggestions = "• Check that you have write permissions to the destination\n• Ensure the destination folder exists\n• Try exporting to a different location"
            elif isinstance(error, ValidationError):
                message = f"Validation error: {str(error)}"
                suggestions = "• Check that all required fields are filled\n• Ensure file selections are valid\n• Verify configuration settings"
            elif isinstance(error, tk.TclError):
                message = f"Interface error: {str(error)}"
                suggestions = "• Try resizing the window\n• Restart the application\n• Check system display settings"
            elif isinstance(error, (OSError, PermissionError)):
                message = f"File system error: {str(error)}"
                suggestions = "• Check file permissions\n• Ensure files are not locked by other applications\n• Try running as administrator if needed"
            else:
                message = f"An unexpected error occurred: {str(error)}"
                suggestions = "• Try the operation again\n• Restart the application\n• Check the application logs for more details"
                
            if context:
                message = f"{context}: {message}"
                
            # Create enhanced error dialog with recovery options
            if show_recovery_options:
                full_message = f"{message}\n\nSuggestions:\n{suggestions}"
                
                # Add recovery options based on error type
                if self._is_recoverable_error(error):
                    full_message += "\n\nWould you like to try again?"
                    
                    result = messagebox.askyesno("Error - Recovery Available", full_message)
                    if result:
                        # User wants to retry - attempt basic recovery
                        try:
                            self._attempt_basic_recovery(error, context)
                            return
                        except Exception as recovery_error:
                            logger.error(f"Basic recovery failed: {recovery_error}")
                            messagebox.showerror("Recovery Failed", 
                                               f"Recovery attempt failed: {recovery_error}\n\nPlease try manually or restart the application.")
                else:
                    messagebox.showerror("Error", full_message)
            else:
                # Simple error display without recovery options
                messagebox.showerror("Error", message)
                
        except Exception as fallback_error:
            logger.critical(f"Fallback error handling failed: {fallback_error}")
            # Last resort - basic message
            try:
                messagebox.showerror("Critical Error", 
                                   f"Multiple errors occurred:\nOriginal: {error}\nHandler: {fallback_error}")
            except:
                print(f"CRITICAL ERROR: Original={error}, Handler={fallback_error}")
                
    def _attempt_basic_recovery(self, error: Exception, context: str):
        """
        Attempt basic recovery strategies for common errors.
        
        Args:
            error: The exception that occurred
            context: Error context
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info(f"Attempting basic recovery for {type(error).__name__} in {context}")
            
            # Recovery strategy based on error type and context
            if isinstance(error, tk.TclError) and 'panel' in context.lower():
                # GUI panel error - try to reset to file selection
                logger.info("Attempting panel recovery by resetting to file selection")
                self.current_state = WorkflowState.FILE_SELECTION
                self._show_current_panel()
                
            elif isinstance(error, (FileParsingError, InvalidFileFormatError)):
                # File error - clear file data and reset to file selection
                logger.info("Attempting file error recovery by clearing file data")
                self.workflow_data['file1_info'] = None
                self.workflow_data['file2_info'] = None
                self.workflow_data['file1_data'] = None
                self.workflow_data['file2_data'] = None
                self.current_state = WorkflowState.FILE_SELECTION
                self._show_current_panel()
                
            elif isinstance(error, ComparisonOperationError):
                # Comparison error - reset to operation config
                logger.info("Attempting comparison error recovery by resetting to operation config")
                self.current_state = WorkflowState.OPERATION_CONFIG
                self._show_current_panel()
                
            elif isinstance(error, ExportError):
                # Export error - stay on results panel
                logger.info("Export error recovery - staying on results panel")
                self.current_state = WorkflowState.RESULTS
                self._show_current_panel()
                
            else:
                # Generic recovery - reset to file selection
                logger.info("Attempting generic recovery by resetting workflow")
                self._reset_workflow_state()
                
            # Update status
            if hasattr(self.main_window, 'set_status'):
                self.main_window.set_status("Recovery completed - please try again")
                
            logger.info("Basic recovery completed successfully")
            
        except Exception as recovery_error:
            logger.error(f"Basic recovery failed: {recovery_error}")
            raise recovery_error
        
    def _handle_critical_error(self, nested_error: Exception, original_error: Exception, context: str):
        """
        Handle critical errors in error handling with comprehensive recovery options.
        
        Args:
            nested_error: The error that occurred in error handling
            original_error: The original error
            context: Error context
        """
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            # Log critical error details
            logger.critical(f"Critical error in error handling - Context: {context}")
            logger.critical(f"Original error: {original_error}")
            logger.critical(f"Handler error: {nested_error}")
            
            # Add to critical errors list
            self.critical_errors.append(f"Critical error in {context}: {nested_error} (original: {original_error})")
            
            # Attempt emergency recovery
            emergency_recovery_successful = False
            
            try:
                logger.info("Attempting emergency recovery procedures")
                
                # Emergency recovery step 1: Reset application state
                try:
                    self.current_state = WorkflowState.FILE_SELECTION
                    self.operation_cancelled = False
                    if self.progress_dialog:
                        self.progress_dialog.close()
                        self.progress_dialog = None
                    logger.debug("Application state reset completed")
                except Exception as state_error:
                    logger.error(f"State reset failed: {state_error}")
                
                # Emergency recovery step 2: Clear workflow data
                try:
                    self.workflow_data = {
                        'file1_info': None,
                        'file2_info': None,
                        'file1_data': None,
                        'file2_data': None,
                        'comparison_config': None,
                        'operation_result': None
                    }
                    logger.debug("Workflow data cleared")
                except Exception as data_error:
                    logger.error(f"Workflow data clear failed: {data_error}")
                
                # Emergency recovery step 3: Try to show minimal interface
                try:
                    if hasattr(self, 'main_window') and self.main_window:
                        # Try to show file selection panel if available
                        if (hasattr(self, 'panels') and self.panels and 
                            WorkflowState.FILE_SELECTION in self.panels):
                            self._show_current_panel()
                            logger.debug("File selection panel displayed")
                        else:
                            # Show minimal error panel
                            self._show_minimal_error_panel(
                                f"Critical error occurred: {nested_error}\n\nApplication is in recovery mode."
                            )
                            logger.debug("Minimal error panel displayed")
                        
                        # Update status
                        if hasattr(self.main_window, 'set_status'):
                            self.main_window.set_status("Critical error - application in recovery mode")
                            
                        emergency_recovery_successful = True
                        logger.info("Emergency recovery completed successfully")
                        
                except Exception as display_error:
                    logger.error(f"Emergency display recovery failed: {display_error}")
                    
            except Exception as recovery_error:
                logger.critical(f"Emergency recovery procedures failed: {recovery_error}")
            
            # Prepare user message
            critical_message = (
                f"A critical error occurred in the application:\n\n"
                f"Original Issue: {str(original_error)}\n"
                f"Recovery Error: {str(nested_error)}\n"
                f"Context: {context}\n\n"
            )
            
            if emergency_recovery_successful:
                critical_message += (
                    "Emergency recovery was successful. The application is now in a safe state.\n\n"
                    "You can try to continue using the application, but some features may not work correctly. "
                    "It is recommended to restart the application when convenient."
                )
                dialog_title = "Critical Error - Recovery Successful"
            else:
                critical_message += (
                    "Emergency recovery failed. The application may not function correctly.\n\n"
                    "Please restart the application immediately. If the problem persists, "
                    "check the application logs for more details."
                )
                dialog_title = "Critical Error - Recovery Failed"
            
            # Show error dialog with appropriate options
            try:
                if emergency_recovery_successful:
                    # Offer continue or restart options
                    result = messagebox.askyesnocancel(
                        dialog_title,
                        critical_message + "\n\nWould you like to:\nYes - Continue with recovered state\nNo - Restart application\nCancel - View error details"
                    )
                    
                    if result is False:  # No - restart
                        self._attempt_application_restart()
                    elif result is None:  # Cancel - show details
                        self._show_error_details_dialog(nested_error, original_error, context)
                    # Yes (True) - continue with current state
                    
                else:
                    # Only offer restart or details
                    result = messagebox.askyesno(
                        dialog_title,
                        critical_message + "\n\nWould you like to:\nYes - Restart application\nNo - View error details"
                    )
                    
                    if result:  # Yes - restart
                        self._attempt_application_restart()
                    else:  # No - show details
                        self._show_error_details_dialog(nested_error, original_error, context)
                        
            except Exception as dialog_error:
                logger.critical(f"Could not show critical error dialog: {dialog_error}")
                # Last resort - console output
                print(f"CRITICAL ERROR: {critical_message}")
                
        except Exception as handler_error:
            # Absolute last resort
            logger.critical(f"Critical error handler itself failed: {handler_error}")
            print(f"CRITICAL ERROR HANDLER FAILURE:")
            print(f"  Original: {original_error}")
            print(f"  Nested: {nested_error}")
            print(f"  Handler: {handler_error}")
            print(f"  Context: {context}")
            
            try:
                messagebox.showerror("System Error", 
                                   "Multiple critical errors occurred. Please restart the application immediately.")
            except:
                print("SYSTEM ERROR: Please restart the application immediately.")
                
    def _attempt_application_restart(self):
        """Attempt to restart the application gracefully."""
        logger = logging.getLogger('FileComparisonTool.MainController')
        
        try:
            logger.info("Attempting application restart")
            
            # Save any important state if needed
            # (Currently no persistent state to save)
            
            # Close current application
            if hasattr(self, 'main_window') and self.main_window:
                try:
                    self.main_window.root.quit()
                    logger.info("Application window closed for restart")
                except Exception as close_error:
                    logger.error(f"Error closing application window: {close_error}")
            
            # Note: Actual restart would require external process management
            # For now, just inform user to restart manually
            messagebox.showinfo("Restart Required", 
                              "Please restart the application manually.\n\nThe current session will now close.")
            
        except Exception as restart_error:
            logger.error(f"Application restart attempt failed: {restart_error}")
            messagebox.showerror("Restart Failed", 
                               "Could not restart automatically. Please close and restart the application manually.")
            
    def _show_error_details_dialog(self, nested_error: Exception, original_error: Exception, context: str):
        """Show detailed error information in a dialog."""
        try:
            import traceback
            
            details = (
                f"Error Details:\n\n"
                f"Context: {context}\n\n"
                f"Original Error:\n{str(original_error)}\n\n"
                f"Handler Error:\n{str(nested_error)}\n\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            
            # Create a simple text dialog (could be enhanced with scrollable text widget)
            messagebox.showinfo("Error Details", details)
            
        except Exception as details_error:
            messagebox.showerror("Error Details Failed", 
                               f"Could not display error details: {details_error}")
            
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of errors encountered during application lifecycle.
        
        Returns:
            Dict containing error summary information
        """
        return {
            'initialization_errors': self.initialization_errors.copy(),
            'critical_errors': self.critical_errors.copy(),
            'recovery_attempts': self.recovery_attempts.copy(),
            'total_errors': len(self.initialization_errors) + len(self.critical_errors),
            'has_critical_errors': len(self.critical_errors) > 0,
            'most_frequent_error': max(self.recovery_attempts.items(), key=lambda x: x[1]) if self.recovery_attempts else None
        }
            
    def run(self):
        """Start the main application."""
        try:
            self.main_window.run()
        except Exception as e:
            self._handle_error(e, "Error starting application")
            
    def cancel_operation(self):
        """Cancel the current long-running operation."""
        self.operation_cancelled = True
        
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
            
        self.main_window.show_progress(False)
        self.main_window.set_status("Operation cancelled")
        
        # Log cancellation
        if self.error_handler:
            self.error_handler.logger.info("User cancelled operation")