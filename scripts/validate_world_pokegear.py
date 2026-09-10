#!/usr/bin/env python3
"""Validate the US HeartGold Pokegear Overlay 101 world-sentinel sites."""

from pathlib import Path
import struct

import ndspy.codeCompression


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "base/overlay/overlay_0101.bin"
Y9 = ROOT / "base/overarm9.bin"
OVERLAY_ID = 101
OVERLAY_BASE = 0x021E7740
OVERLAY_SIZE = 0x13BC0
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001

# Runtime address -> accepted pre-install byte sequences. The roamer comparison
# also accepts the first, faulty 0xFFFF attempt so an incremental build can
# replace it without requiring a clean extraction.
DIRECT_PATCHES = {
    0x021E7B08: (bytes.fromhex("27 1C"), bytes.fromhex("E7 43")),
    0x021EA3A2: (
        bytes.fromhex("00 29 12 D1"),
        bytes.fromhex("48 1C 12 D1"),
        bytes.fromhex("08 04 12 D5"),
    ),
    0x021ED618: (bytes.fromhex("02 DC"), bytes.fromhex("02 DA")),
}

HOOK_ADDRESS = 0x021EB20E
HOOK_RETAIL = bytes.fromhex("30 48 00 21 08 B0 29 52 F8 BD")
HOOK_PREFIX = bytes.fromhex("01 4B 18 47 00 00")


def load_runtime_overlay() -> bytes:
    stored = OVERLAY.read_bytes()
    try:
        runtime = ndspy.codeCompression.decompress(stored)
    except ValueError:
        runtime = stored

    if len(runtime) != OVERLAY_SIZE:
        raise RuntimeError(
            f"Overlay 101 runtime size is {len(runtime)}, expected {OVERLAY_SIZE}."
        )
    return runtime


def main():
    y9 = Y9.read_bytes()
    entry = struct.unpack_from("<8I", y9, OVERLAY_ID * 0x20)
    if entry[0] != OVERLAY_ID or entry[1] != OVERLAY_BASE or entry[2] != OVERLAY_SIZE:
        raise RuntimeError(
            "Overlay 101 table entry does not match the audited US HeartGold layout."
        )

    overlay = load_runtime_overlay()
    for address, accepted in DIRECT_PATCHES.items():
        offset = address - OVERLAY_BASE
        size = len(accepted[0])
        actual = overlay[offset:offset + size]
        if actual not in accepted:
            raise RuntimeError(
                f"Pokegear sentinel baseline drift at 0x{address:08X}: "
                f"found {actual.hex(' ').upper()}."
            )

    offset = HOOK_ADDRESS - OVERLAY_BASE
    actual = overlay[offset:offset + len(HOOK_RETAIL)]
    if actual != HOOK_RETAIL:
        if actual[:len(HOOK_PREFIX)] != HOOK_PREFIX:
            raise RuntimeError(
                f"Pokegear no-selection hook drift at 0x{HOOK_ADDRESS:08X}: "
                f"found {actual.hex(' ').upper()}."
            )
        destination = struct.unpack_from("<I", actual, 6)[0]
        if not (OVERLAY_129_START <= destination < OVERLAY_129_END):
            raise RuntimeError(
                f"Pokegear no-selection hook targets unexpected address "
                f"0x{destination:08X}."
            )

    print("Validated 4 Pokegear Header 000 reclamation site(s) in Overlay 101.")


if __name__ == "__main__":
    main()
