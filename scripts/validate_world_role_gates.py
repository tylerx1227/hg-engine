#!/usr/bin/env python3
"""Refuse to overwrite unknown Header-002/Union-role code in US HeartGold."""

from pathlib import Path
import struct

from validation_binary import read_arm9, read_overlay


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
OVERLAY_1 = ROOT / "base/overlay/overlay_0001.bin"
OVERLAY_1_BASE = 0x021E5900
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001

# ARM9 file offset -> (untouched bytes, installed absolute-hook prefix).
ARM9_HOOKS = {
    0x3B5CC: (bytes.fromhex("02 28 01 D1 01 20 70 47"), bytes.fromhex("00 4B 18 47")),
    0x3B5FC: (bytes.fromhex("4B 21 89 00 88 42 01 D1"), bytes.fromhex("00 4B 18 47")),
    0x5337C: (bytes.fromhex("10 B5 04 1C 20 6A 00 68"), bytes.fromhex("00 4B 18 47")),
    0x44480: (bytes.fromhex("08 B5 80 30 00 68 00 69"), bytes.fromhex("00 4B 18 47")),
    0x7C480: (bytes.fromhex("02 28 18 D1 1F 22 92 01"), bytes.fromhex("00 4B 18 47")),
}

# Overlay runtime address -> (untouched bytes, installed absolute-hook prefix).
OVERLAY_1_HOOKS = {
    0x021F4450: (bytes.fromhex("02 29 05 D0 04 29 03 D0"), bytes.fromhex("00 4A 10 47")),
}


def validate_site(label: str, actual: bytes, expected: bytes, hook_prefix: bytes):
    if actual == expected:
        return

    if actual[:4] == hook_prefix:
        destination = struct.unpack_from("<I", actual, 4)[0]
        if OVERLAY_129_START <= destination < OVERLAY_129_END:
            return

    raise RuntimeError(
        f"World role gate baseline drift at {label}: found {actual.hex(' ').upper()}. "
        "Stop and investigate before overwriting it."
    )


def main():
    arm9 = read_arm9(ARM9)
    for offset, (expected, hook_prefix) in ARM9_HOOKS.items():
        validate_site(
            f"ARM9+0x{offset:06X}",
            arm9[offset:offset + 8],
            expected,
            hook_prefix,
        )

    overlay_1 = read_overlay(OVERLAY_1)
    for address, (expected, hook_prefix) in OVERLAY_1_HOOKS.items():
        offset = address - OVERLAY_1_BASE
        validate_site(
            f"Overlay 1 address 0x{address:08X}",
            overlay_1[offset:offset + 8],
            expected,
            hook_prefix,
        )

    total = len(ARM9_HOOKS) + len(OVERLAY_1_HOOKS)
    print(f"Validated {total} stripped-world role gate site(s).")


if __name__ == "__main__":
    main()
