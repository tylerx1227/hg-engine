#!/usr/bin/env python3
"""One-time deterministic bootstrap of protected Engine Script members."""

from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil


OLD_MEMBERS = [
    0, 1, 2, 3, 4, 136, 140, 141, 143, 144,
    145, 146, 148, 149, 150, 151, 163, 164, 165, 166,
    167, 262, 263, 264, 265, 734, 952, 953, 954, 955,
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--dest", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    sources = {}
    for path in args.source.iterdir():
        if not path.is_file():
            continue
        match = re.search(r"(?:^|_)(\d{3,4})(?:\.[^.]*)?$", path.name)
        if match:
            sources.setdefault(int(match.group(1)), []).append(path)

    report = []
    for new_id, old_id in enumerate(OLD_MEMBERS):
        matches = sources.get(old_id, [])
        if len(matches) != 1:
            raise RuntimeError(
                f"Old Script {old_id:03d}: expected exactly one source member, found {matches}."
            )
        data = matches[0].read_bytes()
        report.append({
            "engine_id": new_id,
            "stock_id": old_id,
            "source": matches[0].name,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })

    print(json.dumps(report, indent=2))
    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply after verifying the source build.")
        return

    args.dest.mkdir(parents=True, exist_ok=True)
    existing = sorted(path.name for path in args.dest.iterdir() if path.is_file())
    if existing not in ([], ["0000"]):
        raise RuntimeError(
            "Refusing to overwrite an already-bootstrapped Engine Script directory."
        )
    if existing == ["0000"] and args.dest.joinpath("0000").read_bytes() != bytes.fromhex("02 00 00 00 13 FD 02 00"):
        raise RuntimeError("Engine Script 0000 is not the expected blank fixture.")

    for path in args.dest.iterdir():
        if path.is_file():
            path.unlink()
    for row in report:
        shutil.copy2(
            sources[row["stock_id"]][0],
            args.dest / f'{row["engine_id"]:04d}',
        )
    args.dest.parent.joinpath("engine_script_bootstrap_manifest.json").write_text(
        json.dumps({"format": 1, "members": report}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Bootstrapped protected Engine Scripts 0000..0029.")


if __name__ == "__main__":
    main()
