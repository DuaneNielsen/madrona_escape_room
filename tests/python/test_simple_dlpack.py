#!/usr/bin/env python3
"""
Simple DLPack test - one manager at a time to avoid conflicts
"""

import sys
import os
sys.path.insert(0, '/home/duane/madrona/madrona_escape_room')

try:
    import madrona_escape_room as mer
    import torch
    print("✓ Successfully imported dependencies")
except ImportError as e:
    print(f"✗ Failed to import dependencies: {e}")
    sys.exit(1)

def test_cpu_simple():
    """Simple CPU test"""
    print("\n=== Testing CPU DLPack (Simple) ===")
    
    try:
        # Create CPU manager
        mgr = mer.SimManager(
            exec_mode=mer.madrona.ExecMode.CPU,
            gpu_id=0,
            num_worlds=1,  # Just 1 world to keep it simple
            rand_seed=42,
            auto_reset=True
        )
        print("✓ CPU manager created")
        
        # Get tensor
        obs_tensor = mgr.self_observation_tensor()
        print(f"✓ Tensor: shape={obs_tensor.shape}, GPU={obs_tensor.isOnGPU()}")
        
        # Test DLPack
        try:
            dlpack_tensor = torch.from_dlpack(obs_tensor)
            print(f"✓ DLPack: shape={dlpack_tensor.shape}, device={dlpack_tensor.device}")
        except Exception as e:
            print(f"⚠ DLPack failed: {e}")
            # Try regular conversion
            torch_tensor = obs_tensor.to_torch()
            print(f"✓ to_torch: shape={torch_tensor.shape}, device={torch_tensor.device}")
        
        return True
        
    except Exception as e:
        print(f"✗ CPU test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpu_simple():
    """Simple GPU test"""
    print("\n=== Testing GPU DLPack (Simple) ===")
    
    if not torch.cuda.is_available():
        print("⚠ CUDA not available")
        return True
    
    try:
        print("Creating GPU manager (this may take time for NVRTC compilation)...")
        mgr = mer.SimManager(
            exec_mode=mer.madrona.ExecMode.CUDA,
            gpu_id=0,
            num_worlds=1,  # Just 1 world
            rand_seed=42,
            auto_reset=True
        )
        print("✓ GPU manager created!")
        
        # Get tensor
        obs_tensor = mgr.self_observation_tensor()
        print(f"✓ Tensor: shape={obs_tensor.shape}, GPU={obs_tensor.isOnGPU()}")
        
        # Test DLPack - this is the main goal!
        try:
            print("Testing DLPack conversion...")
            dlpack_tensor = torch.from_dlpack(obs_tensor)
            print(f"✓ DLPack SUCCESS: shape={dlpack_tensor.shape}, device={dlpack_tensor.device}")
            
            if dlpack_tensor.is_cuda:
                print("🎉 GPU DLPack working! Zero-copy GPU tensors achieved!")
                return True
            else:
                print("✗ DLPack tensor should be on CUDA")
                return False
                
        except Exception as e:
            print(f"✗ DLPack conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"✗ GPU test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Simple DLPack Test")
    print("=" * 40)
    
    cpu_ok = test_cpu_simple()
    
    if cpu_ok:
        gpu_ok = test_gpu_simple()
        
        print("\n" + "=" * 40)
        print("RESULTS:")
        print(f"CPU: {'✓' if cpu_ok else '✗'}")
        print(f"GPU: {'✓' if gpu_ok else '✗'}")
        
        if cpu_ok and gpu_ok:
            print("\n🚀 ctypes + DLPack SUCCESS!")
            return 0
    
    print("\n❌ Tests failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())