
import os
import time
from pathlib import Path
from ..utils.icons import get_file_icon
from ..utils.helpers import format_size

class FileScanner:
    """Core logic for scanning directories."""
    
    def __init__(self, callback_queue=None):
        self.callback_queue = callback_queue
        self.stop_flag = False

    def scan_directory(self, folder_path):
        """Scan directory and build file structure."""
        file_items = {}
        total_files = 0
        total_folders = 0
        
        try:
            # Initial scan to get counts (fast)
            for root, dirs, files in os.walk(folder_path):
                if self.stop_flag:
                    if self.callback_queue:
                        self.callback_queue.put(('loading_cancelled', None))
                    return
                
                total_folders += len(dirs)
                total_files += len(files)
                
                # Update progress every 1000 items found
                if (total_files + total_folders) % 1000 == 0:
                    if self.callback_queue:
                        self.callback_queue.put(('loading_progress', 
                                       f"Found {total_folders} folders, {total_files} files..."))
            
            if self.callback_queue:
                self.callback_queue.put(('loading_progress', 
                               f"Found {total_folders} folders, {total_files} files. Building tree..."))
            
            # Now build the tree with proper structure
            self._build_tree_structure(folder_path, file_items)
            
            if not self.stop_flag and self.callback_queue:
                self.callback_queue.put(('loading_complete', file_items))
            
        except Exception as e:
            if not self.stop_flag and self.callback_queue:
                self.callback_queue.put(('loading_error', str(e)))

    def _build_tree_structure(self, root_path, file_items):
        """Build tree structure with proper hierarchy."""
        row_index = 0
        
        def add_items(parent_path, parent_id=""):
            nonlocal row_index
            try:
                # Get items and sort (folders first, then files)
                items = []
                for item in parent_path.iterdir():
                    if self.stop_flag:
                        return
                    
                    if item.name.startswith('.'):
                        continue
                    
                    items.append(item)
                
                # Sort: folders first, then by name
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                
                for item in items:
                    if self.stop_flag:
                        return
                    
                    relative_path = item.relative_to(root_path)
                    display_name = item.name
                    icon = "📁" if item.is_dir() else get_file_icon(item.name)

                    # Get file info
                    size = ""
                    modified = ""
                    if item.is_file():
                        try:
                            size = format_size(item.stat().st_size)
                            modified_time = time.localtime(item.stat().st_mtime)
                            modified = time.strftime("%Y-%m-%d %H:%M", modified_time)
                        except:
                            size = "N/A"
                            modified = "N/A"

                    # Insert item with alternating row colors
                    row_tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
                    
                    # Send item through queue
                    if self.callback_queue:
                        self.callback_queue.put(('add_item', {
                            'parent_id': parent_id,
                            'item_id': str(hash(item)),  # Use hash as unique ID
                            'text': f"{icon} {display_name}",
                            'values': (str(relative_path), size, modified),
                            'tags': ("unchecked", row_tag, 'folder' if item.is_dir() else 'file'),
                            'is_dir': item.is_dir(),
                            'path': item,
                            'relative_path': relative_path
                        }))
                    
                    row_index += 1
                    
                    # Update progress every 100 items
                    if row_index % 100 == 0 and self.callback_queue:
                        self.callback_queue.put(('loading_progress', f"Loading... {row_index} items processed"))

                    # Recursively add subdirectories
                    if item.is_dir():
                        add_items(item, str(hash(item)))

            except Exception as e:
                if not self.stop_flag and self.callback_queue:
                    self.callback_queue.put(('loading_warning', f"Error accessing {parent_path}: {str(e)}"))

        # Start building from root
        add_items(root_path)

    def cancel(self):
        """Cancel the scanning process."""
        self.stop_flag = True
