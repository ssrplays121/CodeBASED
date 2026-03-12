
import tkinter as tk
from .ui.app import CodebaseCompilerApp

def main():
    """Main application entry point."""
    root = tk.Tk()
    
    # Create application
    app = CodebaseCompilerApp(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
