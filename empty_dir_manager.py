#!/usr/bin/env python3
"""
Empty Directory Manager - Cross-Platform Utility

A memory-efficient Python utility for identifying and managing empty directories
in large filesystem structures across Windows, macOS, and Linux platforms.
"""

import argparse
import os
import platform
import sys
import time
from pathlib import Path
from typing import Generator, List

import send2trash


class EmptyDirectoryManager:
    """
    A cross-platform utility for processing empty directories with minimal memory footprint.

    Employs generator-based traversal patterns to efficiently handle massive directory
    structures (300k+ directories) while providing platform-specific integrations for
    directory recycling operations.
    """

    def __init__(self, root_path: str, batch_size: int = 1000, verbose: bool = True):
        """
        Initialize the Empty Directory Manager.

        Args:
            root_path: Root directory to start search
            batch_size: Number of directories to process in each batch
            verbose: Whether to print detailed progress information
        """
        self.root_path = Path(root_path).resolve()
        self.batch_size = batch_size
        self.verbose = verbose
        self.platform = platform.system()

        if not self.root_path.exists():
            raise FileNotFoundError(f"Root path does not exist: {self.root_path}")

        self.trash_name = self._get_trash_name()

    def _get_trash_name(self) -> str:
        """Get the platform-specific name for the trash/recycle location."""
        if self.platform == "Windows":
            return "Recycle Bin"
        elif self.platform == "Darwin":  # macOS
            return "Trash"
        else:  # Linux and others
            return "Trash"

    def find_empty_dirs(self) -> Generator[Path, None, None]:
        """
        Yield empty directories using generator pattern for memory efficiency.

        Uses depth-first traversal (topdown=False) to ensure subdirectories are
        processed before their parents, preventing premature identification.

        Yields:
            Path objects representing empty directories
        """
        try:
            root_str = str(self.root_path)

            for dirpath, dirnames, filenames in os.walk(root_str, topdown=False):
                if filenames:
                    continue

                if dirnames:
                    full_subdirs = [Path(os.path.join(dirpath, d)) for d in dirnames]
                    if any(subdir.exists() for subdir in full_subdirs):
                        continue

                yield Path(dirpath)

        except PermissionError as e:
            if self.verbose:
                print(f"Permission error accessing {e.filename}: {e.strerror}")
        except Exception as e:
            if self.verbose:
                print(f"Error during directory traversal: {e}")

    def list_empty_dirs(self) -> int:
        """
        List all empty directories found in the root path.

        Returns:
            Count of empty directories found
        """
        count = 0
        for empty_dir in self.find_empty_dirs():
            print(empty_dir)
            count += 1
        return count

    def count_empty_dirs(self) -> int:
        """
        Count empty directories without printing each one.

        Returns:
            Count of empty directories found
        """
        return sum(1 for _ in self.find_empty_dirs())

    def trash_empty_dirs(self) -> int:
        """
        Move empty directories to system trash/recycle bin.

        Processes directories in batches to minimize memory usage.

        Returns:
            Count of directories successfully moved to trash
        """
        count = 0
        batch = []
        success_count = 0

        start_time = time.time()
        last_update = start_time

        for empty_dir in self.find_empty_dirs():
            count += 1
            batch.append(empty_dir)

        if len(batch) >= self.batch_size:
            success_count += self._process_batch(batch)
            batch = []

            current_time = time.time()
            if self.verbose and current_time - last_update >= 5:  # Update every 5 seconds
                elapsed = current_time - start_time
                print(f"Processed {count} directories in {elapsed:.2f} seconds ({count / elapsed:.2f} dirs/sec)")
                last_update = current_time

        if batch:
            success_count += self._process_batch(batch)

        if self.verbose:
            print(f"Operation complete: {success_count}/{count} directories successfully moved to {self.trash_name}")

        return success_count

    def _process_batch(self, batch: List[Path]) -> int:
        """
        Process a batch of directories by moving them to trash.

        Args:
            batch: List of Path objects to process

        Returns:
            Count of successfully processed directories
        """
        success_count = 0

        for dir_path in batch:
            try:
                if not dir_path.exists():
                    continue

                send2trash.send2trash(str(dir_path))

                if self.verbose:
                    print(f"Moved to {self.trash_name}: {dir_path}")

                success_count += 1

            except PermissionError:
                if self.verbose:
                    print(f"Permission denied: {dir_path}")
            except FileNotFoundError:
                pass
            except Exception as e:
                if self.verbose:
                    print(f"Error processing {dir_path}: {e}")

        return success_count


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Find and process empty directories across platforms",
        epilog="Works on Windows, macOS, and Linux with appropriate trash integration"
    )

    parser.add_argument("path",
                        help="Root path to search for empty directories")

    parser.add_argument("--action",
                        choices=["list", "count", "trash"],
                        default="list",
                        help="Action to perform on empty directories")

    parser.add_argument("--batch-size",
                        type=int,
                        default=1000,
                        help="Number of directories to process in each batch")

    parser.add_argument("--quiet",
                        action="store_true",
                        help="Suppress progress messages")

    args = parser.parse_args()

    try:
        manager = EmptyDirectoryManager(
            args.path,
            batch_size=args.batch_size,
            verbose=not args.quiet
        )

        if not args.quiet:
            print(f"Platform detected: {platform.system()}")
            print(f"Searching for empty directories in {args.path}...")

        if args.action == "list":
            count = manager.list_empty_dirs()
            print(f"Found {count} empty directories")

        elif args.action == "count":
            count = manager.count_empty_dirs()
            print(f"Found {count} empty directories")

        elif args.action == "trash":
            count = manager.trash_empty_dirs()
            print(f"Processed {count} empty directories")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
