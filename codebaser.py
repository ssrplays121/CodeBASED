#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
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

        # Bind click events
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Double-1>", self._handle_double_click)

    def _create_checkbox_images(self):
        """Create checkbox images using canvas."""
        # Create checked icon (✓)
        self.checked_icon = tk.PhotoImage(width=16, height=16)
        self.checked_icon.put("#4CAF50", to=(2, 2, 14, 14))
        self.checked_icon.put("#FFFFFF", to=(5, 5, 11, 11))
        self.checked_icon.put("#4CAF50", to=(7, 9, 9, 11))  # Check mark

        # Create unchecked icon (□)
        self.unchecked_icon = tk.PhotoImage(width=16, height=16)
        self.unchecked_icon.put("#2196F3", to=(2, 2, 14, 14))
        self.unchecked_icon.put("#FFFFFF", to=(4, 4, 12, 12))

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

        if all_checked:
            self.item(parent, tags=("checked",))
        elif any_checked:
            # Mixed state - use unchecked for simplicity
            self.item(parent, tags=("unchecked",))
        else:
            self.item(parent, tags=("unchecked",))

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
        self.root.title("Codebase Compiler")
        self.root.geometry("1000x700")

        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", padding=6, font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'), foreground="#2196F3")
        style.configure("Status.TLabel", font=('Segoe UI', 9), foreground="#666666")
        style.configure("Success.TLabel", foreground="#4CAF50")
        style.configure("Error.TLabel", foreground="#F44336")

        # Main frame
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="Codebase Compiler", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(header_frame, text="✓ Select files to compile into a single text file",
                 style="Status.TLabel").pack(side=tk.LEFT, padx=(10, 0))

        # Folder selection frame
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))

        self.folder_path_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_path_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="📁 Select Folder", command=self.select_folder).pack(side=tk.RIGHT)

        # Treeview frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create checkbox treeview
        self.tree = CheckboxTreeview(tree_frame, columns=("path", "size", "modified"),
                                    show="tree headings", yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)

        # Configure columns
        self.tree.heading("#0", text="File/Folder", anchor=tk.W)
        self.tree.heading("path", text="Path", anchor=tk.W)
        self.tree.heading("size", text="Size", anchor=tk.E)
        self.tree.heading("modified", text="Last Modified", anchor=tk.W)

        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("path", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=80, anchor=tk.E)
        self.tree.column("modified", width=150, minwidth=120)

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready to select folder")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)

        self.file_count_var = tk.StringVar(value="Files: 0")
        ttk.Label(status_frame, textvariable=self.file_count_var, style="Status.TLabel").pack(side=tk.RIGHT, padx=(10, 0))

        # Output frame
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))

        # Output directory selection
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(output_dir_frame, text="Output directory:", style="Status.TLabel").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(output_dir_frame, text="📁 Select Output Folder", command=self.select_output_dir).pack(side=tk.RIGHT)

        # Output filename
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X)
        
        ttk.Label(output_file_frame, text="Output filename:", style="Status.TLabel").pack(side=tk.LEFT)
        self.output_file_var = tk.StringVar(value="codebase.txt")
        output_file_entry = ttk.Entry(output_file_frame, textvariable=self.output_file_var, width=40)
        output_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        output_file_entry.bind('<KeyRelease>', self.update_full_output_path)

        # Full output path display
        self.full_output_path_var = tk.StringVar()
        ttk.Label(output_file_frame, textvariable=self.full_output_path_var, style="Status.TLabel").pack(side=tk.BOTTOM, pady=(5, 0))

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="🔍 Refresh Tree", command=self.refresh_tree).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="✓ Check All", command=self.check_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="✗ Uncheck All", command=self.uncheck_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⚡ Compile Selected", command=self.compile_selected,
                  style="Accent.TButton").pack(side=tk.RIGHT)

        # Configure accent button style
        style.configure("Accent.TButton", background="#4CAF50", foreground="white")
        style.map("Accent.TButton", background=[('active', '#45a049')])

        # Queue for thread communication
        self.queue = queue.Queue()
        self.root.after(100, self.process_queue)

        self.current_folder = None
        self.file_items = {}
        self.output_dir = None

        # Initialize default output directory
        self.update_full_output_path()

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
            self.full_output_path_var.set(f"Full path: {full_path}")
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
                    icon = "📁" if item.is_dir() else "📄"

                    # Get file info
                    size = ""
                    modified = ""
                    if item.is_file():
                        try:
                            size = f"{item.stat().st_size / 1024:.1f} KB" if item.stat().st_size > 1024 else f"{item.stat().st_size} B"
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

    def update_file_count(self):
        """Update the file count display."""
        file_count = sum(1 for item in self.file_items.values() if not item['is_dir'])
        self.file_count_var.set(f"Files: {file_count}")

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
            messagebox.showwarning("No Files Selected", "Please select at least one file to compile.")
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
            f"You are about to compile {len(selected_files)} files into:\n\n{full_output_path}\n\n"
            f"Selected files:\n" + "\n".join([f"• {f.name}" for f in selected_files[:5]]) +
            (f"\n... and {len(selected_files)-5} more" if len(selected_files) > 5 else ""),
            icon='question'
        )

        if not confirm:
            return

        # Start compilation in a separate thread
        threading.Thread(target=self._compile_files_thread, args=(selected_files, full_output_path), daemon=True).start()

    def _compile_files_thread(self, files, full_output_path):
        """Thread function for compiling files."""
        try:
            total_files = len(files)
            processed = 0
            errors = []

            with open(full_output_path, 'w', encoding='utf-8') as outfile:
                outfile.write(f"=== CODEBASE COMPILATION ===\n")
                outfile.write(f"Source Folder: {self.current_folder}\n")
                outfile.write(f"Output File: {full_output_path}\n")
                outfile.write(f"Files compiled: {total_files}\n")
                outfile.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write("=" * 50 + "\n\n")

                for file_path in files:
                    processed += 1
                    relative_path = file_path.relative_to(self.current_folder)

                    # Update status via queue
                    self.queue.put(('status', f"Processing {processed}/{total_files}: {file_path.name}"))

                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()

                        outfile.write(f"// {'=' * 60}\n")
                        outfile.write(f"// File: {relative_path}\n")
                        outfile.write(f"// Path: {file_path}\n")
                        outfile.write(f"// Size: {file_path.stat().st_size} bytes\n")
                        outfile.write(f"// Last Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_path.stat().st_mtime))}\n")
                        outfile.write(f"// {'=' * 60}\n\n")
                        outfile.write(content + "\n\n")

                    except Exception as e:
                        error_msg = f"Error reading {relative_path}: {str(e)}"
                        errors.append(error_msg)
                        outfile.write(f"// ERROR: {error_msg}\n\n")

            # Final status update
            if errors:
                self.queue.put(('error', f"Compilation completed with {len(errors)} errors. Output saved to {full_output_path}"))
                self.root.after(0, lambda: messagebox.showwarning("Compilation Warnings",
                    f"Completed with {len(errors)} errors:\n" + "\n".join(errors[:3]) +
                    ("\n... and more" if len(errors) > 3 else "")))
            else:
                self.queue.put(('success', f"Successfully compiled {total_files} files to {full_output_path}"))
                file_size = os.path.getsize(full_output_path) / 1024
                size_str = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                self.root.after(0, lambda: messagebox.showinfo("Success",
                    f"Compilation completed successfully!\n\n"
                    f"Files compiled: {total_files}\n"
                    f"Output file: {full_output_path}\n"
                    f"Output size: {size_str}"))

        except Exception as e:
            self.queue.put(('error', f"Compilation failed: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Compilation failed: {str(e)}"))

    def process_queue(self):
        """Process messages from the compilation thread."""
        try:
            while True:
                msg_type, message = self.queue.get_nowait()
                if msg_type == 'status':
                    self.status_var.set(message)
                elif msg_type == 'success':
                    self.status_var.set(message)
                    self.status_label.configure(style="Success.TLabel")
                elif msg_type == 'error':
                    self.status_var.set(message)
                    self.status_label.configure(style="Error.TLabel")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

def main():
    """Main application entry point."""
    root = tk.Tk()

    # Set application icon (if available)
    try:
        if sys.platform.startswith('win'):
            root.iconbitmap(default='python.ico')
    except:
        pass

    app = CodebaseCompilerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    