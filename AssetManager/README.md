# Asset Manager by G4PLS
You can use all files as-is in your project. When creating the UI you want to Include the AssetManagerWindow.

## Adding Assets
To add assets you firstly want to choose if the asset is an Icon or a Color.
The Asset Manager contains two variables `icons` and `colors`.
- Color: `self.asset_manager.colors.add_asset("black", Color(color=(0,0,0,0)))`
- Icon: `self.asset_manager.icons.add_asset("mute", Icon(path=os.path.join(self.PATH, "assets", "mute.png")))`

Its important that you add the `color=` or `path=` because the way to instantiate the Assets is quite generic and handled by the assets.

## Removing Assets
To remove assets its a simple as doing: `self.asset_manager.icons.remove_asset("mute")`

## Changing Assets
You have to options to change an asset. You can either change its internal values or replace it.

### Replacing internal Values
- Color: `self.asset_manager.colors.change_asset("black", color=(255, 0, 255, 255))`
- Icon: `self.asset_manager.icons.change_asset("mute", path="/home/user/pictures/test.png")`

The `color=` and `path=` is again important for the values to be set correctly.

### Swapping out the Asset
- Color: `self.asset_manager.colors.add_asset("black", Color(color=(0,0,0,0)), True)`
- Icon: `self.asset_manager.icons.add_asset("mute", Icon(path=os.path.join(self.PATH, "assets", "mute.png")), True)`

By adding the True we say that we want to just override any asset that may exist, if it doesnt exist it just gets added

## Overrides
Every manager also contains overrides, those overrides will be used when you "modify" an asset with the included Window.
This is to ensure that the original values stay the same while there are overrides that will be used.

Those overrides will also be saved and loaded into a json file.

The method names are the same as for the assets except its `override` instead of asset. 
Example: `add_override()`

## Getting Values
To get Values you have multiple choices:
- `get_asset(key, skip_override) -> Asset | None`
- `get_asset_values(key, skip_override) -> Values of the Asset`
- `get_assets() -> MappingProxyType[str, Asset]`
- `get_overrides() -> MappingProxyType[str, Asset]`
- `get_assets_merged() -> MappingProxyType[str, Asset]`

By default, it will first look if an override exists and return that, thats why you can set `skip_override=True` to only look at normal assets

The MappingProxyType ensures that the return dictionaries cant be modified. To modify them you should use the included methods

## Events
Every Manager has its own Observer that you can subscribe to. This is so you can do things if assets get changed.

- Color: `self.asset_manager.colors.add_listener(self.color_changed)`
- Icon: `self.asset_manager.icons.add_listener(self.icon_changed)`

| **Event**          | **Emits On**             | **Passed Values**            |
|---------------------|--------------------------|-----------------------------|
| **ADD**            | `add_asset()`           | `Event, key, asset`           |
| **REMOVE**         | `remove_asset()`        | `Event, key`                  |
| **CHANGE**         | `change_asset()`        | `Event, key, override, values`|
| **OVERRIDE_ADD**   | `add_override()`        | `Event, key, asset`           |
| **OVERRIDE_REMOVE**| `remove_override()`     | `Event, key`                  |
| **OVERRIDE_CHANGE**| `change_override()`     | `Event, key, override, values`|