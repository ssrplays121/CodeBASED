#!/usr/bin/env python3
"""File system scanning and tree data generation."""
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable, Any

from config import ICON_MAP, EXCLUDED_PREFIXES


def get_file_icon(filename: str) -> str:
    """Get appropriate emoji icon for file type."""
    ext = os.path.splitext(filename)[1].lower()
    return ICON_MAP.get(ext, '📄')


def format_size(size_in_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"


class DirectoryScanner:
    """Scans a directory and yields items for tree building."""
    
    def __init__(self, root_path: Path, stop_flag: Callable[[], bool] = None):
        """
        Args:
            root_path: Root directory to scan.
            stop_flag: Callable that returns True if scanning should be cancelled.
        """
        self.root_path = root_path
        self.stop_flag = stop_flag or (lambda: False)
    
    def scan(self, progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Perform the scan and return a dictionary mapping item_id to item info.
        
        Returns:
            Dictionary with keys: 'items' (dict), 'total_folders', 'total_files'
        """
        items = {}
        total_folders = 0
        total_files = 0
        
        # First pass: count items for progress reporting
        if progress_callback:
            progress_callback("Counting files and folders...")
        
        for root, dirs, files in os.walk(self.root_path):
            if self.stop_flag():
                return {'items': {}, 'total_folders': 0, 'total_files': 0, 'cancelled': True}
            
            # Filter out hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(EXCLUDED_PREFIXES)]
            files = [f for f in files if not f.startswith(EXCLUDED_PREFIXES)]
            
            total_folders += len(dirs)
            total_files += len(files)
        
        if progress_callback:
            progress_callback(f"Found {total_folders} folders, {total_files} files. Building tree...")
        
        # Build tree structure
        self._build_items(self.root_path, "", items, progress_callback)
        
        return {
            'items': items,
            'total_folders': total_folders,
            'total_files': total_files,
            'cancelled': False
        }
    
    def _build_items(self, current_path: Path, parent_id: str, items: Dict, 
                     progress_callback: Optional[Callable[[str], None]] = None):
        """Recursively build items dictionary."""
        try:
            # Get all items, filter hidden
            entries = []
            for entry in current_path.iterdir():
                if self.stop_flag():
                    return
                if entry.name.startswith(EXCLUDED_PREFIXES):
                    continue
                entries.append(entry)
            
            # Sort: folders first, then by name
            entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for entry in entries:
                if self.stop_flag():
                    return
                
                item_id = str(hash(entry))
                relative_path = entry.relative_to(self.root_path)
                icon = "📁" if entry.is_dir() else get_file_icon(entry.name)
                display_text = f"{icon} {entry.name}"
                
                size = ""
                modified = ""
                if entry.is_file():
                    try:
                        stat = entry.stat()
                        size = format_size(stat.st_size)
                        modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
                    except:
                        size = "N/A"
                        modified = "N/A"
                
                items[item_id] = {
                    'parent_id': parent_id,
                    'text': display_text,
                    'values': (str(relative_path), size, modified),
                    'is_dir': entry.is_dir(),
                    'path': entry,
                    'relative_path': relative_path
                }
                
                # Recursively add subdirectories
                if entry.is_dir():
                    self._build_items(entry, item_id, items, progress_callback)
                    
        except Exception as e:
            if progress_callback:
                progress_callback(f"Warning: Error accessing {current_path}: {str(e)}")