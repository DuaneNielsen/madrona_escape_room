# Binary Struct Layout Extraction for Python Bindings - Research Report

## Executive Summary

When creating Python bindings for C/C++ structs, the fundamental challenge is ensuring the memory layout matches exactly between the compiled C++ code and the Python ctypes representation. Current approaches (like ctypeslib) parse source code and **guess** the layout, but the actual truth lives in the compiled binary. This document explores tools and techniques for extracting the real memory layout from compiled binaries.

## The Problem

### Current Approach (Source Parsing)
- Tools like ctypeslib parse C/C++ headers using clang's AST
- Generate ctypes.Structure definitions based on source order
- **Hope** that ctypes' layout rules match the compiler's layout rules
- Often force `_pack_ = 1` to avoid padding issues

### Why This Fails
1. **Compiler-specific padding** - Different compilers add padding differently
2. **Architecture differences** - x86 vs ARM have different alignment requirements  
3. **Optimization flags** - `-O2` vs `-O3` can change layouts
4. **ABI variations** - System V vs Windows ABI
5. **Subtle type differences** - `long` is 4 bytes on Windows, 8 on Linux

### The Real Solution
The compiler already calculated the exact offsets and stored them in:
- **Debug symbols (DWARF)** - Contains complete type information
- **Symbol tables** - Has sizes and locations
- **BTF (BPF Type Format)** - Compact kernel format for types

## Available Tools

### 1. pahole - The Gold Standard
**Purpose**: Shows and manipulates data structure layout from debug info

**Key Features**:
- Reads DWARF, CTF, and BTF debug formats
- Shows exact byte offsets for every field
- Identifies padding holes and alignment
- Can generate compileable C headers

**Example Usage**:
```bash
# Show struct layout with offsets
pahole -C CompiledLevel library.so

# Output:
struct CompiledLevel {
    int32_t num_tiles;        /* 0     4 */
    int32_t max_entities;     /* 4     4 */
    float world_scale;        /* 8     4 */
    /* padding: 4 bytes */    /* 12    4 */
    float* spawn_x;           /* 16    8 */
    ...
}

# Generate complete header
pahole --compile library.so > structs.h
```

**Sources**:
- Man page: https://man.archlinux.org/man/extra/pahole/pahole.1.en
- Ubuntu docs: https://manpages.ubuntu.com/manpages/jammy/man1/pahole.1.html
- BTFHub guide: https://github.com/aquasecurity/btfhub/blob/main/docs/how-to-use-pahole.md

### 2. pyelftools - Pure Python ELF/DWARF Parser
**Purpose**: Parse ELF files and extract DWARF debug information in Python

**Key Features**:
- Pure Python, no dependencies
- Full DWARF parsing capabilities
- Can extract struct definitions and offsets
- More work required to get offsets vs pahole

**Example Usage**:
```python
from elftools.elf.elffile import ELFFile
from elftools.dwarf.descriptions import describe_form_class

with open('library.so', 'rb') as f:
    elffile = ELFFile(f)
    dwarf_info = elffile.get_dwarf_info()
    
    # Iterate through compile units and DIEs
    for CU in dwarf_info.iter_CUs():
        for DIE in CU.iter_DIEs():
            if DIE.tag == 'DW_TAG_structure_type':
                # Extract struct info and member offsets
                pass
```

**Sources**:
- GitHub: https://github.com/eliben/pyelftools
- User Guide: https://github.com/eliben/pyelftools/wiki/User's-guide
- Examples: https://python.hotexamples.com/examples/elftools.elf.elffile/ELFFile/get_dwarf_info/

### 3. BTF (BPF Type Format)
**Purpose**: Compact type format used by Linux kernel for eBPF

**Key Features**:
- Much smaller than DWARF
- Designed for runtime type information
- Includes offsets and sizes
- Requires kernel support (Linux 5.2+)

**Usage**:
```bash
# Convert DWARF to BTF
pahole -J binary.o

# Access kernel BTF
cat /sys/kernel/btf/vmlinux
```

**Sources**:
- Kernel docs: https://www.kernel.org/doc/html/latest/bpf/btf.html
- BTFHub: https://github.com/aquasecurity/btfhub

### 4. LIEF - Library to Instrument Executable Formats
**Purpose**: Parse, modify, and generate ELF/PE/MachO files

