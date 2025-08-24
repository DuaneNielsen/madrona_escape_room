#!/usr/bin/env python3
"""Test the minimal wrapper."""

import sys
sys.path.insert(0, '/home/duane/madrona_escape_room')
sys.path.insert(0, '/home/duane/madrona_escape_room/scratch')
from generated_compiled_level import CompiledLevel
from madrona_escape_room import SimManager

# Create a simple level
level = CompiledLevel()
level.num_tiles = 4
level.num_spawn_points = 1
level.max_entities = 100  # Need to allocate space for entities!

# Just a 2x2 floor
level.spawn_x[0] = 0.0
level.spawn_y[0] = 0.0  
level.spawn_z[0] = 0.0

for i in range(4):
    level.object_ids[i] = 0  # Floor
    level.tile_x[i] = (i % 2) * 2.5
    level.tile_y[i] = (i // 2) * 2.5
    level.tile_z[i] = 0.0
    level.tile_scale_x[i] = 1.0
    level.tile_scale_y[i] = 1.0
    level.tile_scale_z[i] = 1.0
    level.tile_rot_w[i] = 1.0  # Identity quaternion

print("Creating manager...")
mgr = SimManager(level)

print("Running steps...")
for i in range(5):
    mgr.step()
    print(f"  Step {i+1}")

print("Done!")