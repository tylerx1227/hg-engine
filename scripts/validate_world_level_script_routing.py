#!/usr/bin/env python3
"""Validate the stripped World Level Script archive and loader hook."""

from pathlib import Path
import struct

from validation_binary import read_arm9


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
HOOK_OFFSET = 0x3B8C4
VANILLA_PREFIX = bytes.fromhex("38 B5 05 1C 08 1C FF F7")
HOOK_PREFIX = bytes.fromhex("00 4B 18 47")
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001
HEADERS = ROOT / "world/members/headers"
MEMBERS = ROOT / "world/members/level_scripts"


def validate_hook():
    actual = read_arm9(ARM9)[HOOK_OFFSET:HOOK_OFFSET + 8]
    if actual == VANILLA_PREFIX:
        return
    if actual[:4] == HOOK_PREFIX:
        destination = struct.unpack_from("<I", actual, 4)[0]
        if OVERLAY_129_START <= destination < OVERLAY_129_END:
            return
    raise RuntimeError(
        f"World Level Script hook drift at ARM9+0x{HOOK_OFFSET:06X}: "
        f"found {actual.hex(' ').upper()}. Stop before overwriting it."
    )


def validate_members():
    members = sorted(MEMBERS.iterdir(), key=lambda path: path.name)
    if [path.name for path in members] != ["0000"]:
        raise RuntimeError("Stripped world must contain exactly World Level Script 0000.")
    if members[0].read_bytes() != bytes(4):
        raise RuntimeError(
            "World Level Script 0000 must be the four-byte empty template "
            "accepted by both the game and DSPRE."
        )
    for header_path in HEADERS.iterdir():
        actual = struct.unpack_from("<H", header_path.read_bytes(), 8)[0]
        if actual != 0:
            raise RuntimeError(
                f"Header {header_path.name} references missing World Level Script {actual}."
            )


def main():
    validate_hook()
    validate_members()
    print("Validated stripped World Level Script 0000 and its loader hook.")


if __name__ == "__main__":
    main()