**Key Features**:
- Multi-format support
- Python bindings
- Can extract symbols and relocations
- Less focused on debug info than pyelftools

**Sources**:
- https://lief-project.github.io/

## Recommended Approach

### For Production Use
1. **Compile with debug symbols**: Add `-g` to compilation flags
2. **Use pahole to extract layout**: 
   ```bash
   pahole -C YourStruct library.so > struct_layout.txt
   ```
3. **Parse pahole output** to generate Python ctypes:
   ```python
   # Parse offset comments from pahole
   # Generate ctypes.Structure with explicit padding
   ```

### For Quick Prototyping
1. Use clang to parse headers (current approach)
2. **Validate** with pahole on the compiled library
3. Add explicit padding fields where needed

### For Embedded/Kernel Work
1. Use BTF format for compact representation
2. Tools like bpftool can dump BTF info
3. libbpf can consume BTF at runtime

## Implementation Sketch

```python
import subprocess
import re

def extract_struct_layout(library_path, struct_name):
    """Extract actual struct layout using pahole."""
    result = subprocess.run(
        ['pahole', '-C', struct_name, library_path],
        capture_output=True, text=True
    )
    
    # Parse output like:
    # int32_t field_name; /* offset size */
    offsets = {}
    for line in result.stdout.split('\n'):
        match = re.search(r'(\w+)\s+(\w+);\s*/\*\s*(\d+)\s+(\d+)', line)
        if match:
            type_name, field_name, offset, size = match.groups()
            offsets[field_name] = {
                'type': type_name,
                'offset': int(offset),
                'size': int(size)
            }
    
    return offsets

def generate_ctypes_struct(name, layout):
    """Generate ctypes.Structure with correct padding."""
    fields = []
    current_offset = 0
    
    for field_name, info in sorted(layout.items(), key=lambda x: x[1]['offset']):
        # Add padding if needed
        if info['offset'] > current_offset:
            padding_size = info['offset'] - current_offset
            fields.append((f'_pad_{current_offset}', ctypes.c_byte * padding_size))
        
        # Add field
        ctype = map_to_ctype(info['type'], info['size'])
        fields.append((field_name, ctype))
        current_offset = info['offset'] + info['size']
    
    # Create the structure class
    class GeneratedStruct(ctypes.Structure):
        _fields_ = fields
    
    return GeneratedStruct
```

## Comparison with Current Approach

| Aspect | Source Parsing (Current) | Binary Extraction (Proposed) |
|--------|-------------------------|------------------------------|
| **Accuracy** | Guesses layout | Exact offsets from compiler |
| **Dependencies** | libclang | pahole or pyelftools |
| **Complexity** | Simple | Requires debug symbols |
| **Maintenance** | Parse each time | Cached layout info |
| **Cross-platform** | Same code everywhere | Platform-specific layouts |
| **Build integration** | Not needed | Needs post-compile step |

## Conclusion

While source parsing with clang (current approach) works for simple cases, extracting the actual memory layout from compiled binaries is the only way to guarantee correctness. Tools like pahole make this straightforward, providing exact offsets that account for all compiler decisions about padding, alignment, and optimization.

For the Madrona Escape Room project, the recommendation is:
1. Keep the current clang-based approach for development
2. Add a validation step using pahole to verify layouts
3. Generate explicit padding in ctypes structures where needed
4. Consider caching the extracted layouts for production use

## Further Reading

- "The 7 dwarves: debugging information beyond gdb" (OLS 2007): https://landley.net/kdocs/ols/2007/ols2007v2-pages-35-44.pdf
- "Metal.Serial: ELFs & DWARFs" (Embedded Artistry): https://embeddedartistry.com/blog/2020/07/13/metal-serial-elfs-dwarfs/
- DWARF Debugging Standard: https://dwarfstd.org/
- pyelftools Documentation: https://github.com/eliben/pyelftools/wiki
- Linux kernel BTF documentation: https://www.kernel.org/doc/html/latest/bpf/btf.html

## Appendix: Tool Installation

```bash
# Install pahole (dwarves package)
sudo apt install dwarves  # Debian/Ubuntu
sudo pacman -S pahole     # Arch
sudo dnf install dwarves  # Fedora

# Install pyelftools
pip install pyelftools

# Install LIEF
pip install lief
```