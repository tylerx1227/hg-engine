#!/usr/bin/env python3
"""Validate global text banks that are permanent engine/project contracts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEXT_ROOT = ROOT / "data/text"

# These counts are the currently proven HGSS contracts. Changing wording is
# supported, but changing record counts requires auditing every numeric caller
# and deliberately updating this manifest.
PROTECTED_BANKS = {
    # HeaderHGSS.locationName is a byte. Bank 279 may therefore be rebuilt as
    # a custom 1..256-entry table; every current Header reference must be
    # updated before entries are removed or reordered.
    279: (1, 256, "primary location names selected by Header location-name IDs"),
    280: (77, 77, "secondary/met-location names"),
    281: (15, 15, "special met-location names"),
    445: (2, 2, "New Game player/friend default-name data"),
}


def main():
    for bank_id, (minimum_count, maximum_count, role) in PROTECTED_BANKS.items():
        path = TEXT_ROOT / f"{bank_id}.txt"
        if not path.is_file():
            raise RuntimeError(
                f"protected Global Text bank {bank_id} is missing ({role})"
            )
        lines = path.read_text(encoding="utf-8").splitlines()
        if not minimum_count <= len(lines) <= maximum_count:
            raise RuntimeError(
                f"protected Global Text bank {bank_id} has {len(lines)} records; "
                f"expected {minimum_count}..{maximum_count} ({role}). Audit consumers before "
                "changing this contract."
            )

    print(
        "Validated 4 source-owned protected Global Text banks "
        "(279, 280, 281, and 445)."
    )


if __name__ == "__main__":
    main()
