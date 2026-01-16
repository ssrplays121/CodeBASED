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
        self.tag_configure("checked", image=self.checked_icon, foreground="#4CAF50")
        self.tag_configure("unchecked", image=self.unchecked_icon, foreground="#757575")
        self.tag_configure("mixed", image=self.mixed_icon, foreground="#FF9800")

        # Bind click events
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Double-1>", self._handle_double_click)

    def _create_checkbox_images(self):
        """Create checkbox images using canvas."""
        # Create checked icon (✓) - simplified version
        self.checked_icon = tk.PhotoImage(width=16, height=16)
        # Draw a simple check mark in a box
        for i in range(16):
            for j in range(16):
                if 2 <= i <= 13 and 2 <= j <= 13:
                    # White background
                    self.checked_icon.put("#FFFFFF", (i, j))
        # Green border
        for i in range(2, 14):
            self.checked_icon.put("#4CAF50", (i, 2))
            self.checked_icon.put("#4CAF50", (i, 13))
        for j in range(2, 14):
            self.checked_icon.put("#4CAF50", (2, j))
            self.checked_icon.put("#4CAF50", (13, j))
        # Check mark
        for i in range(5, 11):
            self.checked_icon.put("#4CAF50", (i, 7))
            self.checked_icon.put("#4CAF50", (i, 8))
        self.checked_icon.put("#4CAF50", (6, 6))
        self.checked_icon.put("#4CAF50", (7, 6))
        self.checked_icon.put("#4CAF50", (9, 9))
        self.checked_icon.put("#4CAF50", (10, 9))

        # Create unchecked icon (□)
        self.unchecked_icon = tk.PhotoImage(width=16, height=16)
        for i in range(16):
            for j in range(16):
                if 2 <= i <= 13 and 2 <= j <= 13:
                    self.unchecked_icon.put("#FFFFFF", (i, j))
        # Gray border
        for i in range(2, 14):
            self.unchecked_icon.put("#BDBDBD", (i, 2))
            self.unchecked_icon.put("#BDBDBD", (i, 13))
        for j in range(2, 14):
            self.unchecked_icon.put("#BDBDBD", (2, j))
            self.unchecked_icon.put("#BDBDBD", (13, j))

        # Create mixed state icon (-)
        self.mixed_icon = tk.PhotoImage(width=16, height=16)
        for i in range(16):
            for j in range(16):
                if 2 <= i <= 13 and 2 <= j <= 13:
                    self.mixed_icon.put("#FFFFFF", (i, j))
        # Orange border
        for i in range(2, 14):
            self.mixed_icon.put("#FF9800", (i, 2))
            self.mixed_icon.put("#FF9800", (i, 13))
        for j in range(2, 14):
            self.mixed_icon.put("#FF9800", (2, j))
            self.mixed_icon.put("#FF9800", (13, j))
        # Minus sign
        for i in range(4, 12):
            self.mixed_icon.put("#FF9800", (i, 7))
            self.mixed_icon.put("#FF9800", (i, 8))

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
        self.root.title("Codebase Compiler Pro")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # Modern color scheme
        self.colors = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'primary_light': '#BBDEFB',
            'secondary': '#4CAF50',
            'secondary_dark': '#388E3C',
            'accent': '#FF9800',
            'background': '#FAFAFA',
            'surface': '#FFFFFF',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'divider': '#E0E0E0',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336'
        }
        
        # Set window background
        self.root.configure(bg=self.colors['background'])
        
        # Configure styles
        self._configure_styles()
        
        # Main container
        self.main_container = tk.Frame(root, bg=self.colors['background'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with gradient effect (simulated with solid color and border)
        header_frame = tk.Frame(self.main_container, 
                               bg=self.colors['primary'],
                               height=100,
                               relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors['primary'])
        header_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # App title with icon
        title_frame = tk.Frame(header_content, bg=self.colors['primary'])
        title_frame.pack()
        
        # Icon label
        icon_label = tk.Label(title_frame, text="⚡", 
                            font=('Segoe UI', 32, 'bold'),
                            bg=self.colors['primary'], 
                            fg='white')
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title text
        title_text = tk.Label(title_frame, 
                            text="Codebase Compiler Pro", 
                            font=('Segoe UI', 24, 'bold'),
                            bg=self.colors['primary'], 
                            fg='white')
        title_text.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle = tk.Label(header_content, 
                          text="Compile your codebase into a single, organized file", 
                          font=('Segoe UI', 11),
                          bg=self.colors['primary'], 
                          fg='#E3F2FD')
        subtitle.pack(pady=(5, 0))
        
        # Folder selection card
        folder_card = self._create_card(self.main_container, "📁 Source Folder")
        folder_card.pack(fill=tk.X, pady=(0, 15))
        
        # Folder selection frame inside card
        folder_selection_frame = tk.Frame(folder_card, bg=self.colors['surface'])
        folder_selection_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.folder_path_var = tk.StringVar()
        folder_entry = tk.Entry(folder_selection_frame, 
                              textvariable=self.folder_path_var, 
                              font=('Segoe UI', 10),
                              bd=2,
                              relief=tk.FLAT,
                              bg='white',
                              fg=self.colors['text_primary'],
                              insertbackground=self.colors['primary'])
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        
        # Select folder button
        select_btn = tk.Button(folder_selection_frame, 
                             text="Browse", 
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['primary'], 
                             fg='white',
                             activebackground=self.colors['primary_dark'],
                             activeforeground='white',
                             relief=tk.FLAT,
                             cursor='hand2',
                             command=self.select_folder)
        select_btn.pack(side=tk.RIGHT, ipadx=20, ipady=8)
        
        # File tree card
        tree_card = self._create_card(self.main_container, "📂 File Selection")
        tree_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview container
        tree_container = tk.Frame(tree_card, bg=self.colors['surface'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        # Create checkbox treeview
        self.tree = CheckboxTreeview(tree_container, 
                                    columns=("path", "size", "modified"),
                                    show="tree headings",
                                    yscrollcommand=vsb.set,
                                    xscrollcommand=hsb.set)
        
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
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Status bar
        self.status_bar = tk.Frame(self.main_container, 
                                  bg=self.colors['surface'], 
                                  height=40,
                                  relief=tk.FLAT,
                                  borderwidth=1)
        self.status_bar.pack(fill=tk.X, pady=(0, 15))
        self.status_bar.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready to select folder")
        self.file_count_var = tk.StringVar(value="Files: 0")
        
        status_label = tk.Label(self.status_bar, 
                              textvariable=self.status_var,
                              font=('Segoe UI', 9),
                              bg=self.colors['surface'], 
                              fg=self.colors['text_secondary'])
        status_label.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        file_count_label = tk.Label(self.status_bar, 
                                  textvariable=self.file_count_var,
                                  font=('Segoe UI', 9, 'bold'),
                                  bg=self.colors['surface'], 
                                  fg=self.colors['primary'])
        file_count_label.pack(side=tk.RIGHT, padx=20, fill=tk.Y)
        
        # Output settings card
        output_card = self._create_card(self.main_container, "💾 Output Settings")
        output_card.pack(fill=tk.X, pady=(0, 15))
        
        output_content = tk.Frame(output_card, bg=self.colors['surface'])
        output_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Output directory
        output_dir_frame = tk.Frame(output_content, bg=self.colors['surface'])
        output_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(output_dir_frame, 
                text="Output Directory:", 
                font=('Segoe UI', 10),
                bg=self.colors['surface'], 
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.output_dir_var = tk.StringVar()
        output_dir_entry = tk.Entry(output_dir_frame, 
                                  textvariable=self.output_dir_var,
                                  font=('Segoe UI', 10),
                                  bd=2,
                                  relief=tk.FLAT,
                                  bg='white',
                                  fg=self.colors['text_primary'],
                                  insertbackground=self.colors['primary'])
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10), ipady=6)
        
        output_dir_btn = tk.Button(output_dir_frame, 
                                 text="Select",
                                 font=('Segoe UI', 9),
                                 bg=self.colors['primary_light'], 
                                 fg=self.colors['primary'],
                                 activebackground=self.colors['primary'],
                                 activeforeground='white',
                                 relief=tk.FLAT,
                                 cursor='hand2',
                                 command=self.select_output_dir)
        output_dir_btn.pack(side=tk.RIGHT, ipadx=15, ipady=4)
        
        # Output filename
        output_file_frame = tk.Frame(output_content, bg=self.colors['surface'])
        output_file_frame.pack(fill=tk.X)
        
        tk.Label(output_file_frame, 
                text="Output Filename:", 
                font=('Segoe UI', 10),
                bg=self.colors['surface'], 
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.output_file_var = tk.StringVar(value="codebase.txt")
        output_file_entry = tk.Entry(output_file_frame, 
                                   textvariable=self.output_file_var,
                                   font=('Segoe UI', 10),
                                   bd=2,
                                   relief=tk.FLAT,
                                   bg='white',
                                   fg=self.colors['text_primary'],
                                   insertbackground=self.colors['primary'])
        output_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10), ipady=6)
        output_file_entry.bind('<KeyRelease>', self.update_full_output_path)
        
        # Full path display
        self.full_output_path_var = tk.StringVar()
        path_label = tk.Label(output_content, 
                            textvariable=self.full_output_path_var,
                            font=('Segoe UI', 9),
                            bg=self.colors['surface'], 
                            fg=self.colors['text_secondary'])
        path_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Action buttons frame
        button_frame = tk.Frame(self.main_container, bg=self.colors['background'])
        button_frame.pack(fill=tk.X)
        
        # Left buttons (actions)
        left_buttons = tk.Frame(button_frame, bg=self.colors['background'])
        left_buttons.pack(side=tk.LEFT)
        
        # Action buttons
        refresh_btn = tk.Button(left_buttons, 
                              text="🔄 Refresh", 
                              font=('Segoe UI', 10),
                              bg=self.colors['primary_light'], 
                              fg=self.colors['primary'],
                              activebackground=self.colors['primary'],
                              activeforeground='white',
                              relief=tk.FLAT,
                              cursor='hand2',
                              command=self.refresh_tree)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=8)
        
        check_btn = tk.Button(left_buttons, 
                            text="✓ Check All", 
                            font=('Segoe UI', 10),
                            bg='#E8F5E9', 
                            fg=self.colors['success'],
                            activebackground=self.colors['success'],
                            activeforeground='white',
                            relief=tk.FLAT,
                            cursor='hand2',
                            command=self.check_all)
        check_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=8)
        
        uncheck_btn = tk.Button(left_buttons, 
                              text="✗ Uncheck All", 
                              font=('Segoe UI', 10),
                              bg='#FFEBEE', 
                              fg=self.colors['error'],
                              activebackground=self.colors['error'],
                              activeforeground='white',
                              relief=tk.FLAT,
                              cursor='hand2',
                              command=self.uncheck_all)
        uncheck_btn.pack(side=tk.LEFT, ipadx=15, ipady=8)
        
        # Right button (main action)
        compile_btn = tk.Button(button_frame, 
                              text="⚡ Compile Selected Files", 
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['secondary'], 
                              fg='white',
                              activebackground=self.colors['secondary_dark'],
                              activeforeground='white',
                              relief=tk.FLAT,
                              cursor='hand2',
                              command=self.compile_selected)
        compile_btn.pack(side=tk.RIGHT, ipadx=30, ipady=10)
        
        # Progress bar (hidden initially)
        self.progress_frame = tk.Frame(self.main_container, bg=self.colors['background'])
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          variable=self.progress_var,
                                          mode='determinate',
                                          length=100)
        self.progress_bar.pack(fill=tk.X)
        
        # Queue for thread communication
        self.queue = queue.Queue()
        self.root.after(100, self.process_queue)

        self.current_folder = None
        self.file_items = {}
        self.output_dir = None

        # Initialize default output directory
        self.update_full_output_path()
        
        # Center window
        self.center_window()

    def _configure_styles(self):
        """Configure ttk styles for a modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview
        style.configure("Treeview",
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['surface'],
                       borderwidth=0,
                       font=('Segoe UI', 9))
        
        style.configure("Treeview.Heading",
                       background=self.colors['primary_light'],
                       foreground=self.colors['text_primary'],
                       relief=tk.FLAT,
                       font=('Segoe UI', 9, 'bold'))
        
        # Configure scrollbars
        style.configure("Vertical.TScrollbar",
                       background=self.colors['divider'],
                       troughcolor=self.colors['surface'],
                       bordercolor=self.colors['divider'],
                       arrowcolor=self.colors['text_secondary'],
                       gripcount=0)
        
        style.configure("Horizontal.TScrollbar",
                       background=self.colors['divider'],
                       troughcolor=self.colors['surface'],
                       bordercolor=self.colors['divider'],
                       arrowcolor=self.colors['text_secondary'],
                       gripcount=0)
        
        # Configure progress bar
        style.configure("TProgressbar",
                       background=self.colors['primary'],
                       troughcolor=self.colors['background'],
                       bordercolor=self.colors['divider'])

    def _create_card(self, parent, title):
        """Create a modern card container."""
        card = tk.Frame(parent, 
                       bg=self.colors['surface'],
                       relief=tk.FLAT,
                       borderwidth=1)
        
        # Card header
        header = tk.Frame(card, bg=self.colors['primary_light'])
        header.pack(fill=tk.X, pady=(1, 0))
        
        tk.Label(header, 
                text=title, 
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['primary_light'], 
                fg=self.colors['text_primary']).pack(side=tk.LEFT, padx=10, pady=5)
        
        return card

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

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

        def add_items(parent_path, parent_id=""):
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

                    # Insert item
                    item_id = self.tree.insert(
                        parent_id, "end",
                        text=f"{icon} {display_name}",
                        values=(str(relative_path), size, modified),
                        tags=("unchecked",)
                    )

                    self.file_items[item_id] = {
                        'path': item,
                        'is_dir': item.is_dir(),
                        'relative_path': relative_path
                    }

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
        self.progress_frame.pack(fill=tk.X, pady=(15, 0))
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
                # Write header
                outfile.write("=" * 70 + "\n")
                outfile.write(" " * 10 + "📚 CODEBASE COMPILATION ARCHIVE 📚\n")
                outfile.write("=" * 70 + "\n\n")
                outfile.write(f"📁 Source Directory: {self.current_folder}\n")
                outfile.write(f"💾 Output File: {full_output_path}\n")
                outfile.write(f"📊 Total Files: {total_files}\n")
                outfile.write(f"📅 Compiled on: {time.strftime('%Y-%m-%d at %H:%M:%S')}\n")
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
                        outfile.write("▄" * 70 + "\n")
                        outfile.write(f"📄 FILE: {relative_path}\n")
                        outfile.write("─" * 70 + "\n")
                        outfile.write(f"📍 Full Path: {file_path}\n")
                        outfile.write(f"📏 Size: {file_size}\n")
                        outfile.write(f"🕒 Last Modified: {mod_time}\n")
                        outfile.write(f"🔢 Lines: {len(content.splitlines())}\n")
                        outfile.write("─" * 70 + "\n\n")
                        
                        # Write content
                        outfile.write(content)
                        
                        # Add spacing between files
                        outfile.write("\n" + "─" * 70 + "\n\n")

                    except Exception as e:
                        error_msg = f"Error reading {relative_path}: {str(e)}"
                        errors.append(error_msg)
                        outfile.write(f"❌ ERROR: {error_msg}\n\n")

                # Write footer
                outfile.write("=" * 70 + "\n")
                outfile.write(" " * 10 + "✅ COMPILATION COMPLETE ✅\n")
                outfile.write("=" * 70 + "\n\n")
                outfile.write(f"📊 Summary:\n")
                outfile.write(f"   ✅ Successfully processed: {total_files - len(errors)} files\n")
                outfile.write(f"   ❌ Errors encountered: {len(errors)} files\n")
                outfile.write(f"   📁 Total size: {self._format_size(os.path.getsize(full_output_path))}\n")
                outfile.write(f"   ⏱️  Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if errors:
                    outfile.write("\n" + "!" * 70 + "\n")
                    outfile.write("⚠️  ERRORS ENCOUNTERED:\n")
                    for error in errors[:10]:
                        outfile.write(f"   • {error}\n")
                    if len(errors) > 10:
                        outfile.write(f"   ... and {len(errors) - 10} more errors\n")

            # Final status update
            if errors:
                self.queue.put(('error', f"Completed with {len(errors)} errors"))
                self.root.after(0, lambda: messagebox.showwarning(
                    "Compilation Complete",
                    f"✅ Compilation finished with {len(errors)} errors.\n\n"
                    f"📁 Output: {full_output_path}\n"
                    f"📄 Files processed: {total_files}\n"
                    f"⚠️  Errors: {len(errors)}\n\n"
                    f"Check the output file for details."
                ))
            else:
                self.queue.put(('success', f"Successfully compiled {total_files} files"))
                file_size = os.path.getsize(full_output_path)
                size_str = self._format_size(file_size)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success! 🎉",
                    f"✅ Compilation completed successfully!\n\n"
                    f"📁 Output file: {full_output_path}\n"
                    f"📊 Files compiled: {total_files}\n"
                    f"📦 Output size: {size_str}\n\n"
                    f"✨ Your codebase is ready for review!"
                ))

        except Exception as e:
            self.queue.put(('error', f"Compilation failed: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror(
                "Error ❌",
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
                    self.progress_frame.pack_forget()
                elif msg_type == 'success':
                    self.status_var.set(message)
                    self.status_bar.configure(bg=self.colors['success'])
                    for widget in self.status_bar.winfo_children():
                        if isinstance(widget, tk.Label):
                            widget.configure(bg=self.colors['success'], fg='white')
                elif msg_type == 'error':
                    self.status_var.set(message)
                    self.status_bar.configure(bg=self.colors['error'])
                    for widget in self.status_bar.winfo_children():
                        if isinstance(widget, tk.Label):
                            widget.configure(bg=self.colors['error'], fg='white')
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