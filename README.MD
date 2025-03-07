# Cross-Platform Empty Directory Manager

A high-performance Python utility for identifying and managing empty directories in large filesystem structures across
Windows, macOS, and Linux platforms.

## Overview

This utility tackles the challenging task of processing massive directory structures (300k+ directories) with minimal
system resource overhead. Using advanced traversal patterns and intelligent batching techniques, it provides a unified
solution for managing empty directories across all major operating systems.

## Architectural Foundation

The utility is built on a generator-based traversal architecture that enables processing of extremely large directory
structures with constant memory usage, regardless of the total number of directories involved. This architectural
approach makes it particularly suitable for scenarios involving hundreds of thousands of directories.

Key technical components include:

- **Depth-First Traversal**: Bottom-up processing ensures accurate identification of empty directories
- **Incremental Processing**: Stream-based approach prevents memory exhaustion
- **Platform Abstraction Layer**: Unified interface with platform-specific implementations
- **Intelligent Batch Processing**: Configurable batch sizes optimize resource utilization

## Platform Compatibility

The utility provides full compatibility across major operating systems:

| Platform | Empty Directory Detection | Trash/Recycling Integration | Path Handling                    |
|----------|---------------------------|-----------------------------|----------------------------------|
| Windows  | ✓                         | Recycle Bin                 | Handles both forward/backslashes |
| macOS    | ✓                         | Trash                       | Native path formatting           |
| Linux    | ✓                         | Desktop Environment Trash   | Native path formatting           |

## Installation

```bash
# Clone the repository
git clone https://github.com/poacosta/empty-directory-manager.git
cd empty-directory-manager

# Install requirements
pip install send2trash pathlib
```

## Usage

### Command Line Interface

```bash
# List all empty directories
python empty_dir_manager.py /path/to/search --action list

# Count empty directories
python empty_dir_manager.py /path/to/search --action count

# Move empty directories to system trash
python empty_dir_manager.py /path/to/search --action trash
```

### Advanced Options

```bash
# Customize batch processing size (for very large operations)
python empty_dir_manager.py /path/to/search --action trash --batch-size 500

# Suppress progress messages
python empty_dir_manager.py /path/to/search --action trash --quiet
```

## Performance Optimizations

The utility employs several performance optimization techniques:

1. **Lazy Evaluation**: Directory traversal occurs on-demand, conserving resources
2. **Path Validation Caching**: Minimizes redundant filesystem operations
3. **Batched Operations**: Reduces system call overhead
4. **Progress Metering**: Real-time performance monitoring with adaptive batch sizing

## Requirements

- Python 3.6+
- send2trash library (`pip install send2trash`)
- pathlib (included in Python 3.4+)
