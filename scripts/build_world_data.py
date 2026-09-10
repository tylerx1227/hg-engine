#!/usr/bin/env python3
"""Compile DSPRE-editable world data JSON into fixed-size NARC members."""

import json
from pathlib import Path
import shutil
import struct
import sys


VERSION = 1
CONFIG_MAGIC = b"TWRL"
SPAWN_MAGIC = b"TWSP"
RECORD_SIZE = 80
LOCATION = struct.Struct("<5i")
CONFIG_PREFIX = struct.Struct("<4sHHIHH")
SPAWN_PREFIX = struct.Struct("<4sHHBBBBHH")


def fail(message):
    raise ValueError(message)


def location(value, label):
    if not isinstance(value, list) or len(value) != 5:
        fail(f"{label} must be [header, warp, x, y, direction]")
    values = [int(item) for item in value]
    return LOCATION.pack(*values)


def u16(value, label):
    value = int(value)
    if value < 0 or value > 0xFFFF:
        fail(f"{label} must be from 0 through 65535")
    return value


def u8(value, label):
    value = int(value)
    if value < 0 or value > 0xFF:
        fail(f"{label} must be from 0 through 255")
    return value


def build_config(config, spawn_count):
    initial_spawn = u16(config["initialSpawnId"], "initialSpawnId")
    if initial_spawn == 0 or initial_spawn > spawn_count:
        fail("initialSpawnId must identify an existing one-based spawn")
    data = CONFIG_PREFIX.pack(
        CONFIG_MAGIC,
        VERSION,
        RECORD_SIZE,
        int(config.get("featureFlags", 0)),
        initial_spawn,
        u16(config.get("mainMatrixId", 0), "mainMatrixId"),
    )
    data += location(config["newGameStart"], "newGameStart")
    data += location(config["postGameCurrentPosition"], "postGameCurrentPosition")
    data += location(config["postGameSpecialSpawn"], "postGameSpecialSpawn")
    data += struct.pack("<I", 0)
    if len(data) != RECORD_SIZE:
        fail(f"internal config size error: {len(data)}")
    return data


def build_spawn(spawn, index):
    flags = 0
    if spawn.get("blackout", False):
        flags |= 1
    if spawn.get("fly", False):
        flags |= 2
    recovery = {"home": 0, "center": 1, "custom": 2}.get(spawn["recoveryKind"])
    if recovery is None:
        fail(f"spawn {index}: recoveryKind must be home, center, or custom")
    data = SPAWN_PREFIX.pack(
        SPAWN_MAGIC,
        VERSION,
        RECORD_SIZE,
        flags,
        recovery,
        0,
        0,
        u16(spawn.get("flypointFlagIndex", 0xFFFF), f"spawn {index} flypointFlagIndex"),
        u16(spawn.get("recoveryScriptId", 0xFFFF), f"spawn {index} recoveryScriptId"),
    )
    data += location(spawn["death"], f"spawn {index} death")
    data += location(spawn["flyDestination"], f"spawn {index} flyDestination")
    data += location(spawn["specialDestination"], f"spawn {index} specialDestination")
    data += struct.pack("<I", 0)
    if len(data) != RECORD_SIZE:
        fail(f"internal spawn size error: {len(data)}")
    return data


def validate_header_references(document, source):
    headers = source.parent / "members/headers"
    header_members = sorted(headers.iterdir(), key=lambda path: path.name)
    header_count = len(header_members)
    if [path.name for path in header_members] != [f"{i:04d}" for i in range(header_count)]:
        fail("Dynamic Header members must be contiguous from 0000")

    locations = []
    config = document["config"]
    for field in ("newGameStart", "postGameCurrentPosition", "postGameSpecialSpawn"):
        locations.append((f"config.{field}", config[field]))
    for index, spawn in enumerate(document["spawns"], 1):
        for field in ("death", "flyDestination", "specialDestination"):
            locations.append((f"spawn {index}.{field}", spawn[field]))

    for label, value in locations:
        if not isinstance(value, list) or len(value) != 5:
            fail(f"{label} must be [header, warp, x, y, direction]")
        header_id = int(value[0])
        if header_id < 0 or header_id >= header_count:
            fail(f"{label} references missing Header {header_id}; count is {header_count}")


def main():
    if len(sys.argv) != 3:
        fail("usage: build_world_data.py INPUT.json OUTPUT_DIRECTORY")
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    document = json.loads(source.read_text(encoding="utf-8"))
    if document.get("schemaVersion") != VERSION:
        fail(f"schemaVersion must be {VERSION}")
    spawns = document.get("spawns")
    if not isinstance(spawns, list) or not spawns:
        fail("spawns must contain at least one record")
    validate_header_references(document, source)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / "0000").write_bytes(build_config(document["config"], len(spawns)))
    for index, spawn in enumerate(spawns, 1):
        (output / f"{index:04d}").write_bytes(build_spawn(spawn, index))
    print(f"World Data: wrote 1 config and {len(spawns)} spawn members to {output}")


if __name__ == "__main__":
    main()
