
import time
import os
from ..utils.helpers import format_size

class CodebaseCompiler:
    """Core logic for compiling files."""
    
    def __init__(self, callback_queue=None):
        self.callback_queue = callback_queue

    def compile_files(self, files, full_output_path, root_folder):
        """Compile list of files into a single output file."""
        try:
            total_files = len(files)
            processed = 0
            errors = []

            with open(full_output_path, 'w', encoding='utf-8') as outfile:
                # Write header
                outfile.write("=" * 70 + "\n")
                outfile.write(" " * 10 + "codeBASED COMPILATION ARCHIVE\n")
                outfile.write("=" * 70 + "\n\n")
                outfile.write(f"// Source Directory: {root_folder}\n")
                outfile.write(f"// Output File: {full_output_path}\n")
                outfile.write(f"// Total Files: {total_files}\n")
                outfile.write(f"// Compiled on: {time.strftime('%Y-%m-%d at %H:%M:%S')}\n")
                outfile.write("=" * 70 + "\n\n")

                for file_path in files:
                    processed += 1
                    relative_path = file_path.relative_to(root_folder)

                    # Update progress via queue
                    if self.callback_queue:
                        progress = (processed / total_files) * 100
                        self.callback_queue.put(('progress', progress))
                        self.callback_queue.put(('status', f"Processing {processed}/{total_files}: {relative_path}"))

                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                            content = infile.read()
                        
                        # Get file stats
                        stats = file_path.stat()
                        file_size = format_size(stats.st_size)
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
                outfile.write(f"//   Total size: {format_size(os.path.getsize(full_output_path))}\n")
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
                if self.callback_queue:
                    self.callback_queue.put(('error', f"Completed with {len(errors)} errors"))
                    # Can pass data back for UI to display detail dialog
                    # but simple string message is good for now, or a dict.
                    # Let's keep it simple as string for 'error' type for now as in old code
            else:
                if self.callback_queue:
                    self.callback_queue.put(('success', f"Successfully compiled {total_files} files"))
        
        except Exception as e:
            if self.callback_queue:
                self.callback_queue.put(('error', f"Compilation failed: {str(e)}"))
        finally:
            if self.callback_queue:
                self.callback_queue.put(('progress_complete', None))
