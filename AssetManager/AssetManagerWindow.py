"""
Author: G4PLS
Year: 2024
"""
from src.backend.DeckManagement.ImageHelpers import image2pixbuf
from .Preview import AssetPreview
from .AssetManager import AssetManager, Icon, Color

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, Pango, Gdk

class IconPreview(AssetPreview):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image = image
        self.pixbuf = image2pixbuf(image)
        self.build()

    def scale_pixbuf(self):
        original_width = self.pixbuf.get_width()
        original_height = self.pixbuf.get_height()
        w = self.size[0]
        h = self.size[1]

        scale = min(w / original_width, h / original_height)

        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        return self.pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)

    def build(self):
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.set_size_request(self.size[0], self.size[1])
        self.set_child(self.main_box)

        self.picture = Gtk.Picture(width_request=self.size[0], height_request=self.size[1], overflow=Gtk.Overflow.HIDDEN,
                                   content_fit=Gtk.ContentFit.COVER,
                                   hexpand=False, vexpand=False, keep_aspect_ratio=True)
        self.picture.set_pixbuf(self.scale_pixbuf())

        self.main_box.append(self.picture)

        self.label = Gtk.Label(label=self.name, xalign=Gtk.Align.CENTER, hexpand=False, ellipsize=Pango.EllipsizeMode.END,
                               max_width_chars=20,
                               margin_start=20, margin_end=20)
        self.main_box.append(self.label)

        self.set_size_request(self.size[0], self.size[1])

    def set_image(self, image):
        self.image = image
        self.pixbuf = image2pixbuf(self.image)
        self.picture.set_pixbuf(self.scale_pixbuf())

class ColorPreview(AssetPreview):
    def __init__(self, color: tuple[int, int, int, int], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color = color
        self.build()

    def build(self):
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.set_size_request(self.size[0], self.size[1])
        self.set_child(self.main_box)

        self.color_button = Gtk.ColorButton(title="Pick Color")
        self.color_button.set_sensitive(False)
        self.set_color(self.color)
        self.color_button.set_size_request(self.size[0], self.size[1])

        self.main_box.append(self.color_button)

        self.label = Gtk.Label(label=self.name, xalign=Gtk.Align.CENTER, hexpand=False, ellipsize=Pango.EllipsizeMode.END,
                               max_width_chars=20,
                               margin_start=20, margin_end=20)
        self.main_box.append(self.label)

        self.set_size_request(self.size[0], self.size[1])

    def set_color(self, color: tuple[int, int, int, int]):
        self.color = color
        self.color_button.set_rgba(self.get_rgba())

    def set_color_rgba(self, color: Gdk.RGBA):
        self.color = (int(color.red * 255), int(color.green * 255), int(color.green * 255), int(color.alpha * 255))
        self.color_button.set_rgba(color)

    def get_rgba(self):
        rgba = Gdk.RGBA()
        rgba.red = self.color[0] / 255
        rgba.green = self.color[1] / 255
        rgba.blue = self.color[2] / 255
        rgba.alpha = self.color[3] / 255
        return rgba

class AssetManagerWindow(Adw.PreferencesWindow):
    def __init__(self, asset_manager: AssetManager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_manager = asset_manager
        self.set_size_request(500, 500)

        self.add(self.build_icon_chooser())
        self.add(self.build_color_chooser())

        self.display_previews()
        self.display_colors()

        self.connect_events()

        self.show()

    def build_icon_chooser(self):
        page = Adw.PreferencesPage(title="Icon")
        group = Adw.PreferencesGroup(title="Icon Settings")
        page.add(group)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        group.add(main_box)

        self.icon_search_entry = Gtk.SearchEntry()
        self.icon_search_entry.set_placeholder_text("Search icons...")
        main_box.append(self.icon_search_entry)

        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

        self.icon_flow_box = Gtk.FlowBox(hexpand=True, orientation=Gtk.Orientation.HORIZONTAL,
                                    selection_mode=Gtk.SelectionMode.SINGLE, valign=Gtk.Align.START)
        self.icon_flow_box.set_max_children_per_line(3)

        scrolled_window.set_child(self.icon_flow_box)

        bin_wrapper = Adw.Bin()
        bin_wrapper.set_child(scrolled_window)
        group.add(bin_wrapper)

        return page

    def build_color_chooser(self):
        page = Adw.PreferencesPage(title="Color")
        group = Adw.PreferencesGroup(title="Color Settings")
        page.add(group)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        group.add(main_box)

        self.color_search_entry = Gtk.SearchEntry()
        self.color_search_entry.set_placeholder_text("Search colors...")
        main_box.append(self.color_search_entry)

        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

        self.color_flow_box = Gtk.FlowBox(hexpand=True, orientation=Gtk.Orientation.HORIZONTAL,
                                    selection_mode=Gtk.SelectionMode.SINGLE, valign=Gtk.Align.START)
        self.color_flow_box.set_max_children_per_line(3)

        scrolled_window.set_child(self.color_flow_box)

        bin_wrapper = Adw.Bin()
        bin_wrapper.set_child(scrolled_window)
        group.add(bin_wrapper)

        return page

    #
    # EVENTS
    #

    def connect_events(self):
        self.icon_flow_box.connect("child-activated", self.on_icon_clicked)
        self.color_flow_box.connect("child-activated", self.on_color_clicked)

    # Icon

    def on_icon_clicked(self, flow_box, preview: IconPreview):
        icon_dialog = Gtk.FileDialog.new()
        icon_dialog.set_title("Icon")

        icon_dialog.open(self, None, self.on_icon_dialog_response, preview)

    def on_icon_dialog_response(self, dialog: Gtk.FileDialog, task, preview: IconPreview):
        file = dialog.open_finish(task)

        if file:
            file_path = file.get_path()
            self.asset_manager.icons.add_override(preview.name, Icon(path=file_path), override=True)

            _, render = self.asset_manager.icons.get_asset_values(preview.name)
            preview.set_image(render)
            self.asset_manager.save()

    # Color

    def on_color_clicked(self, flow_box, preview: ColorPreview):
        color_dialog = Gtk.ColorDialog.new()
        color_dialog.set_title("Color")

        # Open the dialog
        color_dialog.choose_rgba(self, preview.get_rgba(), None, self.on_color_dialog_response, preview)

    def on_color_dialog_response(self, dialog: Gtk.ColorDialog, task: Gio.Task, preview: ColorPreview):
        rgba = dialog.choose_rgba_finish(task)
        preview.set_color_rgba(rgba)
        self.asset_manager.colors.add_override(preview.name, Color(color=preview.color), override=True)
        self.asset_manager.save()

    #
    # DISPLAY
    #

    def display_previews(self):
        icons = self.asset_manager.icons.get_assets_merged()

        for name, icon in icons.items():
            _, render = icon.get_values()

            preview = IconPreview(name=name, image=render, size=(100, 100), vexpand=False, hexpand=False)
            self.icon_flow_box.append(preview)

    def display_colors(self):
        colors = self.asset_manager.colors.get_assets_merged()

        for name, color in colors.items():
            color = color.get_values()
            preview = ColorPreview(name=name, color=color, size=(100, 100), hexpand=False, vexpand=False)
            self.color_flow_box.append(preview)