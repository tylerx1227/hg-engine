#!/usr/bin/env python3
"""Reject member folders that narcpy could silently pack in the wrong order."""

import argparse
from pathlib import Path


def validate_member_directory(directory: Path):
    if not directory.is_dir():
        raise ValueError(f'member directory does not exist: {directory}')

    entries = sorted(directory.iterdir(), key=lambda entry: entry.name)
    if not entries:
        raise ValueError(f'member directory is empty: {directory}')

    for entry in entries:
        if entry.is_symlink() or not entry.is_file():
            raise ValueError(f'only regular member files are allowed: {entry}')

    actual_names = [entry.name for entry in entries]
    expected_names = [f'{index:04d}' for index in range(len(entries))]
    if actual_names != expected_names:
        raise ValueError(
            f'{directory} must contain one contiguous, four-digit sequence '
            f'from 0000; found {actual_names}'
        )

    print(f'Validated {directory}: {len(entries)} member(s), 0000..{expected_names[-1]}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directories', nargs='+', type=Path)
    args = parser.parse_args()
    for directory in args.directories:
        validate_member_directory(directory)


if __name__ == '__main__':
    main()
