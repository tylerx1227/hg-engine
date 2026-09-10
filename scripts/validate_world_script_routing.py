#!/usr/bin/env python3
"""Validate the stripped editable World Script archive and its loader."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parent.parent
HEADERS = ROOT / "world/members/headers"
MEMBERS = ROOT / "world/members/scripts"
NO_OP_SCRIPT = bytes.fromhex("02 00 00 00 13 FD 02 00")


def main():
    members = sorted(MEMBERS.iterdir(), key=lambda path: path.name)
    if [path.name for path in members] != ["0000"]:
        raise RuntimeError("Stripped world must contain exactly World Script 0000.")
    if members[0].read_bytes() != NO_OP_SCRIPT:
        raise RuntimeError("World Script 0000 must be the valid one-script End template.")

    for header_path in HEADERS.iterdir():
        actual = struct.unpack_from("<H", header_path.read_bytes(), 6)[0]
        if actual != 0:
            raise RuntimeError(f"Header {header_path.name} references missing World Script {actual}.")

    loader = (ROOT / "src/world_text.c").read_text(encoding="utf-8")
    if "NARC_WORLD_SCRIPTS" not in loader:
        raise RuntimeError("Current-map loader is not routed directly to World Scripts.")
    if "sWorldScriptToStock" in loader:
        raise RuntimeError("Obsolete compact-to-stock World Script translation is present.")

    narcs_mk = (ROOT / "narcs.mk").read_text(encoding="utf-8")
    if "cp $(SCR_SEQ_WORLD_MEMBERS) $(SCR_SEQ_DIR)/" not in narcs_mk:
        raise RuntimeError("NARC 12 is not built exclusively from editable World Scripts.")
    print("Validated stripped World Script 0000 and direct Header routing.")


if __name__ == "__main__":
    main()
