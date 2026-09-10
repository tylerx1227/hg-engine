#!/usr/bin/env python3
"""Seed the one-member bootstrap world asset archives from the proven room."""

from pathlib import Path
import struct

import ndspy.narc


ROOT = Path(__file__).resolve().parents[1]
FILESYS = ROOT / "base" / "root"
WORLD_MEMBERS = ROOT / "world" / "members"


def narc_member(path: str, member: int) -> bytes:
    narc = ndspy.narc.NARC.fromFile(str(FILESYS / path))
    return narc.files[member]


def write_member(collection: str, data: bytes) -> None:
    directory = WORLD_MEMBERS / collection
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "0000"
    if target.exists():
        if target.read_bytes() == data:
            return
        raise RuntimeError(f"refusing to overwrite different canonical member: {target}")
    target.write_bytes(data)


def main() -> None:
    # Map 0000 is a maintained, zero-building authoring template. It must not be
    # regenerated from a retail room because DSPRE also uses this exact asset for
    # new Tyler-world Map files.
    blank_map = ROOT / "world" / "templates" / "hgss_blank_map.bin"
    write_member("maps", blank_map.read_bytes())

    area_data = bytearray(narc_member("a/0/4/2", 25))
    if len(area_data) != 8:
        raise RuntimeError(f"Area Data 25 is {len(area_data)} bytes, expected 8")
    building_texture, map_texture = struct.unpack_from("<HH", area_data)
    write_member("map_textures", narc_member("a/0/4/4", map_texture))
    write_member("building_textures", narc_member("a/0/7/0", building_texture))
    write_member("building_configs", narc_member("a/0/4/3", building_texture))

    # Both retained texture banks are now member 0000.
    struct.pack_into("<HH", area_data, 0, 0, 0)
    write_member("area_data", area_data)

    header_path = WORLD_MEMBERS / "headers" / "0000"
    header = bytearray(header_path.read_bytes())
    if len(header) != 24:
        raise RuntimeError(f"Header 0000 is {len(header)} bytes, expected 24")
    if header[1] not in (0, 25):
        raise RuntimeError(f"Header 0000 has unexpected Area Data {header[1]}")
    # Canonical Tyler authoring defaults. Header 0000 owns bundle member 0000.
    header[0] = 0xFF  # no wild encounters
    header[1] = 0
    struct.pack_into("<H", header, 2, 0x000F)  # neutral world X/Y; retain unknown nibble
    struct.pack_into("<4H", header, 4, 0, 0, 0, 0)  # matrix/script/level/text
    struct.pack_into("<2H", header, 12, 1018, 1018)  # New Bark Town day/night music
    struct.pack_into("<H", header, 16, 0)  # event
    header[18] = 0  # Mystery Zone location name
    header[19] = 3  # Town icon; Mom call message 0
    last32 = (1 << 8) | (2 << 18) | (6 << 20) | (0b1111011 << 25)
    struct.pack_into("<I", header, 20, last32)
    header_path.write_bytes(header)

    matrix_path = WORLD_MEMBERS / "matrices" / "0000"
    matrix = bytearray(matrix_path.read_bytes())
    width, height, has_headers, has_heights, name_length = matrix[:5]
    cell_count = width * height
    map_grid_start = 5 + name_length + cell_count * 2 * has_headers + cell_count * has_heights
    first_map = struct.unpack_from("<H", matrix, map_grid_start)[0]
    if first_map not in (0, 217):
        raise RuntimeError(f"Matrix 0000 has unexpected first LandData {first_map}")
    struct.pack_into("<H", matrix, map_grid_start, 0)
    matrix_path.write_bytes(matrix)

    print(
        "Seeded zero-building Map 0000 from the maintained blank template and "
        "Area Data, map texture, building texture, and building configuration "
        f"member 0000 from retail members 25, {map_texture}, and {building_texture}."
    )


if __name__ == "__main__":
    main()
