#!/usr/bin/env python3
"""Validate the single-header bootstrap world before NARC packing."""

import argparse
from pathlib import Path
import struct


HEADER_SIZE = 24
MAPNAME_SIZE = 16
EXPECTED_MATRIX = 0
EXPECTED_AREA_DATA = 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()

    members = sorted(args.directory.iterdir(), key=lambda member: member.name)
    if [member.name for member in members] != ["0000"]:
        raise RuntimeError("Bootstrap world must contain exactly Dynamic Header 0000.")

    data = members[0].read_bytes()
    if len(data) != HEADER_SIZE:
        raise RuntimeError(f"Dynamic Header 0000 is {len(data)} bytes, expected {HEADER_SIZE}.")

    area_data = data[1]
    move_and_world_coords = struct.unpack_from("<H", data, 2)[0]
    matrix_id, script_id, level_script_id, text_id = struct.unpack_from("<4H", data, 4)
    day_music, night_music = struct.unpack_from("<2H", data, 12)
    event_id = struct.unpack_from("<H", data, 16)[0]
    if (script_id, level_script_id, text_id, event_id) != (0, 0, 0, 0):
        raise RuntimeError(
            "Bootstrap Header 0000 must reference World Script, Level Script, "
            "World Text, and Event member 0000."
        )
    if matrix_id != EXPECTED_MATRIX or area_data != EXPECTED_AREA_DATA:
        raise RuntimeError(
            f"Bootstrap Header 0000 must use author-owned Matrix {EXPECTED_MATRIX} and "
            f"Area Data {EXPECTED_AREA_DATA}; found Matrix {matrix_id}, Area Data {area_data}."
        )
    if data[0] != 0xFF:
        raise RuntimeError("Bootstrap Header 0000 must have wild encounters disabled.")
    if move_and_world_coords != 0x000F:
        raise RuntimeError("Bootstrap Header 0000 must use neutral world-map coordinates (0,0).")
    if (day_music, night_music) != (1018, 1018):
        raise RuntimeError("Bootstrap Header 0000 must use New Bark Town music 1018.")
    if data[18:20] != bytes((0, 3)):
        raise RuntimeError(
            "Bootstrap Header 0000 must use protected Location Name 000, Town icon, and Mom call message 0."
        )
    last32 = struct.unpack_from("<I", data, 20)[0]
    expected_last32 = (1 << 8) | (2 << 18) | (6 << 20) | (0b1111011 << 25)
    if last32 != expected_last32:
        raise RuntimeError(
            "Bootstrap Header 0000 must be City/Town, camera 0, following All, battle BG 6, "
            "Johto, and allow Bicycle/Run/Fly/Pokegear calls/Radio with Escape Rope disabled."
        )

    events = args.directory.parent / "events"
    event_members = sorted(events.iterdir(), key=lambda member: member.name)
    if [member.name for member in event_members] != ["0000"]:
        raise RuntimeError("Bootstrap world must contain exactly Event File 0000.")
    if event_members[0].read_bytes() != bytes(16):
        raise RuntimeError("Event File 0000 must contain four zero event counts.")

    matrices = args.directory.parent / "matrices"
    matrix_members = sorted(matrices.iterdir(), key=lambda member: member.name)
    if [member.name for member in matrix_members] != ["0000"]:
        raise RuntimeError("Bootstrap world must contain exactly Matrix 0000.")
    matrix = matrix_members[0].read_bytes()
    width, height, has_headers, has_heights, name_length = matrix[:5]
    if (width, height, has_headers, has_heights, name_length) != (47, 17, 1, 1, 4):
        raise RuntimeError("Matrix 0000 must be main, 47x17, with Header and altitude grids.")
    if matrix[5:9] != b"main":
        raise RuntimeError("Matrix 0000 must be named main.")
    cell_count = width * height
    expected_size = 9 + cell_count * 2 + cell_count + cell_count * 2
    if len(matrix) != expected_size:
        raise RuntimeError(f"Matrix 0000 is {len(matrix)} bytes; expected {expected_size}.")
    header_grid = matrix[9:9 + cell_count * 2]
    altitude_grid = matrix[9 + cell_count * 2:9 + cell_count * 3]
    map_grid = matrix[9 + cell_count * 3:]
    if header_grid != bytes(cell_count * 2) or altitude_grid != bytes(cell_count):
        raise RuntimeError("Matrix 0000 Header and altitude grids must be zero-filled.")
    maps = struct.unpack(f"<{cell_count}H", map_grid)
    if maps[0] != 0 or any(value != 0xFFFF for value in maps[1:]):
        raise RuntimeError(
            "Matrix 0000 must contain author-owned LandData 000 only in starting cell (0,0)."
        )

    mapname = args.directory.parents[1] / "mapname.bin"
    names = mapname.read_bytes()
    if len(names) != MAPNAME_SIZE:
        raise RuntimeError(
            f"mapname.bin must contain exactly one {MAPNAME_SIZE}-byte name; found {len(names)} bytes."
        )
    if names.rstrip(b"\0") != b"BOOTSTRAP":
        raise RuntimeError("Header 0000 internal name must be BOOTSTRAP.")

    print("Validated one boot-safe Dynamic Header 0000 and one internal name.")


if __name__ == "__main__":
    main()
