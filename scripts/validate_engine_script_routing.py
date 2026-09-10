#!/usr/bin/env python3
"""Validate protected Engine Script ownership and loader routing."""

from pathlib import Path
import hashlib
import json
import re
import struct


ROOT = Path(__file__).resolve().parent.parent
ARM9 = ROOT / "base/arm9.bin"
HOOK_OFFSET = 0x40168
VANILLA_PREFIX = bytes.fromhex("38 B5 0D 1C 11 1C 1C 1C")
HOOK_PREFIX = bytes.fromhex("00 4B 18 47")
MAPPING_OFFSET = 0xFA4A4
MAPPING_STOCK_BANKS = [
    263, 264, 2, 151, 952, 734, 144, 955, 954, 146,
    148, 136, 167, 166, 163, 149, 265, 143, 164, 0,
    4, 165, 262, 145, 141, 953, 953, 150, 1, 3,
]
MAPPING_THRESHOLDS = [
    10490, 10450, 10440, 10400, 10350, 10300, 10200, 10150, 10100, 10000,
    9950, 9900, 9850, 9800, 9700, 9600, 9500, 9300, 9200, 9100,
    9000, 8900, 8800, 8000, 7000, 5000, 3000, 2800, 2500, 2000,
]
MAPPING_MSG_BANKS = [
    433, 19, 748, 246, 726, 444, 209, 732, 733, 211,
    666, 40, 312, 43, 266, 40, 439, 204, 267, 14,
    46, 268, 427, 210, 199, 40, 40, 23, 20, 40,
]
EXPECTED_ENTRY_COUNTS = [
    3, 9, 3, 74, 18, 1, 1, 256, 1, 4,
    256, 19, 2, 1, 1, 29, 1, 6, 1, 13,
    3, 7, 1, 6, 2, 0, 12, 740, 1, 19,
]
MEMBERS = ROOT / "world/engine_scripts/members"
MANIFEST = ROOT / "world/engine_scripts/engine_script_bootstrap_manifest.json"
EXPECTED_STOCK_IDS = [
    0, 1, 2, 3, 4, 136, 140, 141, 143, 144,
    145, 146, 148, 149, 150, 151, 163, 164, 165, 166,
    167, 262, 263, 264, 265, 734, 952, 953, 954, 955,
]


def validate_hook():
    arm9 = ARM9.read_bytes()
    actual = arm9[HOOK_OFFSET:HOOK_OFFSET + 8]
    if actual == VANILLA_PREFIX:
        return
    # One build may begin from the immediately preceding experimental hook.
    # bytereplacement restores the exact retail prologue before packaging.
    if actual[:4] == HOOK_PREFIX:
        return
    raise RuntimeError(
        f"Engine Script loader hook drift at ARM9+0x{HOOK_OFFSET:06X}: "
        f"found {actual.hex(' ').upper()}. Stop before overwriting it."
    )


def validate_mapping_transition():
    arm9 = ARM9.read_bytes()
    actual_rows = [
        struct.unpack_from("<3H", arm9, MAPPING_OFFSET + index * 6)
        for index in range(30)
    ]
    if [row[0] for row in actual_rows] != MAPPING_THRESHOLDS:
        raise RuntimeError("Public standard-script thresholds have drifted.")
    if [row[2] for row in actual_rows] != MAPPING_MSG_BANKS:
        raise RuntimeError("Protected standard-script Global Text mappings have drifted.")
    actual_banks = [
        row[1] for row in actual_rows
    ]
    old_to_new = {stock_id: engine_id for engine_id, stock_id in enumerate(EXPECTED_STOCK_IDS)}
    compact_banks = [old_to_new[stock_id] for stock_id in MAPPING_STOCK_BANKS]
    if actual_banks not in (MAPPING_STOCK_BANKS, compact_banks):
        raise RuntimeError(
            "sScriptBankMapping is neither the intact pre-migration table nor "
            "the complete compact Engine Script table."
        )
    if arm9[0x40156:0x40158] not in (bytes.fromhex("8C 22"), bytes.fromhex("06 22")):
        raise RuntimeError("scriptId-zero Engine Script fallback has drifted.")


