#!/usr/bin/env python3
"""Main user interface - no business logic, only presentation."""
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from config import COLORS, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_BUTTON, FONT_BUTTON_LARGE
from widgets import CheckboxTreeview


class MainWindow:
    """Main application window. Delegates actions to a controller."""
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        self.root.title("codeBASED")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS['background'])
        self.root.minsize(1000, 700)
        
        # Variables for UI state
        self.folder_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.output_file_var = tk.StringVar(value="codebase.txt")
        self.full_output_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to select folder")
        self.file_count_var = tk.StringVar(value="Files: 0")
        self.progress_var = tk.DoubleVar()
        
        # Configure root grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # These will be built in build_ui()
        self.main_container = None
        self.tree = None
        self.vsb = None
        self.hsb = None
        self.cancel_btn = None
        self.select_folder_btn = None
        self.refresh_btn = None
        self.check_all_btn = None
        self.uncheck_all_btn = None
        self.compile_btn = None
        self.select_output_btn = None
        self.progress_frame = None
        self.progress_bar = None
        self.status_label = None
        self.file_count_label = None
        self.right_status_container = None
        
        # Window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)
    
    def build_ui(self):
        """Build the UI after controller is set."""
        self._build_ui()
        self._configure_styles()
        self._setup_bindings()
        self.center_window()
    
    def _build_ui(self):
        """Construct all UI elements."""
        # Main container
        self.main_container = tk.Frame(self.root, bg=COLORS['background'])
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        for i in range(8):
            self.main_container.grid_rowconfigure(i, weight=[0, 0, 1, 0, 0, 0, 0, 0][i])
        
        # Header
        self.header_frame = tk.Frame(self.main_container, bg=COLORS['background'])
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        tk.Label(self.header_frame, text="codeBASED", font=FONT_TITLE,
                 bg=COLORS['background'], fg=COLORS['accent']).pack()
        tk.Label(self.header_frame, text="Compile your codebase into a single, organized file",
                 font=FONT_SUBTITLE, bg=COLORS['background'], fg=COLORS['text_secondary']).pack(pady=(5, 0))
        
        # Source folder section
        self.source_frame = tk.Frame(self.main_container, bg=COLORS['surface'], height=60)
        self.source_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.source_frame.grid_propagate(False)
        self.source_frame.grid_rowconfigure(0, weight=1)
        self.source_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(self.source_frame, text="Source Folder:", font=FONT_HEADING,
                 bg=COLORS['surface'], fg=COLORS['accent'], anchor='w'
                 ).grid(row=0, column=0, sticky="w", padx=15, pady=0)
        
        self.folder_entry = tk.Entry(self.source_frame, textvariable=self.folder_path_var,
                                     font=FONT_BODY, bg=COLORS['divider'], fg=COLORS['accent'],
                                     insertbackground=COLORS['accent'], relief=tk.FLAT, highlightthickness=0)
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=0, ipady=8)
        
        self.select_folder_btn = tk.Button(self.source_frame, text="Select Folder", font=FONT_BUTTON,
                                           bg=COLORS['primary'], fg=COLORS['background'],
                                           activebackground=COLORS['secondary'], relief=tk.FLAT,
                                           cursor='hand2', command=self.controller.select_folder)
        self.select_folder_btn.grid(row=0, column=2, padx=(0, 15), pady=0, ipadx=15, ipady=6)
        
        # Tree container
        self.tree_container = tk.Frame(self.main_container, bg=COLORS['surface'])
        self.tree_container.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)
        
        tree_inner = tk.Frame(self.tree_container, bg=COLORS['surface'])
        tree_inner.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        tree_inner.grid_rowconfigure(0, weight=1)
        tree_inner.grid_columnconfigure(0, weight=1)
        
        self.vsb = ttk.Scrollbar(tree_inner, orient="vertical")
        self.hsb = ttk.Scrollbar(tree_inner, orient="horizontal")
        
        self.tree = CheckboxTreeview(tree_inner, columns=("path", "size", "modified"),
                                     show="tree headings", yscrollcommand=self.vsb.set,
                                     xscrollcommand=self.hsb.set)
        self._configure_tree_columns()
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.vsb.config(command=self.tree.yview)
        self.hsb.config(command=self.tree.xview)
        
        # Status bar
        self.status_bar = tk.Frame(self.tree_container, bg=COLORS['surface'], height=30)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.status_bar.grid_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, textvariable=self.status_var,
                                     font=FONT_SMALL, bg=COLORS['surface'], fg=COLORS['text_secondary'],
                                     anchor='w')
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_status_container = tk.Frame(self.status_bar, bg=COLORS['surface'])
        self.right_status_container.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_count_label = tk.Label(self.right_status_container, textvariable=self.file_count_var,
                                         font=('Segoe UI', 9, 'bold'), bg=COLORS['surface'],
                                         fg=COLORS['accent'])
        self.file_count_label.pack(side=tk.RIGHT, padx=(0, 0))
        
        self.cancel_btn = tk.Button(self.right_status_container, text="Cancel Loading",
                                    font=FONT_SMALL, bg=COLORS['stop'], fg='white',
                                    activebackground='#A32E2E', relief=tk.FLAT, cursor='hand2',
                                    command=self.controller.cancel_loading)
        
        # Output settings
        self.output_frame = tk.Frame(self.main_container, bg=COLORS['surface'], height=120)
        self.output_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.output_frame.grid_propagate(False)
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.output_frame.grid_rowconfigure(2, weight=1)
        self.output_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(self.output_frame, text="Output Directory:", font=FONT_HEADING,
                 bg=COLORS['surface'], fg=COLORS['accent'], anchor='w'
                 ).grid(row=0, column=0, sticky="w", padx=15, pady=5)
        
        output_dir_entry = tk.Entry(self.output_frame, textvariable=self.output_dir_var,
                                    font=FONT_BODY, bg=COLORS['divider'], fg=COLORS['accent'],
                                    insertbackground=COLORS['accent'], relief=tk.FLAT, highlightthickness=0)
        output_dir_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5, ipady=6)
        
        self.select_output_btn = tk.Button(self.output_frame, text="Select", font=FONT_BUTTON,
                                           bg=COLORS['primary'], fg=COLORS['background'],
                                           activebackground=COLORS['secondary'], relief=tk.FLAT,
                                           cursor='hand2', command=self.controller.select_output_dir)
        self.select_output_btn.grid(row=0, column=2, padx=(0, 15), pady=5, ipadx=10, ipady=4)
        
        tk.Label(self.output_frame, text="Output Filename:", font=FONT_HEADING,
                 bg=COLORS['surface'], fg=COLORS['accent'], anchor='w'
                 ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        output_file_entry = tk.Entry(self.output_frame, textvariable=self.output_file_var,
                                     font=FONT_BODY, bg=COLORS['divider'], fg=COLORS['accent'],
                                     insertbackground=COLORS['accent'], relief=tk.FLAT, highlightthickness=0)
        output_file_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5, ipady=6)
        output_file_entry.bind('<KeyRelease>', self.controller.update_full_output_path)
        
        self.path_display = tk.Label(self.output_frame, textvariable=self.full_output_path_var,
                                     font=FONT_SMALL, bg=COLORS['surface'], fg=COLORS['text_secondary'])
        self.path_display.grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=5)
        
        # Action buttons
        self.buttons_frame = tk.Frame(self.main_container, bg=COLORS['background'], height=65)
        self.buttons_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        self.buttons_frame.grid_propagate(False)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=0)
        
        left_container = tk.Frame(self.buttons_frame, bg=COLORS['background'])
        left_container.grid(row=0, column=0, sticky="w", padx=(0, 20))
        right_container = tk.Frame(self.buttons_frame, bg=COLORS['background'])
        right_container.grid(row=0, column=1, sticky="e")
        
        control_frame = tk.Frame(left_container, bg=COLORS['background'])
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(8, 0))
        
        self.refresh_btn = tk.Button(control_frame, text="Refresh", font=FONT_BUTTON,
                                     bg=COLORS['divider'], fg=COLORS['accent'],
                                     activebackground=COLORS['secondary'], relief=tk.FLAT,
                                     cursor='hand2', command=self.controller.refresh_tree)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=6)
        
        self.check_all_btn = tk.Button(control_frame, text="Check All", font=FONT_BUTTON,
                                       bg=COLORS['divider'], fg=COLORS['accent'],
                                       activebackground=COLORS['secondary'], relief=tk.FLAT,
                                       cursor='hand2', command=self.controller.check_all)
        self.check_all_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=6)
        
        self.uncheck_all_btn = tk.Button(control_frame, text="Uncheck All", font=FONT_BUTTON,
                                         bg=COLORS['divider'], fg=COLORS['accent'],
                                         activebackground=COLORS['secondary'], relief=tk.FLAT,
                                         cursor='hand2', command=self.controller.uncheck_all)
        self.uncheck_all_btn.pack(side=tk.LEFT, ipadx=15, ipady=6)
        
        compile_frame = tk.Frame(right_container, bg=COLORS['background'])
        compile_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(8, 2))
        
        self.compile_btn = tk.Button(compile_frame, text="Compile Selected Files", font=FONT_BUTTON_LARGE,
                                     bg=COLORS['primary'], fg=COLORS['background'],
                                     activebackground=COLORS['secondary'], relief=tk.FLAT,
                                     cursor='hand2', command=self.controller.compile_selected)
        self.compile_btn.pack(side=tk.RIGHT, ipadx=30, ipady=8)
        
        # Progress bar
        self.progress_frame = tk.Frame(self.main_container, bg=COLORS['background'], height=30)
        self.progress_frame.grid(row=5, column=0, sticky="ew")
        self.progress_frame.grid_propagate(False)
        progress_inner = tk.Frame(self.progress_frame, bg=COLORS['background'])
        progress_inner.place(relx=0.5, rely=0.5, anchor='center', relwidth=1.0)
        self.progress_bar = ttk.Progressbar(progress_inner, variable=self.progress_var,
                                            mode='determinate', length=100)
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.progress_frame.grid_remove()
    
    def _configure_tree_columns(self):
        """Configure treeview columns."""
        self.tree.tag_configure('folder', foreground=COLORS['secondary'])
        self.tree.tag_configure('file', foreground=COLORS['accent'])
        self.tree.tag_configure('evenrow', background=COLORS['divider'])
        self.tree.tag_configure('oddrow', background=COLORS['surface'])
        
        self.tree.heading("#0", text="File/Folder", anchor=tk.W)
        self.tree.heading("path", text="Path", anchor=tk.W)
        self.tree.heading("size", text="Size", anchor=tk.E)
        self.tree.heading("modified", text="Last Modified", anchor=tk.W)
        
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("path", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=80, anchor=tk.E)
        self.tree.column("modified", width=150, minwidth=120)
    
    def _configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=COLORS['divider'], foreground=COLORS['accent'],
                        fieldbackground=COLORS['divider'], borderwidth=0, font=FONT_BODY)
        style.configure("Treeview.Heading", background=COLORS['surface'], foreground=COLORS['accent'],
                        relief=tk.FLAT, font=('Segoe UI', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', COLORS['primary'])])
        style.configure("Vertical.TScrollbar", background=COLORS['surface'],
                        troughcolor=COLORS['divider'], bordercolor=COLORS['surface'],
                        arrowcolor=COLORS['accent'])
        style.configure("Horizontal.TScrollbar", background=COLORS['surface'],
                        troughcolor=COLORS['divider'], bordercolor=COLORS['surface'],
                        arrowcolor=COLORS['accent'])
        style.configure("TProgressbar", background=COLORS['secondary'],
                        troughcolor=COLORS['divider'], bordercolor=COLORS['surface'])
    
    def _setup_bindings(self):
        """Bind window events."""
        self.root.bind('<Configure>', self._on_window_resize)
    
    def _on_window_resize(self, event):
        if hasattr(self, 'tree') and self.tree.winfo_width() > 100:
            width = self.tree.winfo_width()
            self.tree.column("#0", width=int(width * 0.4))
            self.tree.column("path", width=int(width * 0.35))
    
    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    # --- Public UI update methods ---
    def set_status(self, text: str, is_error: bool = False):
        self.status_var.set(text)
        self.status_label.config(fg=COLORS['error'] if is_error else COLORS['text_secondary'])
    
    def set_file_count(self, folders: int, files: int):
        self.file_count_var.set(f"📁 {folders} folders | 📄 {files} files")
    
    def show_loading_state(self, message: str):
        self.status_var.set(message)
        self.file_count_label.pack_forget()
        self.cancel_btn.pack(side=tk.RIGHT, padx=(10, 0), ipadx=10, ipady=2)
    
    def show_normal_state(self):
        self.cancel_btn.pack_forget()
        self.file_count_label.pack(side=tk.RIGHT, padx=(0, 0))
    
    def set_buttons_state(self, enabled: bool):
        state = 'normal' if enabled else 'disabled'
        self.select_folder_btn.config(state=state)
        self.refresh_btn.config(state=state)
        self.check_all_btn.config(state=state)
        self.uncheck_all_btn.config(state=state)
        self.compile_btn.config(state=state)
        self.select_output_btn.config(state=state)
    
    def show_progress(self, value: float):
        if value <= 0:
            self.progress_frame.grid()
        self.progress_var.set(value)
        if value >= 100:
            self.progress_frame.grid_remove()
    
    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_tree_item(self, item_id: str, parent_id: str, text: str, values: tuple, tags: tuple):
        self.tree.insert(parent_id, "end", iid=item_id, text=text, values=values, tags=tags)
    
    def get_checked_items(self):
        return self.tree.get_checked_items()
    
    def check_all(self):
        for item in self.tree.get_children():
            self._check_recursive(item)
    
    def _check_recursive(self, item_id):
        self.tree.item(item_id, tags=("checked",))
        for child in self.tree.get_children(item_id):
            self._check_recursive(child)
    
    def uncheck_all(self):
        for item in self.tree.get_children():
            self._uncheck_recursive(item)
    
    def _uncheck_recursive(self, item_id):
        self.tree.item(item_id, tags=("unchecked",))
        for child in self.tree.get_children(item_id):
            self._uncheck_recursive(child)
    
    def get_output_settings(self):
        return self.output_dir_var.get().strip(), self.output_file_var.get().strip()
    
    def set_output_directory(self, path: str):
        self.output_dir_var.set(path)
    
    def set_output_filename(self, name: str):
        self.output_file_var.set(name)
    
    def set_full_output_path_display(self, full_path: str):
        self.full_output_path_var.set(f"Output will be saved to: {full_path}")
    
    def set_source_folder(self, path: str):
        self.folder_path_var.set(path)
    
    def get_source_folder(self) -> str:
        return self.folder_path_var.get()