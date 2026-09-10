#!/usr/bin/env python3
"""Validate the stripped World Text archive and current-map loader hook."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
HOOK_OFFSET = 0x4018C
VANILLA_PREFIX = bytes.fromhex("38 B5 05 1C 28 6A 0C 1C")
HOOK_PREFIX = bytes.fromhex("00 4B 18 47")
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001
HEADERS = ROOT / "world/members/headers"
WORLD_TEXT = ROOT / "world/members/text"
EMPTY_TEXT = bytes.fromhex("01 00 F4 6A 28 9B 24 9B 25 9B 24 9B 2C E4")


def validate_hook():
    actual = ARM9.read_bytes()[HOOK_OFFSET:HOOK_OFFSET + 8]
    if actual == VANILLA_PREFIX:
        return
    if actual[:4] == HOOK_PREFIX:
        destination = struct.unpack_from("<I", actual, 4)[0]
        if OVERLAY_129_START <= destination < OVERLAY_129_END:
            return
    raise RuntimeError(
        f"World Text loader hook drift at ARM9+0x{HOOK_OFFSET:06X}: "
        f"found {actual.hex(' ').upper()}. Stop before overwriting it."
    )


def validate_members():
    members = sorted(WORLD_TEXT.iterdir(), key=lambda path: path.name)
    if [path.name for path in members] != ["0000"]:
        raise RuntimeError("Stripped world must contain exactly World Text 0000.")
    if members[0].read_bytes() != EMPTY_TEXT:
        raise RuntimeError("World Text 0000 must be the valid empty one-entry HGSS bank.")
    for header_path in HEADERS.iterdir():
        actual = struct.unpack_from("<H", header_path.read_bytes(), 10)[0]
        if actual != 0:
            raise RuntimeError(f"Header {header_path.name} references missing World Text {actual}.")


def main():
    validate_hook()
    validate_members()
    print("Validated stripped World Text 0000 and its current-map loader hook.")


if __name__ == "__main__":
    main()
