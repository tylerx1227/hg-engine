# World Level Scripts

Header-owned level scripts are stored separately from ordinary scripts in
NARC 267 (`a/3/0/0`). This prevents the Header level-script namespace from
sharing IDs with regular map scripts or engine/common scripts.

## Current data contract

- Header offset `0x08` is a `u16` World Level Script member ID.
- The stripped foundation contains only member `0000`, a four-byte empty file.
- Header 000 references member 000 directly; the retired retail migration and
  its repopulation tool are no longer present in active source.
- The runtime loader clears the map event object's `0x100`-byte script-header
  buffer and reads the selected member from NARC 267.
- Members larger than `0x100` bytes are rejected by the build validator.

## Authoring ownership

DSPRE Tyler Fork detects NARC 267 and routes the Level Script Editor, Header
`Open Level Scripts` action, associated-file creation, import/export, save,
and Research Helper through this archive. In this mode, adding a level script
does not create a regular script file.

This separation makes World Level Script ID 000 a normal author-owned ID. New
members added by DSPRE are author-owned world content.

## Validation

`scripts/validate_world_level_script_routing.py` verifies the guarded ARM9
hook, the single empty member, and every Header reference. Tyler builds and
runtime-tests `test.nds`; the assistant must not build that ROM.
