"""
Author: G4PLS
Year: 2024
"""

import gi

from src.backend.DeckManagement.ImageHelpers import image2pixbuf

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk

class AssetPreview(Gtk.FlowBoxChild):
    def __init__(self, name: str, size: tuple[int, int] = (50,50), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_css_classes(["asset-preview"])
        self.set_margin_start(5)
        self.set_margin_end(5)
        self.set_margin_top(5)
        self.set_margin_bottom(5)

        self.name = name
        self.size = size

        self.set_size_request(self.size[0], self.size[1])

    def build(self):
        pass