#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk


class CheckboxTreeview(ttk.Treeview):
    """Custom Treeview with checkboxes."""
    def __init__(self, master=None, header_state_callback=None, **kw):
        super().__init__(master, **kw)

        # Create checkbox images
        self.header_state_callback = header_state_callback
        self._create_checkbox_images()

        # Configure tags for checked/unchecked states
        self.tag_configure("checked", image=self.checked_icon)
        self.tag_configure("unchecked", image=self.unchecked_icon)
        self.tag_configure("mixed", image=self.mixed_icon)

        # Bind click events
        self.bind("<Button-1>", self._handle_click)
        # Bind events for expanding/collapsing folders to update header checkbox state
        self.bind('<<TreeviewOpen>>', self._on_visibility_changed)
        self.bind('<<TreeviewClose>>', self._on_visibility_changed)

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

    def _set_check_state(self, item, state):
        tags = list(self.item(item, "tags"))
        tags = [t for t in tags if t not in ("checked", "unchecked", "mixed")]
        tags.append(state)
        self.item(item, tags=tuple(tags))

    def set_header_checkbox(self, state):
        state = state or "unchecked"
        image = {
            "checked": self.checked_icon,
            "mixed": self.mixed_icon,
            "unchecked": self.unchecked_icon
        }.get(state, self.unchecked_icon)
        self.heading("#0", image=image, text="  File/Folder", anchor=tk.W)
        self._header_state = state
        if self.header_state_callback:
            self.header_state_callback(state)

    def update_header_checkbox(self):
        root_children = self.get_children()
        if not root_children:
            state = "unchecked"
        else:
            all_checked = all("checked" in self.item(c, "tags") for c in root_children)
            any_checked = any(
                "checked" in self.item(c, "tags") or "mixed" in self.item(c, "tags")
                for c in root_children
            )
            if all_checked:
                state = "checked"
            elif not any_checked:
                state = "unchecked"
            else:
                state = "mixed"
        self.set_header_checkbox(state)

    def set_item_check_state(self, item, checked):
        self._set_check_state(item, "checked" if checked else "unchecked")

    def _handle_click(self, event):
        region = self.identify("region", event.x, event.y)
        if region != "tree":
            return
        item = self.identify("item", event.x, event.y)
        if not item:
            return

        element = self.identify_element(event.x, event.y)
        tags = self.item(item, "tags")
        is_folder = "folder" in tags
        is_file = "file" in tags

        # Folder: any click except checkbox image toggles open/close
        if is_folder and element != "image":
            self.item(item, open=not self.item(item, "open"))
            self.recolor_visible_rows()
            self.selection_set(item)
            self.focus(item)
            self.see(item)
            return "break"

        # Folder: click on checkbox image toggles check only
        if is_folder and element == "image":
            self.toggle_check(item)
            return "break"

        # File: any click toggles checkbox and selects
        if is_file:
            self.toggle_check(item)
            self.selection_set(item)
            self.focus(item)
            self.see(item)
            return "break"

    def toggle_check(self, item):
        """Toggle checkbox state."""
        current_tags = self.item(item, "tags")
        checked = "checked" not in current_tags
        self._set_check_state(item, "checked" if checked else "unchecked")
        self._propagate_check_state(item, checked)
        self.update_header_checkbox()

    def _propagate_check_state(self, item, checked):
        children = self.get_children(item)
        for child in children:
            self._set_check_state(child, "checked" if checked else "unchecked")
            self._propagate_check_state(child, checked)

        parent = self.parent(item)
        if parent and parent != "":
            self._update_parent_check_state(parent)

    def _update_parent_check_state(self, parent):
        children = self.get_children(parent)
        if not children:
            return

        all_checked = all("checked" in self.item(child, "tags") for child in children)
        any_checked = any(
            "checked" in self.item(child, "tags") or "mixed" in self.item(child, "tags")
            for child in children
        )
        all_unchecked = all("unchecked" in self.item(child, "tags") for child in children)

        if all_checked:
            self._set_check_state(parent, "checked")
        elif all_unchecked:
            self._set_check_state(parent, "unchecked")
        else:
            self._set_check_state(parent, "mixed")

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

    def _iter_all(self, parent=''):
        for child in self.get_children(parent):
            yield child
            yield from self._iter_all(child)

    def _iter_visible(self, parent=''):
        for child in self.get_children(parent):
            yield child
            if self.item(child, 'open'):
                yield from self._iter_visible(child)

    def recolor_visible_rows(self):
        # Remove old row-color tags everywhere
        for item in self._iter_all():
            tags = [t for t in self.item(item, 'tags') if t not in ('evenrow', 'oddrow')]
            self.item(item, tags=tuple(tags))

        # Assign alternating colors to displayed rows only
        even = True
        for item in self._iter_visible():
            tags = list(self.item(item, 'tags'))
            tags.append('evenrow' if even else 'oddrow')
            self.item(item, tags=tuple(tags))
            even = not even

    def _on_visibility_changed(self, _event):
        self.recolor_visible_rows()