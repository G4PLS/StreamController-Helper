"""
Author: G4PLS
Year: 2024

This adds a new UI element which can execute different things based on the selection.
To add a new entry you just have to add the ComboActionItem with any given callback and it will be executed when calling
trigger_item_callback.

The best usecase for this is to use the ComboActionRow to send back the item-changed event and handle most of the
things inside the actual action.
"""

from GtkHelper.GtkHelper import ComboRow

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject

class ComboActionItem:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

class ComboActionRow(ComboRow):
    __gsignals__ = {
        'item-changed': (GObject.SignalFlags.RUN_FIRST, None, (str,int,)) # Item, Index
    }

    def __init__(self, title: str, **kwargs):
        super().__init__(title=title, model=Gtk.ListStore.new([str, int]), **kwargs)
        self.renderer = Gtk.CellRendererText()
        self.combo_box.pack_start(self.renderer, True)
        self.combo_box.add_attribute(self.renderer, "text", 0)

        self.combo_box.connect("changed", self.combo_box_changed)

        self.items: list[ComboActionItem] = []
        self.current_item: ComboActionItem = None

    def set_model_items(self, items: list[ComboActionItem], selected_index: int = -1):
        self.model.clear()

        if not items:
            return

        self.combo_box.disconnect_by_func(self.combo_box_changed)

        self.items = items

        for i, item in enumerate(items):
            self.model.append([item.name, i])

        if 0 <= selected_index < len(items):
            self.combo_box.set_active(selected_index)

        self.combo_box.connect("changed", self.combo_box_changed)

    def combo_box_changed(self, *args):
        if self.combo_box.get_active() < 0:
            return

        index = self.model[self.combo_box.get_active()][1]
        self.current_item = self.items[index]
        self.emit("item-changed", self.current_item, index)

    def trigger_item_callback(self):
        if self.current_item:
            self.current_item.callback()