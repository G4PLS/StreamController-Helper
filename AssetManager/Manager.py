import asyncio
import json
import os.path

from src.backend.DeckManagement.Media.Media import Media
from PIL.Image import Image

class Observer:
    def __init__(self):
        self.observers: list = []

    def subscribe(self, observer: callable):
        if observer not in self.observers:
            self.observers.append(observer)

    def unsubscribe(self, observer: callable):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._notify(*args, **kwargs))

    async def _notify(self, *args, **kwargs):
        coroutines = [self._ensure_coroutine(observer, *args, **kwargs) for observer in self.observers]
        await asyncio.gather(*coroutines)

    async def _ensure_coroutine(self, callback: callable, *args, **kwargs):
        if asyncio.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        else:
            try:
                return await asyncio.to_thread(callback, *args, **kwargs)
            except Exception as e:
                #log.error(f"Callback {callback.__name__} in {self.event_id} could not be called")
                return await asyncio.sleep(0)


class AssetManager:
    COLORS_KEY = "colors"
    ICONS_KEY = "icons"

    def __init__(self, override_path: str, pre_render_all_icons: bool = False, fallback_color: tuple[int, int, int, int] = (0,0,0,0)):
        self.colors: dict[str, tuple[int, int, int, int]] = {}
        self.icons: dict[str, Media] = {}
        self.pre_rendered_icons: dict[str, Image] = {}

        # Fallbacks
        self.fallback_color: tuple[int, int, int, int] = fallback_color
        self.fallback_icon: Media = None

        # Globals
        self.pre_render_all_icons: bool = pre_render_all_icons
        self.override_path = override_path
        self.asset_json: dict = {}

        # Observers
        self.color_observer = Observer()
        self.icon_observer = Observer()

        self.load_from_file()

    # Save/Load

    def load_from_file(self):
        if not os.path.isfile(self.override_path):
            return

        with open(self.override_path) as f:
            self.asset_json = json.load(f)

        self.load_colors()
        self.load_icons()

    def load_colors(self):
        colors = self.asset_json.get(self.COLORS_KEY, None)

        if not colors:
            return

        for key, value in colors.items():
            self.add_color(key, tuple(value))

    def load_icons(self):
        icons = self.asset_json.get(self.ICONS_KEY, None)

        if not icons:
            return

        for key, value in icons.items():
            self.add_icon_by_path(key, value)

    def save_asset_json(self):
        with open(self.override_path, "w") as f:
            json.dump(self.asset_json, f, indent=4)

    # Color

    def add_color(self, key: str, color: tuple[int,int,int,int]):
        if not self.colors.__contains__(key):
            self.colors[key] = color

    def remove_color(self, key: str):
        if self.colors.__contains__(key):
            del self.colors[key]

    def change_color(self, key: str, color: tuple[int, int, int, int]):
        if self.colors.__contains__(key):
            del self.colors[key]
            self.colors[key] = color
            self.color_observer.notify(key)

    def add_change_color(self, key: str, color: tuple[int, int, int, int]):
        if self.colors.__contains__(key):
            del self.colors[key]

        self.colors[key] = color

    # Color Overrides

    def has_color_override(self, key):
        colors = self.asset_json.get(self.COLORS_KEY, {})
        return colors.__contains__(key)

    def add_color_override(self, key: str, color: tuple[int, int, int, int]):
        if self.colors.__contains__(key) and not self.has_color_override(key):
            colors = self.asset_json.get(self.COLORS_KEY, {})
            colors[key] = list(color)
            self.asset_json[self.COLORS_KEY] = colors
            self.save_asset_json()

    def remove_color_override(self, key):
        if self.has_color_override(key):
            colors = self.asset_json.get(self.COLORS_KEY, {})
            del colors[key]
            self.asset_json[self.COLORS_KEY] = colors
            self.save_asset_json()

    def change_color_override(self, key: str, color: tuple[int, int, int, int]):
        if self.has_color_override(key):
            colors = self.asset_json.get(self.COLORS_KEY, {})
            colors[key] = list(color)
            self.asset_json[self.COLORS_KEY] = colors
            self.save_asset_json()

    def add_change_color_override(self, key: str, color: tuple[int, int, int, int]):
        colors = self.asset_json.get(self.COLORS_KEY, {})
        colors[key] = list(color)
        self.asset_json[self.COLORS_KEY] = colors
        self.save_asset_json()

    # Icon

    def add_icon(self, key: str, media: Media, pre_render: bool = False):
        if self.icons.__contains__(key):
            return
        self.icons[key] = media

        if pre_render or self.pre_render_all_icons:
            self.pre_rendered_icons[key] = media.get_final_media()

    def add_icon_by_path(self, key: str, icon_path: str, pre_render: bool = False):
        self.add_icon(key, Media.from_path(icon_path), pre_render)

    def remove_icon(self, key: str):
        if self.icons.__contains__(key):
            del self.icons[key]

        if self.pre_rendered_icons.__contains__(key):
            del self.pre_rendered_icons[key]

    def change_icon(self, key: str, media: Media, pre_render: bool = False):
        if self.icons.__contains__(key):
            self.remove_icon(key)
            self.add_icon(key, media, pre_render)
            self.icon_observer.notify(key)

    def change_icon_by_path(self, key: str, icon_path: str, pre_render: bool = False):
        if self.icons.__contains__(key):
            self.remove_icon(key)
            self.add_icon_by_path(key, icon_path, pre_render)
            self.icon_observer.notify(key)

    def add_change_icon(self, key: str, media: Media, pre_render: bool = False):
        if self.icons.__contains__(key):
            del self.icons[key]

        self.icons[key] = media

        if pre_render or self.pre_render_all_icons:
            self.pre_rendered_icons = media.get_final_media()

    def add_change_icon_by_path(self, key: str, path: str, pre_render: bool = False):
        if self.icons.__contains__(key):
            del self.icons[key]

        media = Media.from_path(path)

        self.icons[key] = media

        if pre_render or self.pre_render_all_icons:
            self.pre_rendered_icons = media.get_final_media()

    def render_all_icons(self, skip_current_rendered: bool = False):
        for key, value in self.icons.items():
            if skip_current_rendered and self.pre_rendered_icons.__contains__(key):
                continue
            self.pre_rendered_icons[key] = value.get_final_media()

    # Icon Overrides

    def has_icon_override(self, key):
        icons = self.asset_json.get(self.ICONS_KEY, {})
        return icons.__contains__(key)

    def add_icon_override(self, key: str, icon_path: str):
        if not os.path.isfile(icon_path):
            return

        if self.icons.__contains__(key) and not self.has_icon_override(key):
            icons = self.asset_json.get(self.ICONS_KEY, {})
            icons[key] = icon_path
            self.asset_json[self.ICONS_KEY] = icons
            self.save_asset_json()

    def remove_icon_override(self, key):
        if self.has_icon_override(key):
            icons = self.asset_json.get(self.ICONS_KEY, {})
            del icons[key]
            self.asset_json[self.ICONS_KEY] = icons
            self.save_asset_json()

    def change_icon_override(self, key: str, icon_path: str):
        if not os.path.isfile(icon_path):
            return

        if self.has_icon_override(key):
            icons = self.asset_json.get(self.ICONS_KEY, {})
            icons[key] = icon_path
            self.asset_json[self.ICONS_KEY] = icons
            self.save_asset_json()

    def add_change_icon_override(self, key: str, icon_path: str):
        if not os.path.isfile(icon_path):
            return

        icons = self.asset_json.get(self.ICONS_KEY, {})
        icons[key] = icon_path
        self.asset_json[self.ICONS_KEY] = icons
        self.save_asset_json()

    # Getter

    def get_color(self, key: str):
        return self.colors.get(key, self.fallback_color)

    def get_icon(self, key: str):
        return self.icons.get(key, self.fallback_icon)

    def get_rendered_icon(self, key: str):
        if not self.pre_rendered_icons.__contains__(key):
            return None

        icon = self.pre_rendered_icons.get(key, self.icons.get(key).get_final_media())

        if icon is None:
            icon = self.fallback_icon

        return icon

    def get_icons(self):
        return self.icons

    def get_rendered_icons(self):
        return self.pre_rendered_icons

    def get_colors(self):
        return self.colors

    # Observer

    def subscribe_icon_change(self, callback: callable):
        self.icon_observer.subscribe(callback)

    def unsubscribe_icon_change(self, callback: callable):
        self.icon_observer.subscribe(callback)

    def subscribe_color_change(self, callback: callable):
        self.color_observer.subscribe(callback)

    def unsubscribe_color_change(self, callback: callable):
        self.color_observer.unsubscribe(callback)