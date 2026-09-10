#!/usr/bin/env python3
"""Validate stripped-world WorldConfig ownership and its routing hooks."""

from pathlib import Path
import json
import re
import struct

from validation_binary import read_arm9, read_overlay


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
OVERLAY_1 = ROOT / "base/overlay/overlay_0001.bin"
CONFIG_SOURCE = ROOT / "src/world_config.c"
SPAWN_SOURCE = ROOT / "src/world_spawn.c"
ASM_SOURCE = ROOT / "asm/world_identity_hooks.s"
WORLD_DATA = ROOT / "world/world_data.json"
HOOKS = {
    0x3E398: (
        "New Game",
        bytes.fromhex("08 B5 FD F7 13 FB FD F7"),
        bytes.fromhex("00 4B 18 47"),
    ),
    0x52D40: (
        "Game Clear",
        bytes.fromhex("03 98 EB F7 11 FB 02 98"),
        bytes.fromhex("00 4B 18 47"),
    ),
    0x653A8: (
        "Escape Rope validity",
        bytes.fromhex("01 28 01 D1 00 20 10 BD"),
        bytes.fromhex("00 4B 18 47"),
    ),
    0x686AE: (
        "Dig validity",
        bytes.fromhex("01 28 01 D1 05 20 10 BD 00 20"),
        bytes.fromhex("01 4B 18 47 00 00"),
    ),
    0x43C44: (
        "dynamic-warp floor lookup",
        bytes.fromhex("F7 F7 90 FE 00 68 AA F1"),
        bytes.fromhex("00 4B 18 47"),
    ),
    0x534DE: (
        "Continue dynamic warp",
        bytes.fromhex("30 1C E8 F7 42 FA 01 1C 20 1C"),
        bytes.fromhex("01 4B 18 47 00 00"),
    ),
    0x5419E: (
        "direct dynamic warp",
        bytes.fromhex("E7 F7 E3 FB 01 1C 00 20 20 67"),
        bytes.fromhex("01 4B 18 47 00 00"),
    ),
    0x3B564: (
        "main-matrix predicate",
        bytes.fromhex("08 B5 FF F7 A1 FE 00 28"),
        bytes.fromhex("00 4B 18 47"),
    ),
    0x92C7A: (
        "Pokégear main-matrix loader",
        bytes.fromhex("3C 20 31 1C A8 F7 99 F9 02 A8"),
        bytes.fromhex("01 4B 18 47 00 00"),
    ),
    0x3C9D8: (
        "Pokédex geography fallback",
        bytes.fromhex("02 98 80 68 28 61 02 98"),
        bytes.fromhex("00 4B 18 47"),
    ),
    0x92C60: (
        "Pokégear geography fallback",
        bytes.fromhex("B0 68 02 A9 A0 60 F0 68"),
        bytes.fromhex("00 4B 18 47"),
    ),
}
OVERLAY_1_BASE = 0x021E5900
OVERLAY_1_HOOKS = {
    0x021E7BD8: (
        "dynamic Event warp",
        bytes.fromhex("53 F6 C6 FE 02 1C 03 CA"),
        bytes.fromhex("00 4B 18 47"),
    ),
}
OVERLAY_129_START = 0x023D8061
OVERLAY_129_END = 0x023E0001


