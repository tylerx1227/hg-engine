#!/usr/bin/env python3
"""Read HGSS executable binaries in their runtime (decompressed) form."""

from pathlib import Path

import ndspy.codeCompression


ARM9_DECOMPRESSED_MIN_SIZE = 0xBC000


def read_arm9(path: Path) -> bytes:
    stored = path.read_bytes()
    if len(stored) >= ARM9_DECOMPRESSED_MIN_SIZE:
        return stored
    try:
        return ndspy.codeCompression.decompress(stored)
    except ValueError as exc:
        raise RuntimeError(
            "ARM9 is smaller than the decompressed HGSS baseline, but its "
            "compression could not be decoded. Stop and investigate before "
            "overwriting it."
        ) from exc


def read_overlay(path: Path) -> bytes:
    stored = path.read_bytes()
    try:
        return ndspy.codeCompression.decompress(stored)
    except ValueError:
        return stored
