"""
Author: G4PLS
Year: 2024

This implements the Gtk.Grid as an Adw.PreferencesRow, adding basic method to add/remove/change widgets in the grid.
This is purely visual and has no further purpose other than to make UI look better.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from loguru import logger as log

class AdwGrid(Adw.PreferencesRow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_box = Gtk.Box()
        self.set_child(self.main_box)
        self.main_box.set_hexpand(False)

        self.grid = Gtk.Grid()
        self.grid.set_halign(Gtk.Align.FILL)
        self.grid.set_hexpand(True)
        self.grid.set_column_homogeneous(True)
        self.main_box.append(self.grid)

    def add_widget(self, widget: Gtk.Widget, column: int, row: int, width: int = 1, height: int = 1) -> None:
        """
        Tries to add a widget to a specified row and column, if a widget is already present it cant be added
        """
        if self.grid.get_child_at(column, row):
            log.warning(f"There is already a widget at {column} {row} present {widget}. To replace a widget use replace_widget")
            return

        self.grid.attach(widget, column, row, width, height)

    def replace_widget(self, widget: Gtk.Widget, column: int, row: int, width: int = 1, height: int = 1) -> Gtk.Widget:
        """
        Replaces the Old Widget with a new one
        @return: The old Widget that got replaced
        """
        old_widget = self.grid.get_child_at(column, row)
        self.grid.attach(widget, column, row, width, height)

        return old_widget

    def remove_widget(self, column, row) -> Gtk.Widget:
        """
        Removes a Widget from the Grid and returns the removes widget
        :return: The Widget that got removed
        """
        widget = self.grid.get_child_at(column, row)
        self.grid.remove(widget)
        return widget