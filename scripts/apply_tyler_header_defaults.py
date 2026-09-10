#!/usr/bin/env python3
"""Apply the canonical Tyler authoring defaults to bootstrap Header 0000."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "world" / "members" / "headers" / "0000"


def main() -> None:
    data = bytearray(HEADER.read_bytes())
    if len(data) != 24:
        raise RuntimeError(f"Header 0000 is {len(data)} bytes; expected 24")

    data[0] = 0xFF
    data[1] = 0
    struct.pack_into("<H", data, 2, 0x000F)
    struct.pack_into("<4H", data, 4, 0, 0, 0, 0)
    struct.pack_into("<2H", data, 12, 1018, 1018)
    struct.pack_into("<H", data, 16, 0)
    data[18] = 0
    data[19] = 3
    last32 = (1 << 8) | (2 << 18) | (6 << 20) | (0b1111011 << 25)
    struct.pack_into("<I", data, 20, last32)
    HEADER.write_bytes(data)
    print("Applied canonical Tyler defaults to bootstrap Header 0000.")


if __name__ == "__main__":
    main()
