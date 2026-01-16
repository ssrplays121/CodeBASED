#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import queue
import time

class CheckboxTreeview(ttk.Treeview):
    """Custom Treeview with checkboxes."""
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        # Create checkbox images
        self._create_checkbox_images()

        # Configure tags for checked/unchecked states
        self.tag_configure("checked", image=self.checked_icon)
        self.tag_configure("unchecked", image=self.unchecked_icon)
        self.tag_configure("mixed", image=self.mixed_icon)

        # Bind click events
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Double-1>", self._handle_double_click)

    def _create_checkbox_images(self):
        """Create checkbox images using canvas."""
        # Create checked icon with custom color
        self.checked_icon = tk.PhotoImage(width=18, height=18)
        # Draw rounded rectangle background
        for x in range(18):
            for y in range(18):
                if 2 <= x <= 15 and 2 <= y <= 15:
                    # Create rounded effect
                    if (x < 4 or x > 13) and (y < 4 or y > 13):
                        self.checked_icon.put("#EBD5AB", (x, y))  # Match background
                    else:
                        self.checked_icon.put("#8BAE66", (x, y))
        
        # Draw check mark
        check_points = [(4, 8), (7, 11), (12, 4), (13, 5), (7, 13), (3, 9)]
        for i in range(len(check_points)-1):
            x1, y1 = check_points[i]
            x2, y2 = check_points[i+1]
            for x in range(min(x1, x2), max(x1, x2)+1):
                for y in range(min(y1, y2), max(y1, y2)+1):
                    self.checked_icon.put("#1B211A", (x, y))

        # Create unchecked icon
        self.unchecked_icon = tk.PhotoImage(width=18, height=18)
        # Draw border
        for x in range(18):
            for y in range(18):
                if 2 <= x <= 15 and 2 <= y <= 15:
                    if x == 2 or x == 15 or y == 2 or y == 15:
                        self.unchecked_icon.put("#628141", (x, y))
                    else:
                        self.unchecked_icon.put("#EBD5AB", (x, y))

        # Create mixed state icon
        self.mixed_icon = tk.PhotoImage(width=18, height=18)
        # Draw border
        for x in range(18):
            for y in range(18):
                if 2 <= x <= 15 and 2 <= y <= 15:
                    if x == 2 or x == 15 or y == 2 or y == 15:
                        self.mixed_icon.put("#8BAE66", (x, y))
                    else:
                        self.mixed_icon.put("#EBD5AB", (x, y))
        
        # Draw horizontal line
        for x in range(5, 13):
            self.mixed_icon.put("#1B211A", (x, 8))
            self.mixed_icon.put("#1B211A", (x, 9))

    def _handle_click(self, event):
        """Handle single click to toggle checkbox."""
        region = self.identify("region", event.x, event.y)
        if region == "tree":
            item = self.identify("item", event.x, event.y)
            if item:
                self.toggle_check(item)

    def _handle_double_click(self, event):
        """Handle double click to expand/collapse folders."""
        region = self.identify("region", event.x, event.y)
        if region == "tree":
            item = self.identify("item", event.x, event.y)
            if item and self.item(item, "open"):
                self.item(item, open=False)
            elif item:
                self.item(item, open=True)

    def toggle_check(self, item):
        """Toggle checkbox state for an item."""
        current_tags = self.item(item, "tags")
        if "checked" in current_tags:
            self.item(item, tags=("unchecked",))
            self._propagate_check_state(item, False)
        else:
            self.item(item, tags=("checked",))
            self._propagate_check_state(item, True)

    def _propagate_check_state(self, item, checked):
        """Propagate check state to children and update parent state."""
        # Update children
        children = self.get_children(item)
        for child in children:
            self.item(child, tags=("checked",) if checked else ("unchecked",))
            self._propagate_check_state(child, checked)

        # Update parent if needed
        parent = self.parent(item)
        if parent and parent != "":
            self._update_parent_check_state(parent)

    def _update_parent_check_state(self, parent):
        """Update parent checkbox based on children states."""
        children = self.get_children(parent)
        if not children:
            return

        all_checked = all("checked" in self.item(child, "tags") for child in children)
        any_checked = any("checked" in self.item(child, "tags") for child in children)
        all_unchecked = all("unchecked" in self.item(child, "tags") for child in children)

        if all_checked:
            self.item(parent, tags=("checked",))
        elif all_unchecked:
            self.item(parent, tags=("unchecked",))
        else:
            self.item(parent, tags=("mixed",))

    def get_checked_items(self):
        """Get all checked items."""
        checked_items = []

        def traverse(item):
            if "checked" in self.item(item, "tags"):
                checked_items.append(item)
            for child in self.get_children(item):
                traverse(child)

        for child in self.get_children():
            traverse(child)

        return checked_items

class CodebaseCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("codeBASED")
        self.root.geometry("1200x800")
        
        # Use custom color palette
        self.colors = {
            'background': '#1B211A',
            'primary': '#628141',
            'secondary': '#8BAE66',
            'accent': '#EBD5AB',
            'surface': '#2A3129',
            'text_primary': '#EBD5AB',
            'text_secondary': '#8BAE66',
            'divider': '#3A4239',
            'success': '#8BAE66',
            'warning': '#EBD5AB',
            'error': '#C44536'
        }
        
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
        for i in range(7):
            self.main_container.grid_rowconfigure(i, weight=[0, 1, 0, 1, 0, 1, 0][i])
        
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
        
        # Source folder section
        self.source_frame = tk.Frame(self.main_container, bg=self.colors['surface'])
        self.source_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.source_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(
            self.source_frame,
            text="Source Folder:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent'],
            anchor='w'
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        self.folder_path_var = tk.StringVar()
        folder_entry = tk.Entry(
            self.source_frame,
            textvariable=self.folder_path_var,
            font=('Segoe UI', 10),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        folder_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), ipady=8)
        
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
        self.select_folder_btn.grid(row=0, column=2, padx=(0, 15), ipadx=15, ipady=6)
        
        # File tree section
        tree_container = tk.Frame(self.main_container, bg=self.colors['surface'])
        tree_container.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Treeview frame
        tree_inner_frame = tk.Frame(tree_container, bg=self.colors['surface'])
        tree_inner_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        tree_inner_frame.grid_rowconfigure(0, weight=1)
        tree_inner_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_inner_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_inner_frame, orient="horizontal")
        
        # Create checkbox treeview
        self.tree = CheckboxTreeview(
            tree_inner_frame,
            columns=("path", "size", "modified"),
            show="tree headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
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
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Tree controls
        controls_frame = tk.Frame(tree_container, bg=self.colors['surface'])
        controls_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Status and count labels
        self.status_var = tk.StringVar(value="Ready to select folder")
        self.status_label = tk.Label(
            controls_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg=self.colors['surface'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.Y)
        
        self.file_count_var = tk.StringVar(value="Files: 0")
        self.file_count_label = tk.Label(
            controls_frame,
            textvariable=self.file_count_var,
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent']
        )
        self.file_count_label.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Output settings section
        output_frame = tk.Frame(self.main_container, bg=self.colors['surface'])
        output_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        output_frame.grid_columnconfigure(1, weight=1)
        
        # Output directory
        tk.Label(
            output_frame,
            text="Output Directory:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent'],
            anchor='w'
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.output_dir_var = tk.StringVar()
        output_dir_entry = tk.Entry(
            output_frame,
            textvariable=self.output_dir_var,
            font=('Segoe UI', 10),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        output_dir_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(15, 5), ipady=6)
        
        self.select_output_btn = tk.Button(
            output_frame,
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
        self.select_output_btn.grid(row=0, column=2, padx=(0, 15), pady=(15, 5), ipadx=10, ipady=4)
        
        # Output filename
        tk.Label(
            output_frame,
            text="Output Filename:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['accent'],
            anchor='w'
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        
        self.output_file_var = tk.StringVar(value="codebase.txt")
        output_file_entry = tk.Entry(
            output_frame,
            textvariable=self.output_file_var,
            font=('Segoe UI', 10),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        output_file_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15), ipady=6)
        output_file_entry.bind('<KeyRelease>', self.update_full_output_path)
        
        # Full path display
        self.full_output_path_var = tk.StringVar()
        self.path_display = tk.Label(
            output_frame,
            textvariable=self.full_output_path_var,
            font=('Segoe UI', 9),
            bg=self.colors['surface'],
            fg=self.colors['text_secondary']
        )
        self.path_display.grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 15))
        
        # Action buttons section
        buttons_frame = tk.Frame(self.main_container, bg=self.colors['background'])
        buttons_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Left action buttons
        left_buttons = tk.Frame(buttons_frame, bg=self.colors['background'])
        left_buttons.pack(side=tk.LEFT)
        
        # Action buttons
        self.refresh_btn = tk.Button(
            left_buttons,
            text="Refresh",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.refresh_tree
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=6)
        
        self.check_all_btn = tk.Button(
            left_buttons,
            text="Check All",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.check_all
        )
        self.check_all_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=6)
        
        self.uncheck_all_btn = tk.Button(
            left_buttons,
            text="Uncheck All",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.uncheck_all
        )
        self.uncheck_all_btn.pack(side=tk.LEFT, ipadx=15, ipady=6)
        
        # Main compile button
        self.compile_btn = tk.Button(
            buttons_frame,
            text="Compile Selected Files",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.compile_selected
        )
        self.compile_btn.pack(side=tk.RIGHT, ipadx=30, ipady=8)
        
        # Progress bar section
        self.progress_frame = tk.Frame(self.main_container, bg=self.colors['background'])
        self.progress_frame.grid(row=5, column=0, sticky="ew")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode='determinate',
            length=100
        )
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.progress_frame.grid_remove()  # Hide initially
        
        # Configure styles
        self._configure_styles()
        
        # Queue for thread communication
        self.queue = queue.Queue()
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
                # Keep size and modified columns fixed

    def select_folder(self):
        """Open folder selection dialog."""
        folder_path = filedialog.askdirectory(title="Select Codebase Folder")
        if folder_path:
            self.folder_path_var.set(folder_path)
            self.current_folder = Path(folder_path)
            
            # Set default output directory to the selected folder
            self.output_dir_var.set(str(folder_path))
            self.output_dir = Path(folder_path)
            self.update_full_output_path()
            
            self.load_tree()

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

    def load_tree(self):
        """Load files and folders into the treeview."""
        if not self.current_folder or not self.current_folder.exists():
            messagebox.showerror("Error", "Invalid folder path")
            return

        self.status_var.set(f"Loading files from: {self.current_folder.name}...")
        self.root.update()

        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.file_items = {}
        row_index = 0

        def add_items(parent_path, parent_id=""):
            nonlocal row_index
            try:
                items = sorted(parent_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

                for item in items:
                    if item.name.startswith('.'):
                        continue

                    relative_path = item.relative_to(self.current_folder)
                    display_name = item.name
                    icon = "📁" if item.is_dir() else self._get_file_icon(item.name)

                    # Get file info
                    size = ""
                    modified = ""
                    if item.is_file():
                        try:
                            size = self._format_size(item.stat().st_size)
                            modified_time = time.localtime(item.stat().st_mtime)
                            modified = time.strftime("%Y-%m-%d %H:%M", modified_time)
                        except:
                            size = "N/A"
                            modified = "N/A"

                    # Insert item with alternating row colors
                    row_tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
                    item_id = self.tree.insert(
                        parent_id, "end",
                        text=f"{icon} {display_name}",
                        values=(str(relative_path), size, modified),
                        tags=("unchecked", row_tag, 'folder' if item.is_dir() else 'file')
                    )

                    self.file_items[item_id] = {
                        'path': item,
                        'is_dir': item.is_dir(),
                        'relative_path': relative_path
                    }
                    row_index += 1

                    # Recursively add subdirectories
                    if item.is_dir():
                        add_items(item, item_id)

            except Exception as e:
                messagebox.showwarning("Warning", f"Error accessing {parent_path}: {str(e)}")

        try:
            add_items(self.current_folder)
            self.status_var.set(f"Loaded folder: {self.current_folder.name}")
            self.update_file_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load folder: {str(e)}")
            self.status_var.set("Error loading folder")

    def _get_file_icon(self, filename):
        """Get appropriate emoji icon for file type."""
        ext = os.path.splitext(filename)[1].lower()
        
        icon_map = {
            '.py': '🐍', '.js': '📜', '.jsx': '⚛️', '.ts': '📘', '.tsx': '⚛️',
            '.html': '🌐', '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
            '.java': '☕', '.cpp': '🔧', '.c': '🔧', '.h': '📋',
            '.json': '📦', '.xml': '📄', '.yml': '⚙️', '.yaml': '⚙️',
            '.md': '📝', '.txt': '📃', '.csv': '📊', '.sql': '🗄️',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
            '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📗', '.xlsx': '📗',
            '.zip': '🗜️', '.tar': '🗜️', '.gz': '🗜️', '.7z': '🗜️',
            '.exe': '⚙️', '.dll': '🔧', '.so': '🔧', '.dylib': '🔧',
            '.sh': '🐚', '.bash': '🐚', '.zsh': '🐚',
            '.php': '🐘', '.rb': '💎', '.go': '🐹', '.rs': '🦀',
            '.swift': '🐦', '.kt': '🅺', '.dart': '🎯',
        }
        
        return icon_map.get(ext, '📄')

    def _format_size(self, size_in_bytes):
        """Format file size in human readable format."""
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.1f} KB"
        elif size_in_bytes < 1024 * 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

    def update_file_count(self):
        """Update the file count display."""
        file_count = sum(1 for item in self.file_items.values() if not item['is_dir'])
        folder_count = sum(1 for item in self.file_items.values() if item['is_dir'])
        self.file_count_var.set(f"📁 {folder_count} folders | 📄 {file_count} files")

    def refresh_tree(self):
        """Refresh the treeview with current folder."""
        if self.current_folder:
            self.load_tree()

    def check_all(self):
        """Check all items in the tree."""
        def check_recursive(item_id):
            self.tree.item(item_id, tags=("checked",))
            for child in self.tree.get_children(item_id):
                check_recursive(child)

        for item in self.tree.get_children():
            check_recursive(item)

    def uncheck_all(self):
        """Uncheck all items in the tree."""
        def uncheck_recursive(item_id):
            self.tree.item(item_id, tags=("unchecked",))
            for child in self.tree.get_children(item_id):
                uncheck_recursive(child)

        for item in self.tree.get_children():
            uncheck_recursive(item)

    def compile_selected(self):
        """Compile selected files into a single text file."""
        checked_items = self.tree.get_checked_items()
        selected_files = [self.file_items[item_id]['path']
                         for item_id in checked_items
                         if not self.file_items[item_id]['is_dir']]

        if not selected_files:
            messagebox.showwarning("No Files Selected", 
                                 "Please select at least one file to compile.")
            return

        # Get output directory and file
        output_dir = self.output_dir_var.get().strip()
        output_file = self.output_file_var.get().strip()
        
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Please select a valid output directory")
            return
        
        if not output_file:
            output_file = "codebase.txt"
            self.output_file_var.set(output_file)
        
        full_output_path = os.path.join(output_dir, output_file)

        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Compilation",
            f"📦 You are about to compile {len(selected_files)} files\n\n"
            f"📁 Output: {full_output_path}\n"
            f"📄 Files selected: {len(selected_files)}",
            icon='question'
        )

        if not confirm:
            return

        # Show progress bar
        self.progress_frame.grid()
        self.progress_var.set(0)
        
        # Start compilation in a separate thread
        threading.Thread(target=self._compile_files_thread, 
                        args=(selected_files, full_output_path), 
                        daemon=True).start()

    def _compile_files_thread(self, files, full_output_path):
        """Thread function for compiling files."""
        try:
            total_files = len(files)
            processed = 0
            errors = []

            with open(full_output_path, 'w', encoding='utf-8') as outfile:
                # Write header with custom colors in comments
                outfile.write("=" * 70 + "\n")
                outfile.write(" " * 10 + "codeBASED COMPILATION ARCHIVE\n")
                outfile.write("=" * 70 + "\n\n")
                outfile.write(f"// Source Directory: {self.current_folder}\n")
                outfile.write(f"// Output File: {full_output_path}\n")
                outfile.write(f"// Total Files: {total_files}\n")
                outfile.write(f"// Compiled on: {time.strftime('%Y-%m-%d at %H:%M:%S')}\n")
                outfile.write("=" * 70 + "\n\n")

                for file_path in files:
                    processed += 1
                    relative_path = file_path.relative_to(self.current_folder)

                    # Update progress
                    progress = (processed / total_files) * 100
                    self.queue.put(('progress', progress))
                    self.queue.put(('status', f"Processing {processed}/{total_files}: {relative_path}"))

                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                            content = infile.read()
                        
                        # Get file stats
                        stats = file_path.stat()
                        file_size = self._format_size(stats.st_size)
                        mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                        
                        # Write file header
                        outfile.write("// " + "=" * 67 + "\n")
                        outfile.write(f"// FILE: {relative_path}\n")
                        outfile.write(f"// Path: {file_path}\n")
                        outfile.write(f"// Size: {file_size}\n")
                        outfile.write(f"// Last Modified: {mod_time}\n")
                        outfile.write(f"// Lines: {len(content.splitlines())}\n")
                        outfile.write("// " + "=" * 67 + "\n\n")
                        
                        # Write content
                        outfile.write(content)
                        
                        # Add spacing between files
                        outfile.write("\n\n")

                    except Exception as e:
                        error_msg = f"Error reading {relative_path}: {str(e)}"
                        errors.append(error_msg)
                        outfile.write(f"// ERROR: {error_msg}\n\n")

                # Write footer
                outfile.write("=" * 70 + "\n")
                outfile.write(" " * 10 + "COMPILATION COMPLETE\n")
                outfile.write("=" * 70 + "\n\n")
                outfile.write(f"// Summary:\n")
                outfile.write(f"//   Successfully processed: {total_files - len(errors)} files\n")
                outfile.write(f"//   Errors encountered: {len(errors)} files\n")
                outfile.write(f"//   Total size: {self._format_size(os.path.getsize(full_output_path))}\n")
                outfile.write(f"//   Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if errors:
                    outfile.write("\n// " + "!" * 67 + "\n")
                    outfile.write("// ERRORS ENCOUNTERED:\n")
                    for error in errors[:10]:
                        outfile.write(f"//   • {error}\n")
                    if len(errors) > 10:
                        outfile.write(f"//   ... and {len(errors) - 10} more errors\n")

            # Final status update
            if errors:
                self.queue.put(('error', f"Completed with {len(errors)} errors"))
                self.root.after(0, lambda: messagebox.showwarning(
                    "Compilation Complete",
                    f"Compilation finished with {len(errors)} errors.\n\n"
                    f"Output: {full_output_path}\n"
                    f"Files processed: {total_files}\n"
                    f"Errors: {len(errors)}\n\n"
                    f"Check the output file for details."
                ))
            else:
                self.queue.put(('success', f"Successfully compiled {total_files} files"))
                file_size = os.path.getsize(full_output_path)
                size_str = self._format_size(file_size)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    f"Compilation completed successfully!\n\n"
                    f"Output file: {full_output_path}\n"
                    f"Files compiled: {total_files}\n"
                    f"Output size: {size_str}\n\n"
                    f"Your codebase is ready for review!"
                ))

        except Exception as e:
            self.queue.put(('error', f"Compilation failed: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Compilation failed:\n\n{str(e)}"
            ))
        finally:
            self.queue.put(('progress_complete', None))

    def process_queue(self):
        """Process messages from the compilation thread."""
        try:
            while True:
                msg_type, message = self.queue.get_nowait()
                if msg_type == 'status':
                    self.status_var.set(message)
                elif msg_type == 'progress':
                    self.progress_var.set(message)
                elif msg_type == 'progress_complete':
                    self.progress_frame.grid_remove()
                elif msg_type == 'success':
                    self.status_var.set(message)
                    self.status_label.config(fg=self.colors['success'])
                elif msg_type == 'error':
                    self.status_var.set(message)
                    self.status_label.config(fg=self.colors['error'])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

def main():
    """Main application entry point."""
    root = tk.Tk()
    
    # Create application
    app = CodebaseCompilerApp(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()