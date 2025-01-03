"""
Author: G4PLS
Year: 2024
"""

import enum
import json
from types import MappingProxyType

from .Observer import Observer

class Asset:
    def __init__(self, *args, **kwargs):
        self.change(*args, **kwargs)

    def change(self, *args, **kwargs):
        pass

    def get_values(self):
        pass

    def to_json(self):
        pass

    @classmethod
    def from_json(cls, *args):
        return None

class ManagerEvent(enum.Enum):
    ADD = "add",
    REMOVE = "remove,"
    CHANGE = "change",
    OVERRIDE_ADD = "override_add",
    OVERRIDE_REMOVE = "override_remove",
    OVERRIDE_CHANGE = "override_change"

class Manager:
    def __init__(self, asset_type: type, json_key: str):
        self._asset_type: type = asset_type
        self._assets: dict[str, asset_type] = {}
        self._asset_overrides: dict[str, asset_type] = {}
        self._observer = Observer()
        self._json_key = json_key

    # Assets

    def add_asset(self, key: str, asset: Asset, override: bool = False):
        if not self._assets.__contains__(key) or override:
            self._assets[key] = asset
            self._observer.notify(ManagerEvent.ADD, key, asset)

    def remove_asset(self, key: str):
        if self._assets.__contains__(key):
            del self._assets[key]
            self._observer.notify(ManagerEvent.REMOVE, key)

    def change_asset(self, key: str, *values):
        if self._assets.__contains__(key):
            asset = self.get_asset(key, skip_override=True)
            asset.change(*values)
            self._assets[key] = asset
            self._observer.notify(ManagerEvent.CHANGE, key, asset, {values: values})

    # Overrides

    def add_override(self, key: str, asset: Asset, skip_asset_check: bool = False, override: bool = False):
        if not self._assets.__contains__(key) and not skip_asset_check:
            return

        if not self._asset_overrides.__contains__(key) or override:
            self._asset_overrides[key] = asset
            self._observer.notify(ManagerEvent.OVERRIDE_ADD, key, asset)

    def remove_override(self, key: str):
        if self._asset_overrides.__contains__(key):
            del self._asset_overrides[key]
            self._observer.notify(ManagerEvent.OVERRIDE_REMOVE, key)

    def change_override(self, key: str, *values):
        if self._asset_overrides.__contains__(key):
            override = self.get_asset(key)
            override.change(*values)
            self._asset_overrides[key] = override
            self._observer.notify(ManagerEvent.OVERRIDE_CHANGE, key, override, {"values": values})

    # Getter

    def get_asset(self, key: str, skip_override: bool = False) -> Asset | None:
        """
        Returns the Override before the Asset if it exists
        :param key: The key of said asset
        :param skip_override: When set the Normal asset will always be returned without looking at overrides
        :return: Returns an Asset or None
        """
        if skip_override:
            return self._assets.get(key, None)
        return self._asset_overrides.get(key, self._assets.get(key, None))

    def get_asset_values(self, key: str, skip_override: bool = False):
        asset = self.get_asset(key, skip_override)
        return asset.get_values()

    def get_assets(self) -> MappingProxyType[str, Asset]:
        return MappingProxyType(self._assets)

    def get_overrides(self) -> MappingProxyType[str, Asset]:
        return MappingProxyType(self._asset_overrides)

    def get_assets_merged(self) -> MappingProxyType[str, Asset]:
        combined = {**self._assets, **self._asset_overrides}
        return MappingProxyType(combined)

    # Observer

    def add_listener(self, callback: callable):
        self._observer.subscribe(callback)

    def remove_listener(self, callback: callable):
        self._observer.unsubscribe(callback)

    # Save/Load

    def get_asset_json(self):
        return json.dumps({key: asset.to_json() for key, asset in self._assets.items()}, indent=4)

    def get_override_json(self):
        out = {}

        for key, asset in self._asset_overrides.items():
            out[key] = asset.to_json()
        return out

    def load_json(self, json_data: dict):
        json = json_data.get(self._json_key, None)

        if not json:
            return

        for key, value in json.items():
            self.add_override(key, self._asset_type.from_json(value), skip_asset_check=True)

    def get_save_key(self):
        return self._json_key