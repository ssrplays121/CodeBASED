#!/usr/bin/env python3
"""Compilation engine - aggregates selected files into a single output file."""
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional, Callable

from scanner import format_size


def write_header(outfile, source_root: Path, total_files: int):
    """Write the compilation header."""
    outfile.write("=" * 70 + "\n")
    outfile.write(" " * 10 + "codeBASED COMPILATION ARCHIVE\n")
    outfile.write("=" * 70 + "\n\n")
    outfile.write(f"// Source Directory: {source_root}\n")
    outfile.write(f"// Total Files: {total_files}\n")
    outfile.write(f"// Compiled on: {time.strftime('%Y-%m-%d at %H:%M:%S')}\n")
    outfile.write("=" * 70 + "\n\n")


def write_file_section(outfile, file_path: Path, relative_path: Path) -> Optional[str]:
    """
    Write a single file's content to the output.
    Returns error message if failed, else None.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
            content = infile.read()
        
        stats = file_path.stat()
        file_size = format_size(stats.st_size)
        mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
        
        outfile.write("// " + "=" * 67 + "\n")
        outfile.write(f"// FILE: {relative_path}\n")
        outfile.write(f"// Path: {file_path}\n")
        outfile.write(f"// Size: {file_size}\n")
        outfile.write(f"// Last Modified: {mod_time}\n")
        outfile.write(f"// Lines: {len(content.splitlines())}\n")
        outfile.write("// " + "=" * 67 + "\n\n")
        outfile.write(content)
        outfile.write("\n\n")
        return None
    except Exception as e:
        return f"Error reading {relative_path}: {str(e)}"


def write_footer(outfile, success_count: int, error_count: int, output_path: str):
    """Write compilation footer and summary."""
    outfile.write("=" * 70 + "\n")
    outfile.write(" " * 10 + "COMPILATION COMPLETE\n")
    outfile.write("=" * 70 + "\n\n")
    outfile.write(f"// Summary:\n")
    outfile.write(f"//   Successfully processed: {success_count} files\n")
    outfile.write(f"//   Errors encountered: {error_count} files\n")
    outfile.write(f"//   Total size: {format_size(os.path.getsize(output_path))}\n")
    outfile.write(f"//   Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")


def compile_files(
    file_paths: List[Path],
    output_path: str,
    source_root: Path,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Tuple[int, List[str]]:
    """
    Compile a list of files into a single output file.
    
    Args:
        file_paths: List of Path objects to compile.
        output_path: Destination file path.
        source_root: Root directory for relative path display.
        progress_callback: Function called with (current, total, relative_path).
    
    Returns:
        Tuple (success_count, list_of_error_messages)
    """
    total_files = len(file_paths)
    processed = 0
    errors = []
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        write_header(outfile, source_root, total_files)
        
        for file_path in file_paths:
            relative_path = file_path.relative_to(source_root)
            if progress_callback:
                progress_callback(processed + 1, total_files, str(relative_path))
            
            error = write_file_section(outfile, file_path, relative_path)
            if error:
                errors.append(error)
                outfile.write(f"// ERROR: {error}\n\n")
            processed += 1
        
        write_footer(outfile, processed - len(errors), len(errors), output_path)
        
        if errors:
            outfile.write("\n// " + "!" * 67 + "\n")
            outfile.write("// ERRORS ENCOUNTERED:\n")
            for err in errors[:10]:
                outfile.write(f"//   • {err}\n")
            if len(errors) > 10:
                outfile.write(f"//   ... and {len(errors) - 10} more errors\n")
    
    return processed - len(errors), errors