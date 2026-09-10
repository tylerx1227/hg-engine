#!/usr/bin/env python3
"""Read-only helper for locating named files in an NDS filesystem."""

from pathlib import Path
import hashlib
import sys

import ndspy.narc
import ndspy.rom


def walk(folder, prefix=""):
    for index, name in enumerate(folder.files):
        yield prefix + name, folder.firstID + index
    for name, child in folder.folders:
        yield from walk(child, prefix + name + "/")


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: inspect_rom_paths.py ROM SEARCH [SEARCH ...]")
    rom = ndspy.rom.NintendoDSRom.fromFile(Path(sys.argv[1]))
    if sys.argv[2] == "--narc":
        if len(sys.argv) < 5:
            raise SystemExit("usage: inspect_rom_paths.py ROM --narc PATH MEMBER [MEMBER ...]")
        wanted_path = sys.argv[3]
        paths = dict(walk(rom.filenames))
        if wanted_path not in paths:
            raise SystemExit(f"ROM path not found: {wanted_path}")
        narc = ndspy.narc.NARC(rom.files[paths[wanted_path]])
        print(f"{wanted_path}: {len(narc.files)} members")
        for value in sys.argv[4:]:
            member_id = int(value, 0)
            data = narc.files[member_id]
            digest = hashlib.sha256(data).hexdigest()
            preview = data[:32].hex(" ")
            print(f"{member_id:4d} {len(data):8d} sha256={digest} bytes={preview}")
        return

    needles = tuple(value.lower() for value in sys.argv[2:])
    for path, file_id in walk(rom.filenames):
        if any(needle in path.lower() for needle in needles):
            print(f"{file_id:4d} {len(rom.files[file_id]):8d} {path}")


if __name__ == "__main__":
    main()
