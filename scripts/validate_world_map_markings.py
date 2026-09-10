#!/usr/bin/env python3
"""Refuse to overwrite unknown Map Markings routines in US HeartGold ARM9."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001

# ARM9 file offset -> untouched US HeartGold bytes.
HOOKS = {
    0x2F370: bytes.fromhex("01 88 00 29 03 D0 87 20"),
    0x2F388: bytes.fromhex("18 B4 00 21 01 80 43 88"),
    0x2F3DC: bytes.fromhex("30 B4 00 24 06 49 04 60"),
    0x2F400: bytes.fromhex("18 B4 0B 49 00 23 04 1C"),
}

HOOK_PREFIX = bytes.fromhex("00 4B 18 47")  # ldr r3, [pc]; bx r3


def main():
    arm9 = ARM9.read_bytes()
    for offset, expected in HOOKS.items():
        actual = arm9[offset:offset + 8]
        if actual == expected:
            continue

        if actual[:4] == HOOK_PREFIX:
            destination = struct.unpack_from("<I", actual, 4)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"Map Markings hook baseline drift at ARM9+0x{offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )

    print(f"Validated {len(HOOKS)} Map Markings sentinel hook site(s).")


if __name__ == "__main__":
    main()