def validate_members():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest["members"]
    if [row["stock_id"] for row in rows] != EXPECTED_STOCK_IDS:
        raise RuntimeError("Engine Script bootstrap manifest mapping drifted.")
    if [row["engine_id"] for row in rows] != list(range(30)):
        raise RuntimeError("Engine Script IDs are not compact 0000..0029.")

    paths = sorted(MEMBERS.iterdir(), key=lambda path: path.name)
    if [path.name for path in paths] != [f"{i:04d}" for i in range(30)]:
        raise RuntimeError("Engine Script members are not exactly 0000..0029.")
    for row, path in zip(rows, paths):
        # Members 0003 and 0027 are rebuilt from their HGE armips sources and
        # may intentionally evolve. The other 28 remain exact bootstrap data.
        if row["engine_id"] in (3, 27):
            continue
        if path.stat().st_size != row["size"]:
            raise RuntimeError(f"Engine Script {path.name} size drifted.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise RuntimeError(f"Engine Script {path.name} content drifted.")

    for engine_id, (path, expected_count) in enumerate(zip(paths, EXPECTED_ENTRY_COUNTS)):
        data = path.read_bytes()
        sentinel_offset = next(
            (offset for offset in range(0, len(data) - 1, 4) if data[offset:offset + 2] == b"\x13\xFD"),
            None,
        )
        if sentinel_offset is None:
            raise RuntimeError(f"Engine Script {engine_id:04d} has no aligned script-table sentinel.")
        entry_count = sentinel_offset // 4
        if entry_count != expected_count:
            raise RuntimeError(
                f"Engine Script {engine_id:04d} exposes {entry_count} entries; "
                f"expected {expected_count}."
            )
        table_end = sentinel_offset + 2
        for index in range(entry_count):
            relative = struct.unpack_from("<i", data, index * 4)[0]
            target = index * 4 + 4 + relative
            if not table_end <= target < len(data):
                raise RuntimeError(
                    f"Engine Script {engine_id:04d} entry {index} points outside its bytecode."
                )

    common_source = (ROOT / "armips/scr_seq/scr_seq_00003_commonscript.s").read_text()
    trainer_source = (ROOT / "armips/scr_seq/scr_seq_00953_trainerscript.s").read_text()
    if '.create "world/engine_scripts/members/0003", 0' not in common_source:
        raise RuntimeError("HGE common Script 003 is not targeting protected Engine Script 003.")
    if '.create "world/engine_scripts/members/0027", 0' not in trainer_source:
        raise RuntimeError("HGE trainer Script 953 is not targeting protected Engine Script 027.")

    if (ROOT / "src/world_engine_scripts.c").exists():
        raise RuntimeError("The experimental replacement Engine Script loader is still present.")
    narc_source = (ROOT / "src/world_narc.c").read_text(encoding="utf-8")
    if '"a/3/0/2", /*  12:' not in narc_source:
        raise RuntimeError("Retail loader compatibility ID 12 is not routed to Engine Scripts.")
    replacements = (ROOT / "bytereplacement").read_text(encoding="utf-8")
    if "arm9 02040168 38 B5 0D 1C 11 1C 1C 1C" not in replacements:
        raise RuntimeError("Nintendo's standard-script loader prologue is not restored.")
    replacement_rows = {
        int(address, 16): bytes.fromhex(data)
        for address, data in re.findall(
            r"^arm9\s+([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2}\s*)+)$",
            replacements,
            flags=re.MULTILINE,
        )
    }
    old_to_new = {stock_id: engine_id for engine_id, stock_id in enumerate(EXPECTED_STOCK_IDS)}
    expected_compact = [old_to_new[stock_id] for stock_id in MAPPING_STOCK_BANKS]
    for index, engine_id in enumerate(expected_compact):
        address = 0x020FA4A6 + index * 6
        if replacement_rows.get(address) != struct.pack("<H", engine_id):
            raise RuntimeError(f"Missing compact Engine mapping patch at 0x{address:08X}.")
    if replacement_rows.get(0x02040156) != bytes.fromhex("06 22"):
        raise RuntimeError("scriptId-zero fallback is not patched to Engine Script 006.")


def main():
    validate_hook()
    validate_mapping_transition()
    validate_members()
    print("Validated 30 protected Engine Scripts and the native loader compatibility route.")


if __name__ == "__main__":
    main()
