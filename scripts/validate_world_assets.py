#!/usr/bin/env python3
"""Validate the single-member map/area/texture bootstrap collections."""

from pathlib import Path
import struct


COLLECTIONS = (
    "maps",
    "area_data",
    "map_textures",
    "building_textures",
    "building_configs",
)


def only_member(root: Path, collection: str) -> bytes:
    directory = root / collection
    members = sorted(directory.iterdir(), key=lambda member: member.name)
    if [member.name for member in members] != ["0000"] or not members[0].is_file():
        raise RuntimeError(f"World {collection} must contain exactly member 0000")
    data = members[0].read_bytes()
    if not data:
        raise RuntimeError(f"World {collection} member 0000 is empty")
    return data


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "world" / "members"
    land, area, map_texture, building_texture, building_config = (
        only_member(root, collection) for collection in COLLECTIONS
    )

    if len(area) != 8:
        raise RuntimeError(f"Area Data 000 is {len(area)} bytes, expected 8")
    building_tileset, map_tileset = struct.unpack_from("<HH", area)
    if (building_tileset, map_tileset) != (0, 0):
        raise RuntimeError(
            "Area Data 000 must reference building texture 000 and map texture 000"
        )

    if len(land) < 20:
        raise RuntimeError("Map 000 is too short to contain an HGSS LandData header")
    permissions_size, buildings_size, model_size, terrain_size = struct.unpack_from("<4I", land)
    signature, sound_size = struct.unpack_from("<HH", land, 16)
    expected_size = 20 + sound_size + permissions_size + buildings_size + model_size + terrain_size
    if signature != 0x1234 or permissions_size != 2048 or expected_size != len(land):
        raise RuntimeError("Map 000 has an invalid HGSS LandData section layout")
    if buildings_size % 48:
        raise RuntimeError("Map 000 building section is not a multiple of 48 bytes")
    if buildings_size != 0:
        raise RuntimeError(
            f"Map 000 must be the zero-building blank template, found {buildings_size // 48} building(s)"
        )
    permissions_start = 20 + sound_size
    if any(land[permissions_start : permissions_start + permissions_size]):
        raise RuntimeError("Map 000 blank-template permissions must all be type 0/collision 0")
    template = root.parent / "templates" / "hgss_blank_map.bin"
    if not template.is_file() or template.read_bytes() != land:
        raise RuntimeError("Map 000 must exactly match world/templates/hgss_blank_map.bin")
    if not map_texture or not building_texture or not building_config:
        raise RuntimeError("Bootstrap texture/config member 0000 must be valid and non-empty")

    print(
        "Validated zero-building blank Map 000, Area Data 000, map texture 000, and "
        "building texture 000, and building configuration 000."
    )


if __name__ == "__main__":
    main()
