#!/usr/bin/env python3
"""
FastMCP-based Madrona Viewer Server

Provides controlled access to the Madrona Escape Room viewer for screenshots
using the existing capture_level_screenshot.py functionality.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    name="madrona-viewer",
    instructions="""Use this server to capture screenshots from the Madrona Escape Room viewer. \
This server provides controlled access to a 3D viewer with a free-flying camera that can be \
positioned anywhere in the simulation world. Use when you need to:
- Capture screenshots of generated levels for documentation
- Take visual snapshots during development and testing
- Generate images from different camera angles and positions
- Create visual debugging aids for level design

The viewer uses a free camera system that can be positioned and oriented anywhere in 3D space, \
providing much more flexibility than agent-based cameras.

## Available Tools

### capture_screenshot(output_path, [options])
The main tool for taking screenshots. Launches viewer, captures frame 0, and saves the image.

**Required:**
- `output_path`: Where to save screenshot (e.g., "level_test.png")

**Optional:**
- `num_worlds`: Number of worlds (default: 1)
- `exec_mode`: "CPU" or "GPU" (default: "CPU")
- `gpu_id`: GPU device ID for CUDA mode (default: 0)
- `seed`: Random seed for level generation (default: 42)

**Examples:**
- `capture_screenshot("test.png")` - Basic CPU screenshot
- `capture_screenshot("gpu_test.png", exec_mode="GPU", gpu_id=0)` - GPU screenshot
- `capture_screenshot("multi.png", num_worlds=4, seed=123)` - Multiple worlds

### start_viewer([options])
Starts the interactive viewer for manual exploration (optional).

### close_viewer()
Kills any running viewer processes.

## Quick Usage
For most cases, just use: `capture_screenshot("filename.png")`""",
)


def capture_screenshot_internal(
    num_worlds=1, exec_mode="cpu", gpu_id=0, output_path="level_screenshot.png"
):
    """
    Launch viewer with automatic screenshot capture of frame 0.

    This is based on the existing capture_level_screenshot.py script.
    """
    # Build viewer command
    viewer_path = Path(__file__).parent.parent / "build" / "viewer"
    if not viewer_path.exists():
        return (
            None,
            f"Error: Viewer not found at {viewer_path}. "
            "Please build the project first: make -C build -j8",
        )

    # Set environment variable for automatic screenshot
    env = os.environ.copy()
    env["SCREENSHOT_PATH"] = output_path

    # Build command arguments
    cmd = [str(viewer_path), "-n", str(num_worlds), "--hide-menu"]
    if exec_mode.lower() == "cuda":
        cmd.extend(["--cuda", str(gpu_id)])

    try:
        # Launch viewer with timeout (it will capture frame 0 and we'll kill it)
        # The viewer will automatically take a screenshot on frame 0 when SCREENSHOT_PATH is set
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Give it a moment to initialize and capture
        time.sleep(2)

        # Terminate the viewer
        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

        # Check if screenshot was created
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            return (
                output_path,
                f"Screenshot captured successfully: {output_path} ({file_size} bytes)",
            )
        else:
            return None, f"Screenshot was not created at {output_path}"

    except Exception as e:
        return None, f"Error launching viewer: {e}"


@mcp.tool()
async def start_viewer(
    num_worlds: int = 1,
    seed: int = 42,
    exec_mode: str = "CPU",
    gpu_id: int = 0,
    hide_menu: bool = True,
    window_width: int = 1920,
    window_height: int = 1080,
) -> str:
    """Start the Madrona viewer with specified configuration.

    Args:
        num_worlds: Number of simulation worlds (default: 1)
        seed: Random seed for level generation (default: 42)
        exec_mode: "CPU" or "GPU" (default: "CPU")
        gpu_id: GPU device ID for CUDA mode (default: 0)
        hide_menu: Hide ImGui menu for clean screenshots (default: True)
        window_width: Window width in pixels (default: 1920)
        window_height: Window height in pixels (default: 1080)
    """
    # Build viewer command
    viewer_path = Path(__file__).parent.parent / "build" / "viewer"
    if not viewer_path.exists():
        return (
            f"Error: Viewer not found at {viewer_path}. "
            "Please build the project first: make -C build -j8"
        )

    # Build command arguments
    cmd = [str(viewer_path), "-n", str(num_worlds), "--seed", str(seed)]
    if hide_menu:
        cmd.append("--hide-menu")
    if exec_mode.upper() == "GPU":
        cmd.extend(["--cuda", str(gpu_id)])

    try:
        # Start viewer in background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return (
            f"Viewer started with PID {process.pid}. Use capture_screenshot() "
            "to take screenshots, or kill the process when done."
        )
    except Exception as e:
        return f"Error starting viewer: {e}"


@mcp.tool()
async def capture_screenshot(
    output_path: str, num_worlds: int = 1, exec_mode: str = "CPU", gpu_id: int = 0, seed: int = 42
) -> str:
    """Capture a screenshot from the Madrona viewer.

    Args:
        output_path: Path where to save the screenshot (e.g., "screenshot.png")
        num_worlds: Number of simulation worlds (default: 1)
        exec_mode: "CPU" or "GPU" (default: "CPU")
        gpu_id: GPU device ID for CUDA mode (default: 0)
        seed: Random seed for level generation (default: 42)
    """
    # Ensure output path has proper extension
    output_path = str(output_path)
    if not (output_path.endswith(".png") or output_path.endswith(".bmp")):
        output_path += ".png"

    result_path, message = capture_screenshot_internal(
        num_worlds=num_worlds, exec_mode=exec_mode, gpu_id=gpu_id, output_path=output_path
    )

    return message


@mcp.tool()
async def close_viewer() -> str:
    """Close any running viewer processes."""
    try:
        # Kill any running viewer processes
        result = subprocess.run(["pkill", "-f", "build/viewer"], capture_output=True, text=True)
        if result.returncode == 0:
            return "Viewer processes terminated successfully."
        else:
            return "No viewer processes found running."
    except Exception as e:
        return f"Error closing viewer: {e}"


if __name__ == "__main__":
    # Run the server
    mcp.run(transport="stdio")
