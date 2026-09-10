#!/usr/bin/env python3
"""Refuse to overwrite unknown code at the HGSS MapHeader accessor entries."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001
HOOK_PREFIX = bytes.fromhex("00 4B 18 47")  # ldr r3, [pc]; bx r3

# ARM9 file offset: untouched US HeartGold function-entry bytes.
ACCESSORS = {
    0x3B27C: "08B5FFF7F3FF1821",
    0x3B290: "08B5FFF7E9FF1821",
    0x3B2AC: "08B5FFF7DBFF1821",
    0x3B2C0: "08B5FFF7D1FF1821",
    0x3B2D4: "08B5FFF7C7FF1821",
    0x3B2E8: "08B5FFF7BDFF1821",
    0x3B2FC: "08B5FFF7B3FF1821",
    0x3B310: "08B5FFF7A9FF1821",
    0x3B324: "08B5FFF79FFF1821",
    0x3B344: "08B5FFF78FFF1821",
    0x3B358: "08B5FFF785FF1821",
    0x3B36C: "08B5FFF77BFF1821",
    0x3B388: "08B5FFF76DFF1821",
    0x3B3A8: "08B5FFF75DFF1821",
    0x3B3C8: "08B5FFF74DFF1821",
    0x3B3E4: "08B5FFF73FFF1821",
    0x3B400: "08B5FFF731FF1821",
    0x3B41C: "08B5FFF723FF1821",
    0x3B438: "08B5FFF715FF1821",
    0x3B454: "08B5FFF707FF1821",
    0x3B470: "08B5FFF7F9FE1821",
    0x3B48C: "08B5FFF7EBFE1821",
    0x3B4A8: "08B5FFF7DDFE1821",
    0x3B4C4: "08B5FFF7CFFE1821",
    0x3B4DC: "08B5FFF7C3FE1821",
    0x3B4F8: "08B5FFF7B5FE1821",
    0x3B518: "38B50D1C141CFFF7",
}

# The retail implementation scans a 25-entry list whose final member is Header 000.
SEMANTIC_HOOKS = {
    0x3B5DC: "064B002219888842",
}


def main():
    arm9 = ARM9.read_bytes()
    for offset, expected_hex in ACCESSORS.items():
        actual = arm9[offset:offset + 8]
        if actual == bytes.fromhex(expected_hex):
            continue

        if actual[:4] == HOOK_PREFIX:
            destination = struct.unpack_from("<I", actual, 4)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"Dynamic Header hook baseline drift at ARM9+0x{offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )

    for offset, expected_hex in SEMANTIC_HOOKS.items():
        actual = arm9[offset:offset + 8]
        if actual == bytes.fromhex(expected_hex):
            continue

        if actual[:4] == HOOK_PREFIX:
            destination = struct.unpack_from("<I", actual, 4)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"Header semantic hook baseline drift at ARM9+0x{offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )

    print(
        f"Validated {len(ACCESSORS)} Dynamic Header accessor hook sites and "
        f"{len(SEMANTIC_HOOKS)} Header semantic hook site(s)."
    )


if __name__ == "__main__":
    main()
