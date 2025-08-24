#!/usr/bin/env python3
"""Check available assets in the compiled library."""

import ctypes
import os

lib_path = os.path.join(os.getcwd(), "build/libmadrona_escape_room_c_api.so")
lib = ctypes.CDLL(lib_path)

# Get physics assets count
lib.mer_get_physics_assets_count.argtypes = []
lib.mer_get_physics_assets_count.restype = ctypes.c_int

lib.mer_get_physics_asset_name.argtypes = [ctypes.c_int]
lib.mer_get_physics_asset_name.restype = ctypes.c_char_p

lib.mer_get_physics_asset_object_id.argtypes = [ctypes.c_int]
lib.mer_get_physics_asset_object_id.restype = ctypes.c_int

physics_count = lib.mer_get_physics_assets_count()
print(f"Physics assets count: {physics_count}")

for i in range(physics_count):
    name = lib.mer_get_physics_asset_name(i)
    obj_id = lib.mer_get_physics_asset_object_id(i)
    print(f"  [{i}] Object ID {obj_id}: {name.decode() if name else 'None'}")

# Get render assets count
lib.mer_get_render_assets_count.argtypes = []
lib.mer_get_render_assets_count.restype = ctypes.c_int

lib.mer_get_render_asset_name.argtypes = [ctypes.c_int]
lib.mer_get_render_asset_name.restype = ctypes.c_char_p

lib.mer_get_render_asset_object_id.argtypes = [ctypes.c_int]
lib.mer_get_render_asset_object_id.restype = ctypes.c_int

render_count = lib.mer_get_render_assets_count()
print(f"\nRender assets count: {render_count}")

for i in range(render_count):
    name = lib.mer_get_render_asset_name(i)
    obj_id = lib.mer_get_render_asset_object_id(i)
    print(f"  [{i}] Object ID {obj_id}: {name.decode() if name else 'None'}")