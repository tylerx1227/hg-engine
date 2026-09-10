#!/usr/bin/env python3
"""Report the maintained blank Map and retained bootstrap texture sources."""

from pathlib import Path
import struct

import ndspy.narc


ROOT = Path(__file__).resolve().parents[1]
FILESYS = ROOT / "base" / "root"


def load_narc(path: str) -> ndspy.narc.NARC:
    return ndspy.narc.NARC.fromFile(str(FILESYS / path))


def main() -> None:
    area_data = load_narc("a/0/4/2")
    map_textures = load_narc("a/0/4/4")
    building_textures = load_narc("a/0/7/0")

    land = (ROOT / "world" / "templates" / "hgss_blank_map.bin").read_bytes()
    permissions_size, buildings_size, model_size, terrain_size = struct.unpack("<4I", land[:16])
    bgs_signature, bgs_payload_size = struct.unpack_from("<HH", land, 16)
    if bgs_signature != 0x1234:
        raise RuntimeError(f"unexpected LandData 217 sound header 0x{bgs_signature:04X}")
    buildings_start = 20 + bgs_payload_size + permissions_size
    building_ids = [
        struct.unpack_from("<I", land, buildings_start + offset)[0]
        for offset in range(0, buildings_size, 48)
    ]
    area = area_data.files[25]
    buildings_tileset, map_tileset, dynamic_texture, area_type, light_type = struct.unpack(
        "<HHHBB", area[:8]
    )

    print(f"Blank LandData template: {len(land)} bytes")
    print(
        "LandData 217 sections: "
        f"permissions {permissions_size}, buildings {buildings_size}, "
        f"model {model_size}, terrain {terrain_size}"
    )
    print(f"Blank LandData building model IDs: {building_ids}")
    print(f"AreaData: {len(area_data.files)} members; bootstrap 25 is {len(area)} bytes")
    print(
        "AreaData 25: "
        f"building texture {buildings_tileset}, map texture {map_tileset}, "
        f"dynamic texture {dynamic_texture}, area type {area_type}, light {light_type}"
    )
    print(
        f"Map textures: {len(map_textures.files)} members; referenced member "
        f"{map_tileset} is {len(map_textures.files[map_tileset])} bytes"
    )
    print(
        f"Building textures: {len(building_textures.files)} members; referenced member "
        f"{buildings_tileset} is {len(building_textures.files[buildings_tileset])} bytes"
    )


if __name__ == "__main__":
    main()
