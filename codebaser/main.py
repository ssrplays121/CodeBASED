#!/usr/bin/env python3
import tkinter as tk
from ui import MainWindow
from controller import CodebaseController


def main():
    """Main application entry point."""
    root = tk.Tk()
    controller = CodebaseController(None)   # create controller without UI
    ui = MainWindow(root, controller)       # create UI with controller reference
    controller.set_ui(ui)                   # now give controller the UI
    ui.build_ui()                           # build UI (buttons now have valid controller)
    root.mainloop()


if __name__ == "__main__":
    main()