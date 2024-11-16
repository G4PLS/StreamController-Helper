import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from .Manager import AssetManager
from .Preview import IconPreview, ColorPreview

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
            self.asset_manager.change_icon_by_path(preview.name, file_path, True)
            self.asset_manager.add_change_icon_override(preview.name, file_path)

            image = self.asset_manager.get_rendered_icon(preview.name)
            preview.set_image(image)

    # Color

    def on_color_clicked(self, flow_box, preview: ColorPreview):
        color_dialog = Gtk.ColorDialog.new()
        color_dialog.set_title("Color")

        # Open the dialog
        color_dialog.choose_rgba(self, preview.get_rgba(), None, self.on_color_dialog_response, preview)

    def on_color_dialog_response(self, dialog: Gtk.ColorDialog, task: Gio.Task, preview: ColorPreview):
        rgba = dialog.choose_rgba_finish(task)
        preview.set_color_rgba(rgba)
        self.asset_manager.change_color(preview.name, preview.color)
        self.asset_manager.add_change_color_override(preview.name, preview.color)

    #
    # DISPLAY
    #

    def display_previews(self):
        self.asset_manager.render_all_icons(True)
        icons = self.asset_manager.get_rendered_icons()

        for name, icon in icons.items():
            preview = IconPreview(name=name, image=icon, size=(100, 100), vexpand=False, hexpand=False)
            self.icon_flow_box.append(preview)

    def display_colors(self):
        colors = self.asset_manager.get_colors()

        for name, color in colors.items():
            preview = ColorPreview(name=name, color=color, size=(100, 100), hexpand=False, vexpand=False)
            self.color_flow_box.append(preview)