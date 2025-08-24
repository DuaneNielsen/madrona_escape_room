#!/usr/bin/env python3
"""Minimal Madrona Escape Room Python bindings."""

import ctypes
import os

# Import the generated CompiledLevel struct
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scratch'))
from generated_compiled_level import CompiledLevel

# Load the C API library
_lib_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "build", "libmadrona_escape_room_c_api.so")
lib = ctypes.CDLL(_lib_path)

# Minimal config struct
class Config(ctypes.Structure):
    _fields_ = [
        ('exec_mode', ctypes.c_int),
        ('gpu_id', ctypes.c_int),
        ('num_worlds', ctypes.c_uint32),
        ('rand_seed', ctypes.c_uint32),
        ('auto_reset', ctypes.c_bool),
        ('enable_batch_renderer', ctypes.c_bool),
        ('batch_render_view_width', ctypes.c_uint32),
        ('batch_render_view_height', ctypes.c_uint32),
    ]

# Setup function signatures
lib.mer_create_manager.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(Config),
    ctypes.POINTER(CompiledLevel),
    ctypes.c_uint32
]
lib.mer_create_manager.restype = ctypes.c_int

lib.mer_step.argtypes = [ctypes.c_void_p]
lib.mer_step.restype = ctypes.c_int

lib.mer_destroy_manager.argtypes = [ctypes.c_void_p]

class SimManager:
    def __init__(self, compiled_level, num_worlds=1, exec_mode=0):
        """Create manager with a compiled level."""
        config = Config()
        config.exec_mode = exec_mode  # 0=CPU, 1=CUDA
        config.gpu_id = 0
        config.num_worlds = num_worlds
        config.rand_seed = 42
        config.auto_reset = True
        config.enable_batch_renderer = False
        config.batch_render_view_width = 64
        config.batch_render_view_height = 64
        
        self.handle = ctypes.c_void_p()
        result = lib.mer_create_manager(
            ctypes.byref(self.handle),
            ctypes.byref(config),
            ctypes.byref(compiled_level),
            1  # num_compiled_levels
        )
        if result != 0:
            raise RuntimeError(f"Failed to create manager: {result}")
    
    def step(self):
        """Run one simulation step."""
        result = lib.mer_step(self.handle)
        if result != 0:
            raise RuntimeError(f"Step failed: {result}")
    
    def __del__(self):
        """Clean up."""
        if hasattr(self, 'handle') and self.handle:
            lib.mer_destroy_manager(self.handle)

# Export the CompiledLevel class
__all__ = ['SimManager', 'CompiledLevel']