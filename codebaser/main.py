#!/usr/bin/env python3
import tkinter as tk
from app import CodebaseCompilerApp


def main():
    """Main application entry point."""
    root = tk.Tk()
    app = CodebaseCompilerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()