#!/usr/bin/env python3
"""Application controller – orchestrates UI, scanner, and compiler."""
import os
import threading
import queue
from pathlib import Path
from typing import Dict, Any

from config import COLORS, DEFAULT_OUTPUT_FILENAME
from scanner import DirectoryScanner, format_size
from compiler import compile_files
from dialogs import InfoDialog, WarningDialog, ErrorDialog, ConfirmDialog


class CodebaseController:
    def __init__(self, ui):
        self.ui = ui
        self.current_folder = None
        self.file_items: Dict[str, Any] = {}
        self.loading_thread = None
        self.stop_loading_flag = False
        self.is_loading = False
        self.queue = queue.Queue()
        self._queue_processing_started = False
        
        if self.ui is not None:
            self._start_queue_processor()
    
    def set_ui(self, ui):
        """Set the UI after controller creation."""
        self.ui = ui
        if not self._queue_processing_started:
            self._start_queue_processor()
    
    def _start_queue_processor(self):
        self._queue_processing_started = True
        self.ui.root.after(100, self._process_queue)
    
    # --- Event handlers called by UI ---
    def select_folder(self):
        self.cancel_loading()
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title="Select Codebase Folder")
        if folder_path:
            self.ui.set_source_folder(folder_path)
            self.current_folder = Path(folder_path)
            self.ui.set_output_directory(str(folder_path))
            self.update_full_output_path()
            self._load_tree_async()
    
    def select_output_dir(self):
        from tkinter import filedialog
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if output_dir:
            self.ui.set_output_directory(output_dir)
            self.update_full_output_path()
    
    def update_full_output_path(self, event=None):
        output_dir, output_file = self.ui.get_output_settings()
        if not output_file:
            output_file = DEFAULT_OUTPUT_FILENAME
            self.ui.set_output_filename(output_file)
        if output_dir and os.path.isdir(output_dir):
            full_path = os.path.join(output_dir, output_file)
            self.ui.set_full_output_path_display(full_path)
        else:
            self.ui.set_full_output_path_display("Please select a valid output directory")
    
    def refresh_tree(self):
        if self.current_folder and not self.is_loading:
            self._load_tree_async()
    
    def cancel_loading(self):
        if self.is_loading:
            self.stop_loading_flag = True
            self.is_loading = False
            self.queue.put(('loading_cancelled', None))
            self.ui.show_normal_state()
            self.ui.set_buttons_state(True)
            self.ui.set_status("Loading cancelled")
    
    def check_all(self):
        if not self.is_loading:
            self.ui.check_all()
    
    def uncheck_all(self):
        if not self.is_loading:
            self.ui.uncheck_all()
    
    def compile_selected(self):
        if self.is_loading:
            self._show_warning("Please Wait", "Cannot compile while loading files.")
            return
        
        checked_items = self.ui.get_checked_items()
        selected_files = [self.file_items[item_id]['path']
                          for item_id in checked_items
                          if not self.file_items[item_id]['is_dir']]
        
        if not selected_files:
            self._show_warning("No Files Selected", "Please select at least one file to compile.")
            return
        
        output_dir, output_file = self.ui.get_output_settings()
        if not output_dir or not os.path.isdir(output_dir):
            self._show_error("Error", "Please select a valid output directory")
            return
        if not output_file:
            output_file = DEFAULT_OUTPUT_FILENAME
            self.ui.set_output_filename(output_file)
        
        full_output_path = os.path.join(output_dir, output_file)
        
        confirm = ConfirmDialog(self.ui.root, COLORS, "Confirm Compilation",
                                f"📦 You are about to compile {len(selected_files)} files\n\n"
                                f"📁 Output: {full_output_path}\n"
                                f"📄 Files selected: {len(selected_files)}").show()
        if not confirm:
            return
        
        self.ui.show_progress(0)
        threading.Thread(target=self._compile_thread,
                         args=(selected_files, full_output_path),
                         daemon=True).start()
    
    def on_closing(self):
        self.cancel_loading()
        self.ui.root.destroy()
    
    # --- Internal methods ---
    def _load_tree_async(self):
        if not self.current_folder or not self.current_folder.exists():
            self._show_error("Error", "Invalid folder path")
            return
        
        self.ui.clear_tree()
        self.file_items.clear()
        self.ui.show_loading_state("Scanning directory...")
        self.is_loading = True
        self.stop_loading_flag = False
        self.ui.set_buttons_state(False)
        
        self.loading_thread = threading.Thread(target=self._scan_thread, daemon=True)
        self.loading_thread.start()
    
    def _scan_thread(self):
        scanner = DirectoryScanner(self.current_folder, stop_flag=lambda: self.stop_loading_flag)
        result = scanner.scan(progress_callback=lambda msg: self.queue.put(('loading_progress', msg)))
        
        if result.get('cancelled', False):
            self.queue.put(('loading_cancelled', None))
            return
        
        items_data = result['items']
        row_index = 0
        for item_id, info in items_data.items():
            self.file_items[item_id] = {
                'path': info['path'],
                'is_dir': info['is_dir'],
                'relative_path': info['relative_path']
            }
            row_tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
            row_index += 1
            self.queue.put(('add_item', {
                'item_id': item_id,
                'parent_id': info['parent_id'],
                'text': info['text'],
                'values': info['values'],
                'tags': ("unchecked", row_tag, 'folder' if info['is_dir'] else 'file')
            }))
        
        self.queue.put(('loading_complete', {
            'total_folders': result['total_folders'],
            'total_files': result['total_files']
        }))
    
    def _compile_thread(self, files, output_path):
        def progress_callback(current, total, rel_path):
            percent = (current / total) * 100
            self.queue.put(('progress', percent))
            self.queue.put(('status', f"Processing {current}/{total}: {rel_path}"))
        
        success_count, errors = compile_files(files, output_path, self.current_folder, progress_callback)
        
        if errors:
            self.queue.put(('error', f"Completed with {len(errors)} errors"))
            self.ui.root.after(0, lambda: self._show_warning(
                "Compilation Complete",
                f"Compilation finished with {len(errors)} errors.",
                f"Output: {output_path}\nFiles processed: {len(files)}\nErrors: {len(errors)}"
            ))
        else:
            self.queue.put(('success', f"Successfully compiled {success_count} files"))
            size_str = format_size(os.path.getsize(output_path))
            self.ui.root.after(0, lambda: self._show_info(
                "Success!",
                f"Compilation completed successfully!\n\nOutput file: {output_path}\n"
                f"Files compiled: {success_count}\nOutput size: {size_str}",
                "Your codebase is ready for review!"
            ))
        self.queue.put(('progress_complete', None))
    
    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == 'add_item':
                    self.ui.add_tree_item(
                        item_id=data['item_id'],
                        parent_id=data['parent_id'],
                        text=data['text'],
                        values=data['values'],
                        tags=data['tags']
                    )
                elif msg_type == 'loading_progress':
                    self.ui.set_status(data)
                elif msg_type == 'loading_complete':
                    self.is_loading = False
                    self.ui.show_normal_state()
                    self.ui.set_buttons_state(True)
                    self.ui.set_file_count(data['total_folders'], data['total_files'])
                    self.ui.set_status(f"Loaded folder: {self.current_folder.name}")
                elif msg_type == 'loading_cancelled':
                    self.is_loading = False
                    self.ui.show_normal_state()
                    self.ui.set_buttons_state(True)
                    self.ui.set_status("Loading cancelled")
                elif msg_type == 'loading_error':
                    self.is_loading = False
                    self.ui.show_normal_state()
                    self.ui.set_buttons_state(True)
                    self.ui.set_status("Error loading folder", is_error=True)
                    self._show_error("Error", f"Failed to load folder: {data}")
                elif msg_type == 'status':
                    self.ui.set_status(data)
                elif msg_type == 'progress':
                    self.ui.show_progress(data)
                elif msg_type == 'progress_complete':
                    self.ui.show_progress(100)
                elif msg_type == 'success':
                    self.ui.set_status(data)
                elif msg_type == 'error':
                    self.ui.set_status(data, is_error=True)
        except queue.Empty:
            pass
        finally:
            if self.ui:
                self.ui.root.after(50, self._process_queue)
    
    # --- Dialog helpers ---
    def _show_info(self, title, message, details=None):
        InfoDialog(self.ui.root, COLORS, title, message, details).show()
    
    def _show_warning(self, title, message, details=None):
        WarningDialog(self.ui.root, COLORS, title, message, details).show()
    
    def _show_error(self, title, message, details=None):
        ErrorDialog(self.ui.root, COLORS, title, message, details).show()