def validate_source():
    config = CONFIG_SOURCE.read_text(encoding="utf-8")
    document = json.loads(WORLD_DATA.read_text(encoding="utf-8"))
    world_config = document["config"]
    if world_config["mainMatrixId"] != 0:
        raise RuntimeError(
            "Bootstrap WorldConfig must identify author-owned main Matrix 000."
        )
    if world_config["newGameStart"] != [0, -1, 6, 6, 1]:
        raise RuntimeError(
            "Bootstrap New Game must start on Header 000 at (6,6), direction 1."
        )
    if world_config["initialSpawnId"] != 1:
        raise RuntimeError(
            "Bootstrap WorldConfig initial spawn must be the sole one-based spawn 1."
        )
    if world_config["postGameCurrentPosition"] != [0, -1, 6, 6, 1]:
        raise RuntimeError(
            "Bootstrap postgame current position must route to Header 000."
        )
    if world_config["postGameSpecialSpawn"] != [0, -1, 6, 6, 1]:
        raise RuntimeError(
            "Bootstrap postgame special spawn must route to Header 000."
        )
    for fragment in (
        ".mainMatrixId = 0",
        ".newGameStart = { 0, -1, 6, 6, 1 }",
        ".postGameCurrentPosition = { 0, -1, 6, 6, 1 }",
        ".postGameSpecialSpawn = { 0, -1, 6, 6, 1 }",
    ):
        if fragment not in config:
            raise RuntimeError(f"Safe fallback WorldConfig is stale: {fragment}")
    if not re.search(
        r"extern\s+[^;]*\bLONG_CALL\s+Save_LocalFieldData_Get\s*\(",
        config,
        flags=re.DOTALL,
    ):
        raise RuntimeError(
            "World_SetNewGamePosition must call Save_LocalFieldData_Get with "
            "safe Thumb interworking."
        )

    spawn = SPAWN_SOURCE.read_text(encoding="utf-8")
    if "return World_GetConfig()->initialSpawnId;" not in spawn:
        raise RuntimeError(
            "World_GetInitialSpawnId is not sourced from ROM WorldConfig."
        )
    for fragment in ("NARC_New(NARC_WORLD_DATA, 0)", "WORLD_CONFIG_MAGIC"):
        if fragment not in config:
            raise RuntimeError(f"WorldConfig ROM loader is missing: {fragment}")
    for fragment in (
        "config->postGameCurrentPosition",
        "config->postGameSpecialSpawn",
        "World_GetConfig()->mainMatrixId",
        "World_MapHeader_GetMatrixId(mapId)",
        "World_GetMainMatrixMapId",
        "World_IsValidMapId((u32)location->mapId)",
        "localFieldData + 0x50",
    ):
        if fragment not in config:
            raise RuntimeError(f"WorldConfig postgame routing is missing: {fragment}")

    asm_source = ASM_SOURCE.read_text(encoding="utf-8")
    if "bl World_GetInitialSpawnId" not in asm_source:
        raise RuntimeError(
            "LocalFieldData initialization is not using World_GetInitialSpawnId."
        )
    for fragment in (
        ".global World_GameClearLocationsHook",
        "bl World_SetPostGameLocations",
        "ldr r3, =0x02052D4C | 1",
        ".global World_EscapeRopeValidityHook",
        ".global World_DigValidityHook",
        ".global World_DynamicWarpFloorGuardHook",
        ".global World_DynamicEventWarpGuardHook",
        ".global World_ContinueDynamicWarpGuardHook",
        ".global World_DirectDynamicWarpGuardHook",
        ".global World_LoadMainMatrixForPokegearHook",
        ".global World_PokedexGeographyFallbackHook",
        ".global World_PokegearGeographyFallbackHook",
        "bl World_FieldSystemHasValidSpecialSpawn",
        "bl World_LocationIsValid",
        "ldr r3, =0x021EE81C | 1",
        "ldr r3, =0x02043C4E | 1",
        "ldr r3, =0x021E7BE0 | 1",
        "ldr r3, =0x020534E8 | 1",
        "ldr r3, =0x02053502 | 1",
        "ldr r3, =0x020541A8 | 1",
        "bl World_GetMainMatrixMapId",
        "ldr r3, =0x0203AFB4 | 1",
        "add r0, sp, #8",
        "ldr r3, =0x02092C84 | 1",
        "ldr r3, =0x0203C9E4 | 1",
        "ldr r3, =0x02092C6C | 1",
    ):
        if fragment not in asm_source:
            raise RuntimeError(f"WorldConfig/Location hook is missing: {fragment}")


def validate_hook():
    arm9 = read_arm9(ARM9)
    for hook_offset, (label, retail_hook, hook_prefix) in HOOKS.items():
        actual = arm9[hook_offset:hook_offset + len(retail_hook)]
        if actual == retail_hook:
            continue
        if actual[:len(hook_prefix)] == hook_prefix:
            destination = struct.unpack_from("<I", actual, len(hook_prefix))[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue
        raise RuntimeError(
            f"WorldConfig {label} hook drift at ARM9+0x{hook_offset:06X}: "
            f"found {actual.hex(' ').upper()}. Stop before overwriting it."
        )

    overlay = read_overlay(OVERLAY_1)
    for address, (label, retail_hook, hook_prefix) in OVERLAY_1_HOOKS.items():
        offset = address - OVERLAY_1_BASE
        actual = overlay[offset:offset + len(retail_hook)]
        if actual == retail_hook:
            continue
        if actual[:len(hook_prefix)] == hook_prefix:
            destination = struct.unpack_from("<I", actual, len(hook_prefix))[0]
            if OVERLAY_129_START <= destination < OVERLAY_129_END:
                continue
        raise RuntimeError(
            f"WorldConfig {label} hook drift at Overlay 1 address 0x{address:08X}: "
            f"found {actual.hex(' ').upper()}. Stop before overwriting it."
        )


def main():
    validate_source()
    validate_hook()
    print(
        "Validated ROM-resident WorldConfig New Game, Game Clear, and "
        "field-return validity hooks."
    )


if __name__ == "__main__":
    main()
