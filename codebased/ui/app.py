
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import queue
import time
import os
from pathlib import Path

from ..config import THEME_COLORS
from ..core.scanner import FileScanner
from ..core.compiler import CodebaseCompiler
from .widgets import CheckboxTreeview
from .dialogs import InfoDialog, WarningDialog, ErrorDialog, ConfirmDialog

class CodebaseCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("codeBASED")
        self.root.geometry("1200x800")
        
        # Theme
        self.colors = THEME_COLORS
        
        # Thread management
        self.loading_thread = None
        self.is_loading = False
        self.scanner = None
        
        # Queue for communication between threads
        self.queue = queue.Queue()
        
        # Initialize Core components
        self.scanner = FileScanner(self.queue)
        self.compiler = CodebaseCompiler(self.queue)

        # Configure root window
        self.root.configure(bg=self.colors['background'])
        self.root.minsize(1000, 700)
        
        # Configure grid for responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main container with grid
        self.main_container = tk.Frame(root, bg=self.colors['background'])
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Configure rows for proper scaling
        for i in range(8):
            self.main_container.grid_rowconfigure(i, weight=[0, 0, 1, 0, 0, 0, 0, 0][i])
        
        self._build_ui()
        
        # Start queue processing
        self.root.after(100, self.process_queue)

        self.current_folder = None
        self.file_items = {}
        self.output_dir = None

        # Initialize default output directory
        self.update_full_output_path()
        
        # Bind window resize
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Center window
        self.center_window()
        
        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        """Build the user interface elements."""
        # Header
        self.header_frame = tk.Frame(self.main_container, bg=self.colors['background'])
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Main title
        self.title_label = tk.Label(
            self.header_frame,
            text="codeBASED",
            font=('Segoe UI', 36, 'bold'),
            bg=self.colors['background'],
            fg=self.colors['accent']
        )
        self.title_label.pack()
        
        # Subtitle
        self.subtitle_label = tk.Label(
            self.header_frame,
            text="Compile your codebase into a single, organized file",
            font=('Segoe UI', 14),
            bg=self.colors['background'],
            fg=self.colors['text_secondary']
        )
        self.subtitle_label.pack(pady=(5, 0))
        
        # Source folder section - FIXED HEIGHT WITH VERTICALLY CENTERED CONTENT
        self.source_frame = tk.Frame(self.main_container, bg=self.colors['surface'], height=60)
        self.source_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.source_frame.grid_propagate(False)  # Prevents shrinking
        self.source_frame.grid_rowconfigure(0, weight=1)  # Center vertically
        self.source_frame.grid_columnconfigure(1, weight=1)
        
        # Label - vertically centered
        tk.Label(
            self.source_frame,
            text="Source Folder:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent'],
            anchor='w'
        ).grid(row=0, column=0, sticky="w", padx=15, pady=0)
        
        # Entry field - vertically centered
        self.folder_path_var = tk.StringVar()
        self.folder_entry = tk.Entry(
            self.source_frame,
            textvariable=self.folder_path_var,
            font=('Segoe UI', 10),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=0, ipady=8)
        
        # Button - vertically centered
        self.select_folder_btn = tk.Button(
            self.source_frame,
            text="Select Folder",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.select_folder
        )
        self.select_folder_btn.grid(row=0, column=2, padx=(0, 15), pady=0, ipadx=15, ipady=6)
        
        # File tree section
        self.tree_container = tk.Frame(self.main_container, bg=self.colors['surface'])
        self.tree_container.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)
        
        # Treeview frame
        tree_inner_frame = tk.Frame(self.tree_container, bg=self.colors['surface'])
        tree_inner_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        tree_inner_frame.grid_rowconfigure(0, weight=1)
        tree_inner_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollbars
        self.vsb = ttk.Scrollbar(tree_inner_frame, orient="vertical")
        self.hsb = ttk.Scrollbar(tree_inner_frame, orient="horizontal")
        
        # Create checkbox treeview
        self.tree = CheckboxTreeview(
            tree_inner_frame,
            columns=("path", "size", "modified"),
            show="tree headings",
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set
        )
        
        # Configure treeview style
        self._configure_tree_style()
        
        # Configure treeview columns
        self.tree.heading("#0", text="File/Folder", anchor=tk.W)
        self.tree.heading("path", text="Path", anchor=tk.W)
        self.tree.heading("size", text="Size", anchor=tk.E)
        self.tree.heading("modified", text="Last Modified", anchor=tk.W)
        
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("path", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=80, anchor=tk.E)
        self.tree.column("modified", width=150, minwidth=120)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        
        self.vsb.config(command=self.tree.yview)
        self.hsb.config(command=self.tree.xview)
        
        # Merged status bar frame
        self.status_bar = tk.Frame(self.tree_container, bg=self.colors['surface'], height=30)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.status_bar.grid_propagate(False)
        
        # Left side: Status text
        self.status_var = tk.StringVar(value="Ready to select folder")
        self.status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg=self.colors['surface'],
            fg=self.colors['text_secondary'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right side container
        self.right_status_container = tk.Frame(self.status_bar, bg=self.colors['surface'])
        self.right_status_container.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File count label (shown when not loading)
        self.file_count_var = tk.StringVar(value="Files: 0")
        self.file_count_label = tk.Label(
            self.right_status_container,
            textvariable=self.file_count_var,
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent']
        )
        self.file_count_label.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Cancel loading button
        self.cancel_btn = tk.Button(
            self.right_status_container,
            text="Cancel Loading",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['stop'],
            fg='white',
            activebackground='#A32E2E',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.cancel_loading
        )
        
        # Output settings section - FIXED HEIGHT WITH VERTICALLY CENTERED CONTENT
        self.output_frame = tk.Frame(self.main_container, bg=self.colors['surface'], height=120)
        self.output_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.output_frame.grid_propagate(False)
        
        # Configure rows for vertical centering in output frame
        self.output_frame.grid_rowconfigure(0, weight=1)  # Output directory row
        self.output_frame.grid_rowconfigure(1, weight=1)  # Filename row
        self.output_frame.grid_rowconfigure(2, weight=1)  # Path display row
        self.output_frame.grid_columnconfigure(1, weight=1)
        
        # Output directory - vertically centered
        tk.Label(
            self.output_frame,
            text="Output Directory:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent'],
            anchor='w'
        ).grid(row=0, column=0, sticky="w", padx=15, pady=5)
        
        self.output_dir_var = tk.StringVar()
        output_dir_entry = tk.Entry(
            self.output_frame,
            textvariable=self.output_dir_var,
            font=('Segoe UI', 10),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        output_dir_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5, ipady=6)
        
        self.select_output_btn = tk.Button(
            self.output_frame,
            text="Select",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.select_output_dir
        )
        self.select_output_btn.grid(row=0, column=2, padx=(0, 15), pady=5, ipadx=10, ipady=4)
        
        # Output filename - vertically centered
        tk.Label(
            self.output_frame,
            text="Output Filename:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent'],
            anchor='w'
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.output_file_var = tk.StringVar(value="codebase.txt")
        output_file_entry = tk.Entry(
            self.output_frame,
            textvariable=self.output_file_var,
            font=('Segoe UI', 10),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        output_file_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5, ipady=6)
        output_file_entry.bind('<KeyRelease>', self.update_full_output_path)
        
        # Full path display - vertically centered
        self.full_output_path_var = tk.StringVar()
        self.path_display = tk.Label(
            self.output_frame,
            textvariable=self.full_output_path_var,
            font=('Segoe UI', 9),
            bg=self.colors['surface'],
            fg=self.colors['text_secondary']
        )
        self.path_display.grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=5)
        
        # Action buttons section
        self.buttons_frame = tk.Frame(self.main_container, bg=self.colors['background'], height=65)
        self.buttons_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        self.buttons_frame.grid_propagate(False)
        
        self.buttons_frame.grid_columnconfigure(0, weight=1)  # Left side
        self.buttons_frame.grid_columnconfigure(1, weight=0)  # Right side (fixed width)
        
        # Left side container for control buttons
        left_buttons_container = tk.Frame(self.buttons_frame, bg=self.colors['background'])
        left_buttons_container.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        # Right side container for compile button
        right_buttons_container = tk.Frame(self.buttons_frame, bg=self.colors['background'])
        right_buttons_container.grid(row=0, column=1, sticky="e")
        
        # Control buttons (left side)
        control_buttons_frame = tk.Frame(left_buttons_container, bg=self.colors['background'])
        control_buttons_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(8, 0))
        
        self.refresh_btn = tk.Button(
            control_buttons_frame,
            text="Refresh",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.refresh_tree,
            state='normal'
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=6)
        
        self.check_all_btn = tk.Button(
            control_buttons_frame,
            text="Check All",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.check_all,
            state='normal'
        )
        self.check_all_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=6)
        
        self.uncheck_all_btn = tk.Button(
            control_buttons_frame,
            text="Uncheck All",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.uncheck_all,
            state='normal'
        )
        self.uncheck_all_btn.pack(side=tk.LEFT, ipadx=15, ipady=6)
        
        # Main compile button (right side)
        compile_button_frame = tk.Frame(right_buttons_container, bg=self.colors['background'])
        compile_button_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(8, 2))
        
        self.compile_btn = tk.Button(
            compile_button_frame,
            text="Compile Selected Files",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.compile_selected,
            state='normal'
        )
        self.compile_btn.pack(side=tk.RIGHT, ipadx=30, ipady=8)
        
        # Progress bar section
        self.progress_frame = tk.Frame(self.main_container, bg=self.colors['background'], height=30)
        self.progress_frame.grid(row=5, column=0, sticky="ew")
        self.progress_frame.grid_propagate(False)
        
        # Center progress bar vertically
        progress_inner = tk.Frame(self.progress_frame, bg=self.colors['background'])
        progress_inner.place(relx=0.5, rely=0.5, anchor='center', relwidth=1.0)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_inner,
            variable=self.progress_var,
            mode='determinate',
            length=100
        )
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.progress_frame.grid_remove()
        
        # Configure styles
        self._configure_styles()

    def _configure_styles(self):
        """Configure ttk styles with custom colors."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview
        style.configure("Treeview",
                       background=self.colors['divider'],
                       foreground=self.colors['accent'],
                       fieldbackground=self.colors['divider'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure("Treeview.Heading",
                       background=self.colors['surface'],
                       foreground=self.colors['accent'],
                       relief=tk.FLAT,
                       font=('Segoe UI', 10, 'bold'))
        
        style.map("Treeview.Heading",
                 background=[('active', self.colors['primary'])])
        
        # Configure scrollbars
        style.configure("Vertical.TScrollbar",
                       background=self.colors['surface'],
                       troughcolor=self.colors['divider'],
                       bordercolor=self.colors['surface'],
                       arrowcolor=self.colors['accent'])
        
        style.configure("Horizontal.TScrollbar",
                       background=self.colors['surface'],
                       troughcolor=self.colors['divider'],
                       bordercolor=self.colors['surface'],
                       arrowcolor=self.colors['accent'])
        
        # Configure progress bar
        style.configure("TProgressbar",
                       background=self.colors['secondary'],
                       troughcolor=self.colors['divider'],
                       bordercolor=self.colors['surface'])

    def _configure_tree_style(self):
        """Configure treeview item colors."""
        self.tree.tag_configure('folder', foreground=self.colors['secondary'])
        self.tree.tag_configure('file', foreground=self.colors['accent'])
        
        # Configure alternating row colors
        self.tree.tag_configure('evenrow', background=self.colors['divider'])
        self.tree.tag_configure('oddrow', background=self.colors['surface'])

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _on_window_resize(self, event):
        """Handle window resize events."""
        # Update column widths on resize
        if hasattr(self, 'tree'):
            tree_width = self.tree.winfo_width()
            if tree_width > 100:
                # Adjust column proportions
                self.tree.column("#0", width=int(tree_width * 0.4))
                self.tree.column("path", width=int(tree_width * 0.35))

    def select_folder(self):
        """Open folder selection dialog and load tree asynchronously."""
        # First, cancel any ongoing loading
        self.cancel_loading()
        
        folder_path = filedialog.askdirectory(title="Select Codebase Folder")
        if folder_path:
            self.folder_path_var.set(folder_path)
            self.current_folder = Path(folder_path)
            
            # Set default output directory to the selected folder
            self.output_dir_var.set(str(folder_path))
            self.output_dir = Path(folder_path)
            self.update_full_output_path()
            
            # Load tree asynchronously
            self.load_tree_async()

    def select_output_dir(self):
        """Open output directory selection dialog."""
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if output_dir:
            self.output_dir_var.set(output_dir)
            self.output_dir = Path(output_dir)
            self.update_full_output_path()

    def update_full_output_path(self, event=None):
        """Update the full output path display."""
        output_dir = self.output_dir_var.get().strip()
        output_file = self.output_file_var.get().strip()
        
        if not output_file:
            output_file = "codebase.txt"
            self.output_file_var.set(output_file)
        
        if output_dir and os.path.isdir(output_dir):
            full_path = os.path.join(output_dir, output_file)
            self.full_output_path_var.set(f"Output will be saved to: {full_path}")
        else:
            self.full_output_path_var.set("Please select a valid output directory")

    def load_tree_async(self):
        """Load files and folders into the treeview asynchronously."""
        if not self.current_folder or not self.current_folder.exists():
            self.show_error_dialog("Error", "Invalid folder path")
            return

        # Clear existing tree
        self.clear_tree()
        
        # Show loading state in status bar
        self.show_loading_state("Scanning directory...")
        
        # Set loading flag
        self.is_loading = True
        
        # Disable buttons during loading
        self.set_buttons_state('disabled')
        
        # Start loading in a separate thread
        # Reset scanner stop flag
        self.scanner.stop_flag = False
        
        self.loading_thread = threading.Thread(
            target=self.scanner.scan_directory,
            args=(self.current_folder,),
            daemon=True
        )
        self.loading_thread.start()

    def clear_tree(self):
        """Clear the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_items.clear()

    def show_loading_state(self, message):
        """Show loading state in the status bar."""
        # Update status text
        self.status_var.set(message)
        
        # Hide file count label
        self.file_count_label.pack_forget()
        
        # Show cancel button
        self.cancel_btn.pack(side=tk.RIGHT, padx=(10, 0), ipadx=10, ipady=2)

    def show_normal_state(self):
        """Show normal state in the status bar (not loading)."""
        # Hide cancel button
        self.cancel_btn.pack_forget()
        
        # Show file count label
        self.file_count_label.pack(side=tk.RIGHT, padx=(0, 0))

    def cancel_loading(self):
        """Cancel the current loading operation."""
        if self.is_loading:
            self.scanner.cancel()
            self.is_loading = False
            # The queue will receive 'loading_cancelled' which will handle the UI update

    def set_buttons_state(self, state):
        """Enable or disable control buttons."""
        state_normal = 'normal' if state == 'normal' else 'disabled'
        self.select_folder_btn.config(state=state_normal)
        self.refresh_btn.config(state=state_normal)
        self.check_all_btn.config(state=state_normal)
        self.uncheck_all_btn.config(state=state_normal)
        self.compile_btn.config(state=state_normal)
        self.select_output_btn.config(state=state_normal)

    def process_queue(self):
        """Process messages from worker threads."""
        try:
            while True:
                msg_type, message = self.queue.get_nowait()
                
                if msg_type == 'add_item':
                    # Add item to treeview
                    item_data = message
                    self.tree.insert(
                        item_data['parent_id'], 
                        "end", 
                        iid=item_data['item_id'],
                        text=item_data['text'],
                        values=item_data['values'],
                        tags=item_data['tags']
                    )
                    
                    # Store in file_items
                    self.file_items[item_data['item_id']] = {
                        'path': item_data['path'],
                        'is_dir': item_data['is_dir'],
                        'relative_path': item_data['relative_path']
                    }
                    
                elif msg_type == 'loading_progress':
                    # Update status text with loading progress
                    self.status_var.set(message)
                    
                elif msg_type == 'loading_complete':
                    self.is_loading = False
                    # Get file items from message if provided, though we were building incrementally
                    # The message content is the full dict, but we already populated self.file_items incrementally?
                    # Wait, the scanner sends `file_items` at the end.
                    # But the scanner ALSO sends `add_item` individually.
                    # Let's check the scanner code. 
                    # Scanner sends 'add_item' for each item. And finally 'loading_complete' with `file_items`.
                    # The `file_items` in scanner contains nothing because I modified it to not store locally.
                    # Ah, wait. I removed the local storage in `scan_directory` in my previous step?
                    # Let's check scanner.py.
                    # Yes, `file_items = {}` is defined but never populated in `scan_directory` loop.
                    # It just sends `add_item`.
                    # So 'loading_complete' message will contain an empty dict. That's fine, we populated `self.file_items` here in `add_item` block.
                    
                    self.show_normal_state()
                    self.set_buttons_state('normal')
                    self.update_file_count()
                    # Update the status text
                    self.status_var.set(f"Loaded folder: {self.current_folder.name}")
                    
                elif msg_type == 'loading_cancelled':
                    self.is_loading = False
                    self.show_normal_state()
                    self.set_buttons_state('normal')
                    # Update the status text
                    self.status_var.set("Loading cancelled")
                    
                elif msg_type == 'loading_error':
                    self.is_loading = False
                    self.show_normal_state()
                    self.set_buttons_state('normal')
                    self.root.after(0, lambda: self.show_error_dialog("Error", f"Failed to load folder: {message}"))
                    # Update the status text
                    self.status_var.set("Error loading folder")
                    
                elif msg_type == 'loading_warning':
                    print(f"Warning: {message}")
                    
                elif msg_type == 'status':
                    self.status_var.set(message)
                    
                elif msg_type == 'progress':
                    self.progress_var.set(message)
                    
                elif msg_type == 'progress_complete':
                    self.progress_frame.grid_remove()
                    
                elif msg_type == 'success':
                    self.status_var.set(message)
                    self.status_label.config(fg=self.colors['success'])
                    # Show success dialog
                    # We need details for the success dialog.
                    # Ideally the message should be a dict or object. 
                    # For now, let's construct a simple message.
                    # We can fetch file size from the path.
                    full_output_path = os.path.join(self.output_dir_var.get().strip(), self.output_file_var.get().strip())
                    if os.path.exists(full_output_path):
                         # format_size is in helpers, simpler to just import or re-read
                         from ..utils.helpers import format_size
                         size_str = format_size(os.path.getsize(full_output_path))
                         
                         self.root.after(0, lambda: self.show_info_dialog(
                            "Success!",
                            f"Compilation completed successfully!\n\n"
                            f"Output file: {full_output_path}\n"
                            f"Output size: {size_str}",
                            "Your codebase is ready for review!"
                        ))
                    
                elif msg_type == 'error':
                    self.status_var.set(message)
                    self.status_label.config(fg=self.colors['error'])
                    self.root.after(0, lambda: self.show_warning_dialog(
                        "Compilation Issue",
                        message
                    ))
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self.process_queue)

    def refresh_tree(self):
        """Refresh the treeview with current folder."""
        if self.current_folder and not self.is_loading:
            self.load_tree_async()

    def update_file_count(self):
        """Update the file count display."""
        file_count = sum(1 for item in self.file_items.values() if not item['is_dir'])
        folder_count = sum(1 for item in self.file_items.values() if item['is_dir'])
        self.file_count_var.set(f"📁 {folder_count} folders | 📄 {file_count} files")

    def check_all(self):
        """Check all items in the tree."""
        if self.is_loading:
            return
            
        def check_recursive(item_id):
            self.tree.item(item_id, tags=("checked",))
            for child in self.tree.get_children(item_id):
                check_recursive(child)

        for item in self.tree.get_children():
            check_recursive(item)

    def uncheck_all(self):
        """Uncheck all items in the tree."""
        if self.is_loading:
            return
            
        def uncheck_recursive(item_id):
            self.tree.item(item_id, tags=("unchecked",))
            for child in self.tree.get_children(item_id):
                uncheck_recursive(child)

        for item in self.tree.get_children():
            uncheck_recursive(item)

    def compile_selected(self):
        """Compile selected files into a single text file."""
        if self.is_loading:
            self.show_warning_dialog("Please Wait", "Cannot compile while loading files.")
            return
            
        checked_items = self.tree.get_checked_items()
        selected_files = [self.file_items[item_id]['path']
                         for item_id in checked_items
                         if not self.file_items[item_id]['is_dir']]

        if not selected_files:
            self.show_warning_dialog("No Files Selected", 
                                   "Please select at least one file to compile.")
            return

        # Get output directory and file
        output_dir = self.output_dir_var.get().strip()
        output_file = self.output_file_var.get().strip()
        
        if not output_dir or not os.path.isdir(output_dir):
            self.show_error_dialog("Error", "Please select a valid output directory")
            return
        
        if not output_file:
            output_file = "codebase.txt"
            self.output_file_var.set(output_file)
        
        full_output_path = os.path.join(output_dir, output_file)

        # Ask for confirmation using custom dialog
        confirm_dialog = ConfirmDialog(
            self.root,
            self.colors,
            "Confirm Compilation",
            f"📦 You are about to compile {len(selected_files)} files\n\n"
            f"📁 Output: {full_output_path}\n"
            f"📄 Files selected: {len(selected_files)}"
        )
        
        confirm = confirm_dialog.show()
        if not confirm:
            return

        # Show progress bar
        self.progress_frame.grid()
        self.progress_var.set(0)
        
        # Start compilation in a separate thread
        threading.Thread(target=self.compiler.compile_files, 
                        args=(selected_files, full_output_path, self.current_folder), 
                        daemon=True).start()

    # Custom dialog helper methods
    def show_info_dialog(self, title, message, details=None):
        """Show a custom information dialog."""
        dialog = InfoDialog(self.root, self.colors, title, message, details)
        dialog.show()
        
    def show_warning_dialog(self, title, message, details=None):
        """Show a custom warning dialog."""
        dialog = WarningDialog(self.root, self.colors, title, message, details)
        dialog.show()
        
    def show_error_dialog(self, title, message, details=None):
        """Show a custom error dialog."""
        dialog = ErrorDialog(self.root, self.colors, title, message, details)
        dialog.show()
        
    def show_confirm_dialog(self, title, message, details=None):
        """Show a custom confirmation dialog."""
        dialog = ConfirmDialog(self.root, self.colors, title, message, details)
        return dialog.show()
        
    def on_closing(self):
        """Handle window closing."""
        self.cancel_loading()
        self.root.destroy()
