
import tkinter as tk
from tkinter import ttk

class CustomDialog:
    """Base class for custom dialog boxes following the app theme."""
    
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.result = None
        
        # Create top level window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("")
        self.dialog.configure(bg=self.colors['background'])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        self.dialog.focus_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _on_close(self):
        """Handle dialog close."""
        self.result = False
        self.dialog.destroy()
        
    def center_on_parent(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


class InfoDialog(CustomDialog):
    """Custom information dialog."""
    
    def __init__(self, parent, colors, title, message, details=None):
        super().__init__(parent, colors)
        self.dialog.title(title)
        
        # Configure dialog grid with centered content
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(self.dialog, bg=self.colors['primary'], height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            header_frame,
            text="ℹ️  " + title,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            anchor='center'
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # Message content - centered with uniform margins
        content_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        content_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Main message - centered text with word wrapping
        message_label = tk.Label(
            content_frame,
            text=message,
            font=('Segoe UI', 11),
            bg=self.colors['background'],
            fg=self.colors['accent'],
            wraplength=380,  # Reduced to account for padding
            justify=tk.CENTER,
            anchor='center'
        )
        message_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Details if provided - centered text
        if details:
            details_label = tk.Label(
                content_frame,
                text=details,
                font=('Segoe UI', 9),
                bg=self.colors['background'],
                fg=self.colors['text_secondary'],
                wraplength=380,  # Reduced to account for padding
                justify=tk.CENTER,
                anchor='center'
            )
            details_label.grid(row=1, column=0, sticky="ew", pady=(5, 15))
        
        # Button frame - centered
        button_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # OK button - centered
        button_container = tk.Frame(button_frame, bg=self.colors['background'])
        button_container.pack(expand=True)
        
        ok_button = tk.Button(
            button_container,
            text="OK",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_ok,
            width=15
        )
        ok_button.pack(pady=5, ipadx=20, ipady=6)
        
        # Set focus to OK button
        ok_button.focus_set()
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_close())
        
        # Center and show
        self.dialog.update_idletasks()
        self.center_on_parent()
        
    def _on_ok(self):
        """Handle OK button click."""
        self.result = True
        self.dialog.destroy()
        
    def show(self):
        """Show the dialog and wait for response."""
        self.parent.wait_window(self.dialog)
        return self.result


class WarningDialog(CustomDialog):
    """Custom warning dialog."""
    
    def __init__(self, parent, colors, title, message, details=None):
        super().__init__(parent, colors)
        self.dialog.title(title)
        
        # Configure dialog grid with centered content
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(self.dialog, bg=self.colors['warning'], height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            header_frame,
            text="⚠️  " + title,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['warning'],
            fg=self.colors['background'],
            anchor='center'
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # Message content - centered with uniform margins
        content_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        content_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Main message - centered text with word wrapping
        message_label = tk.Label(
            content_frame,
            text=message,
            font=('Segoe UI', 11),
            bg=self.colors['background'],
            fg=self.colors['accent'],
            wraplength=380,  # Reduced to account for padding
            justify=tk.CENTER,
            anchor='center'
        )
        message_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Details if provided - centered text
        if details:
            details_label = tk.Label(
                content_frame,
                text=details,
                font=('Segoe UI', 9),
                bg=self.colors['background'],
                fg=self.colors['text_secondary'],
                wraplength=380,  # Reduced to account for padding
                justify=tk.CENTER,
                anchor='center'
            )
            details_label.grid(row=1, column=0, sticky="ew", pady=(5, 15))
        
        # Button frame - centered
        button_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # OK button - centered
        button_container = tk.Frame(button_frame, bg=self.colors['background'])
        button_container.pack(expand=True)
        
        ok_button = tk.Button(
            button_container,
            text="OK",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_ok,
            width=15
        )
        ok_button.pack(pady=5, ipadx=20, ipady=6)
        
        # Set focus to OK button
        ok_button.focus_set()
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_close())
        
        # Center and show
        self.dialog.update_idletasks()
        self.center_on_parent()
        
    def _on_ok(self):
        """Handle OK button click."""
        self.result = True
        self.dialog.destroy()
        
    def show(self):
        """Show the dialog and wait for response."""
        self.parent.wait_window(self.dialog)
        return self.result


class ErrorDialog(CustomDialog):
    """Custom error dialog."""
    
    def __init__(self, parent, colors, title, message, details=None):
        super().__init__(parent, colors)
        self.dialog.title(title)
        
        # Configure dialog grid with centered content
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(self.dialog, bg=self.colors['error'], height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            header_frame,
            text="❌  " + title,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['error'],
            fg='white',
            anchor='center'
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # Message content - centered with uniform margins
        content_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        content_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Main message - centered text with word wrapping
        message_label = tk.Label(
            content_frame,
            text=message,
            font=('Segoe UI', 11),
            bg=self.colors['background'],
            fg=self.colors['accent'],
            wraplength=380,  # Reduced to account for padding
            justify=tk.CENTER,
            anchor='center'
        )
        message_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Details if provided - centered text
        if details:
            details_label = tk.Label(
                content_frame,
                text=details,
                font=('Segoe UI', 9),
                bg=self.colors['background'],
                fg=self.colors['text_secondary'],
                wraplength=380,  # Reduced to account for padding
                justify=tk.CENTER,
                anchor='center'
            )
            details_label.grid(row=1, column=0, sticky="ew", pady=(5, 15))
        
        # Button frame - centered
        button_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # OK button - centered
        button_container = tk.Frame(button_frame, bg=self.colors['background'])
        button_container.pack(expand=True)
        
        ok_button = tk.Button(
            button_container,
            text="OK",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_ok,
            width=15
        )
        ok_button.pack(pady=5, ipadx=20, ipady=6)
        
        # Set focus to OK button
        ok_button.focus_set()
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_close())
        
        # Center and show
        self.dialog.update_idletasks()
        self.center_on_parent()
        
    def _on_ok(self):
        """Handle OK button click."""
        self.result = True
        self.dialog.destroy()
        
    def show(self):
        """Show the dialog and wait for response."""
        self.parent.wait_window(self.dialog)
        return self.result


class ConfirmDialog(CustomDialog):
    """Custom confirmation dialog with Yes/No options."""
    
    def __init__(self, parent, colors, title, message, details=None):
        super().__init__(parent, colors)
        self.dialog.title(title)
        
        # Configure dialog grid with centered content
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(self.dialog, bg=self.colors['secondary'], height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            header_frame,
            text="❓  " + title,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['background'],
            anchor='center'
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # Message content - centered with uniform margins
        content_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        content_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Main message - centered text with word wrapping
        message_label = tk.Label(
            content_frame,
            text=message,
            font=('Segoe UI', 11),
            bg=self.colors['background'],
            fg=self.colors['accent'],
            wraplength=380,  # Reduced to account for padding
            justify=tk.CENTER,
            anchor='center'
        )
        message_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Details if provided - centered text
        if details:
            details_label = tk.Label(
                content_frame,
                text=details,
                font=('Segoe UI', 9),
                bg=self.colors['background'],
                fg=self.colors['text_secondary'],
                wraplength=380,  # Reduced to account for padding
                justify=tk.CENTER,
                anchor='center'
            )
            details_label.grid(row=1, column=0, sticky="ew", pady=(5, 15))
        
        # Button frame - centered
        button_frame = tk.Frame(self.dialog, bg=self.colors['background'])
        button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Center buttons container
        button_container = tk.Frame(button_frame, bg=self.colors['background'])
        button_container.pack(expand=True)
        
        # Yes button
        yes_button = tk.Button(
            button_container,
            text="Yes",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['background'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_yes,
            width=12
        )
        yes_button.pack(side=tk.LEFT, padx=(0, 10), pady=5, ipadx=15, ipady=6)
        
        # No button
        no_button = tk.Button(
            button_container,
            text="No",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['divider'],
            fg=self.colors['accent'],
            activebackground=self.colors['surface'],
            activeforeground=self.colors['accent'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_no,
            width=12
        )
        no_button.pack(side=tk.LEFT, padx=(10, 0), pady=5, ipadx=15, ipady=6)
        
        # Set focus to Yes button
        yes_button.focus_set()
        self.dialog.bind('<Return>', lambda e: self._on_yes())
        self.dialog.bind('<Escape>', lambda e: self._on_no())
        self.dialog.bind('<y>', lambda e: self._on_yes())
        self.dialog.bind('<Y>', lambda e: self._on_yes())
        self.dialog.bind('<n>', lambda e: self._on_no())
        self.dialog.bind('<N>', lambda e: self._on_no())
        
        # Center and show
        self.dialog.update_idletasks()
        self.center_on_parent()
        
    def _on_yes(self):
        """Handle Yes button click."""
        self.result = True
        self.dialog.destroy()
        
    def _on_no(self):
        """Handle No button click."""
        self.result = False
        self.dialog.destroy()
        
    def show(self):
        """Show the dialog and wait for response."""
        self.parent.wait_window(self.dialog)
        return self.result
