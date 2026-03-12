
import tkinter as tk
from tkinter import ttk

class CheckboxTreeview(ttk.Treeview):
    """Custom Treeview with checkboxes."""
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        # Create checkbox images
        self._create_checkbox_images()

        # Configure tags for checked/unchecked states
        self.tag_configure("checked", image=self.checked_icon)
        self.tag_configure("unchecked", image=self.unchecked_icon)
        self.tag_configure("mixed", image=self.mixed_icon)

        # Bind click events
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Double-1>", self._handle_double_click)

    def _create_checkbox_images(self):
        """Create checkbox images using canvas."""
        # Create checked icon with custom color
        self.checked_icon = tk.PhotoImage(width=18, height=18)
        # Draw rounded rectangle background
        for x in range(18):
            for y in range(18):
                if 2 <= x <= 15 and 2 <= y <= 15:
                    # Create rounded effect
                    if (x < 4 or x > 13) and (y < 4 or y > 13):
                        self.checked_icon.put("#EBD5AB", (x, y))  # Match background
                    else:
                        self.checked_icon.put("#8BAE66", (x, y))
        
        # Draw check mark
        check_points = [(4, 8), (7, 11), (12, 4), (13, 5), (7, 13), (3, 9)]
        for i in range(len(check_points)-1):
            x1, y1 = check_points[i]
            x2, y2 = check_points[i+1]
            for x in range(min(x1, x2), max(x1, x2)+1):
                for y in range(min(y1, y2), max(y1, y2)+1):
                    self.checked_icon.put("#1B211A", (x, y))

        # Create unchecked icon
        self.unchecked_icon = tk.PhotoImage(width=18, height=18)
        # Draw border
        for x in range(18):
            for y in range(18):
                if 2 <= x <= 15 and 2 <= y <= 15:
                    if x == 2 or x == 15 or y == 2 or y == 15:
                        self.unchecked_icon.put("#628141", (x, y))
                    else:
                        self.unchecked_icon.put("#EBD5AB", (x, y))

        # Create mixed state icon
        self.mixed_icon = tk.PhotoImage(width=18, height=18)
        # Draw border
        for x in range(18):
            for y in range(18):
                if 2 <= x <= 15 and 2 <= y <= 15:
                    if x == 2 or x == 15 or y == 2 or y == 15:
                        self.mixed_icon.put("#8BAE66", (x, y))
                    else:
                        self.mixed_icon.put("#EBD5AB", (x, y))
        
        # Draw horizontal line
        for x in range(5, 13):
            self.mixed_icon.put("#1B211A", (x, 8))
            self.mixed_icon.put("#1B211A", (x, 9))

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
        all_unchecked = all("unchecked" in self.item(child, "tags") for child in children)

        if all_checked:
            self.item(parent, tags=("checked",))
        elif all_unchecked:
            self.item(parent, tags=("unchecked",))
        else:
            self.item(parent, tags=("mixed",))

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
