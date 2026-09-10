#!/usr/bin/env python3
"""Refuse to overwrite unknown world-identity code in US HeartGold ARM9."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
OVERLAY_1 = ROOT / "base/overlay/overlay_0001.bin"
OVERLAY_1_BASE = 0x021E5900
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001

# ARM9 file offset -> untouched US HeartGold bytes.
HOOKS = {
    0x3B94C: bytes.fromhex("00 F0 90 F8 68 34 20 80"),
    0x5C568: bytes.fromhex("04 1C 00 92 01 20 01 90"),
    0x6A13C: bytes.fromhex("00 90 30 20 01 90 01 20"),
    0x6AF14: bytes.fromhex("01 21 02 91 19 1C 06 9A"),
}

HOOK_PREFIXES = {
    0x3B94C: bytes.fromhex("00 4B 18 47"),  # ldr r3, [pc]; bx r3
    0x5C568: bytes.fromhex("00 4D 28 47"),  # ldr r5, [pc]; bx r5
    0x6A13C: bytes.fromhex("00 4B 18 47"),  # ldr r3, [pc]; bx r3
    0x6AF14: bytes.fromhex("00 4A 10 47"),  # ldr r2, [pc]; bx r2
}

# Overlay runtime address -> untouched US HeartGold bytes and installed prefix.
OVERLAY_1_HOOKS = {
    0x02204AB0: (
        bytes.fromhex("00 91 00 24 01 94 01 21"),
        (
            bytes.fromhex("00 4B 18 47"),  # corrected: ldr r3, [pc]; bx r3
            bytes.fromhex("00 49 08 47"),  # replace the earlier unsafe r1 hook
        ),
    ),
}


def main():
    arm9 = ARM9.read_bytes()
    for offset, expected in HOOKS.items():
        actual = arm9[offset:offset + 8]
        if actual == expected:
            continue

        if actual[:4] == HOOK_PREFIXES[offset]:
            destination = struct.unpack_from("<I", actual, 4)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"World identity hook baseline drift at ARM9+0x{offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )


    overlay_1 = OVERLAY_1.read_bytes()
    for address, (expected, accepted_hook_prefixes) in OVERLAY_1_HOOKS.items():
        offset = address - OVERLAY_1_BASE
        actual = overlay_1[offset:offset + 8]
        if actual == expected:
            continue

        if actual[:4] in accepted_hook_prefixes:
            destination = struct.unpack_from("<I", actual, 4)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"World identity hook baseline drift at Overlay 1 address 0x{address:08X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )

    total = len(HOOKS) + len(OVERLAY_1_HOOKS)
    print(f"Validated {total} World identity hook site(s).")


if __name__ == "__main__":
    main()
