#!/usr/bin/env python3
"""Create and validate a zero-building HGSS LandData template."""

from argparse import ArgumentParser
from pathlib import Path
import struct


HEADER_SIZE = 20
PERMISSIONS_SIZE = 32 * 32 * 2
BUILDING_SIZE = 48
HGSS_SOUND_SIGNATURE = 0x1234


def parse_sections(data: bytes) -> tuple[int, int, int, int, int]:
    if len(data) < HEADER_SIZE:
        raise RuntimeError("LandData is too short to contain an HGSS header")

    permissions_size, buildings_size, model_size, terrain_size = struct.unpack_from(
        "<4I", data
    )
    sound_signature, sound_size = struct.unpack_from("<HH", data, 16)
    expected_size = (
        HEADER_SIZE
        + sound_size
        + permissions_size
        + buildings_size
        + model_size
        + terrain_size
    )
    if sound_signature != HGSS_SOUND_SIGNATURE:
        raise RuntimeError(
            f"invalid HGSS sound signature 0x{sound_signature:04X}; expected 0x1234"
        )
    if permissions_size != PERMISSIONS_SIZE:
        raise RuntimeError(
            f"permissions section is {permissions_size} bytes; expected {PERMISSIONS_SIZE}"
        )
    if buildings_size % BUILDING_SIZE:
        raise RuntimeError("building section is not a multiple of 48 bytes")
    if model_size == 0 or terrain_size == 0:
        raise RuntimeError("map model and terrain sections must both be non-empty")
    if expected_size != len(data):
        raise RuntimeError(
            f"section sizes describe {expected_size} bytes, but the file is {len(data)} bytes"
        )
    return permissions_size, buildings_size, model_size, terrain_size, sound_size


def remove_buildings(data: bytes) -> bytes:
    permissions_size, buildings_size, _, _, sound_size = parse_sections(data)
    buildings_start = HEADER_SIZE + sound_size + permissions_size
    buildings_end = buildings_start + buildings_size

    result = bytearray(data[:buildings_start] + data[buildings_end:])
    struct.pack_into("<I", result, 4, 0)
    _, result_buildings_size, _, _, _ = parse_sections(result)
    if result_buildings_size != 0:
        raise RuntimeError("generated template still contains a building section")
    return bytes(result)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    cleaned = remove_buildings(args.source.read_bytes())
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_bytes(cleaned)
    print(
        f"Wrote {args.destination} ({len(cleaned)} bytes, zero buildings, "
        "valid HGSS LandData structure)."
    )


if __name__ == "__main__":
    main()
