#!/usr/bin/env python3
"""Validate stripped WorldSpawn ownership and US HeartGold hook baselines."""

from pathlib import Path
import json
import re
import struct


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
SOURCE = ROOT / "src/world_spawn.c"
WORLD_DATA = ROOT / "world/world_data.json"
ASM_SOURCE = ROOT / "asm/world_identity_hooks.s"
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001
# ARM9 file offset -> untouched US HeartGold function prefix.
HOOKS = {
    0x3BA74: bytes.fromhex("10 B5 0C 1C FF F7 F0 FF"),
    0x3BAAC: bytes.fromhex("10 B5 0C 1C FF F7 D4 FF"),
    0x3BAE8: bytes.fromhex("10 B5 0C 1C FF F7 B6 FF"),
    0x3BB20: bytes.fromhex("18 B4 0A 4B 00 22 1C 1C"),
    0x3BB50: bytes.fromhex("06 4B 00 22 D9 88 88 42"),
    0x3BB70: bytes.fromhex("38 B5 0F 4A 00 24 13 1C"),
}

BLACKOUT_HOOKS = {
    0x52692: bytes.fromhex("28 6A 00 68 3F 28 06 D1 00 22"),
    0x52932: bytes.fromhex("E9 F7 9D F8 07 1C E8 68 E9 F7"),
}

HOOK_PREFIX = bytes.fromhex("00 4B 18 47")


def validate_source_table():
    source = SOURCE.read_text(encoding="utf-8")
    for function in (
        "Save_VarsFlags_Get",
        "Save_VarsFlags_FlypointFlagAction",
        "Save_LocalFieldData_Get",
        "LocalFieldData_GetBlackoutSpawn",
    ):
        declaration = re.search(
            rf"extern\s+[^;]*\bLONG_CALL\s+{function}\s*\(",
            source,
            flags=re.DOTALL,
        )
        if declaration is None:
            raise RuntimeError(
                f"{function} must use LONG_CALL or its Thumb interworking veneer is unsafe."
            )

    document = json.loads(WORLD_DATA.read_text(encoding="utf-8"))
    rows = document["spawns"]
    if len(rows) != 1:
        raise RuntimeError(
            f"Bootstrap World Data contains {len(rows)} spawn rows; expected exactly 1."
        )
    row = rows[0]
    expected_locations = [0, -1, 6, 6, 1]
    if row.get("name") != "Bootstrap":
        raise RuntimeError("The sole WorldSpawn must be named Bootstrap.")
    if not row["blackout"] or row["fly"]:
        raise RuntimeError("Bootstrap spawn must allow blackout recovery and disable Fly.")
    if row["flypointFlagIndex"] != 0xFFFF or row["recoveryKind"] != "home":
        raise RuntimeError("Bootstrap spawn must use no Fly flag and safe home recovery.")
    if row.get("recoveryScriptId", 0xFFFF) != 0xFFFF:
        raise RuntimeError("Bootstrap spawn must use the protected default recovery script.")
    for field in ("death", "flyDestination", "specialDestination"):
        if row[field] != expected_locations:
            raise RuntimeError(f"Bootstrap spawn {field} must route to Header 000 at (6,6).")

    for fragment in (
        ".flags = WORLD_SPAWN_BLACKOUT",
        ".flypointFlagIndex = WORLD_FLYPOINT_NONE",
        ".deathWarp = { 0, -1, 6, 6, 1 }",
        ".flyWarp = { 0, -1, 6, 6, 1 }",
        ".specialWarp = { 0, -1, 6, 6, 1 }",
    ):
        if fragment not in source:
            raise RuntimeError(f"Safe fallback WorldSpawn is stale: {fragment}")

    required_source = (
        "NARC_New(NARC_WORLD_DATA, 0)",
        "NARC_ReadWholeMember",
        "WORLD_SPAWN_MAGIC",
        "World_BlackoutUsesHomeRecovery",
        "World_GetRecoveryKind(spawnId) == WORLD_RECOVERY_HOME",
    )
    for fragment in required_source:
        if fragment not in source:
            raise RuntimeError(
                f"WorldSpawn blackout routing is missing required source: {fragment}"
            )

    asm_source = ASM_SOURCE.read_text(encoding="utf-8")
    required_asm = (
        "bl World_GetInitialSpawnId",
        "World_BlackoutMessageKindHook",
        "ldr r3, =0x0205269C | 1",
        "ldr r3, =0x020526A8 | 1",
        "World_BlackoutScriptKindHook",
        "ldr r3, =0x02052946 | 1",
        "ldr r3, =0x02052954 | 1",
    )
    for fragment in required_asm:
        if fragment not in asm_source:
            raise RuntimeError(
                f"WorldSpawn blackout assembly is missing required routing: {fragment}"
            )


def validate_hooks():
    arm9 = ARM9.read_bytes()
    for offset, retail in HOOKS.items():
        actual = arm9[offset:offset + len(retail)]
        if actual == retail:
            continue

        if actual[:4] == HOOK_PREFIX:
            destination = struct.unpack_from("<I", actual, 4)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"WorldSpawn baseline drift at ARM9+0x{offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )

    for offset, retail in BLACKOUT_HOOKS.items():
        actual = arm9[offset:offset + len(retail)]
        if actual == retail:
            continue

        expected_prefix = bytes.fromhex("01 4B 18 47 00 00")
        if actual[:6] == expected_prefix:
            destination = struct.unpack_from("<I", actual, 6)[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue

        raise RuntimeError(
            f"WorldSpawn blackout baseline drift at ARM9+0x{offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop and investigate before overwriting it."
        )


def main():
    validate_source_table()
    validate_hooks()
    print("Validated 1 bootstrap WorldSpawn record, 6 table hooks, and 2 blackout routing hooks.")


if __name__ == "__main__":
    main()
