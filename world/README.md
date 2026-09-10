# Tyler World Data

These folders are canonical build inputs for the custom-world namespace.

- `members/headers` builds the Dynamic Header archive (`a/0/5/0`).
- `members/scripts` builds editable World Scripts (`a/0/1/2`).
- `members/level_scripts` builds NARC 267 (`a/3/0/0`).
- `members/text` builds NARC 268 (`a/3/0/1`).
- `members/events` builds editable Event Files (`a/0/3/2`).
- `members/matrices` builds editable Matrices (`a/0/4/1`).
- `members/maps` builds editable Map/LandData files (`a/0/6/5`).
- `members/area_data` builds editable Area Data (`a/0/4/2`).
- `members/map_textures` builds editable map texture banks (`a/0/4/4`).
- `members/building_textures` builds editable building texture banks (`a/0/7/0`).
- `members/building_configs` builds matching building configurations (`a/0/4/3`).
- `mapname.bin` is the canonical internal Header-name table installed on every
  build; DSPRE uses its length to determine the Header count.
- `engine_scripts/members` builds NARC 269 (`a/3/0/2`).
- `world_data.json` builds NARC 270 (`a/3/0/3`). Member `0000` is the
  versioned global `TWRL` record and members `0001` onward are one-based,
  versioned `TWSP` spawn records. After the foundation ROM is built, this
  archive is edited through DSPRE's **HG-Engine World Settings** editor.

Member filenames must be a contiguous four-digit sequence beginning with
`0000`. Do not place notes, metadata, subdirectories, or other files inside a
member directory; the build intentionally rejects them.

The current bootstrap foundation contains exactly one member in each editable
world collection above. Matrix 000 is the 47x17 `main` matrix and contains one
populated starting cell. Map/LandData 000 is the maintained zero-building,
neutral-permissions template at `world/templates/hgss_blank_map.bin`; DSPRE uses
the identical template when adding Maps to a Tyler HGE project. Area Data, map
texture, building texture, and building configuration have been reindexed to
author-owned member 0000. Their unrelated retail siblings are not installed by
the build.

`world_data.json` is the canonical input only while rebuilding the HG-Engine
foundation. A later engine rebuild replaces NARC 270 with this file's values,
so DSPRE-authored settings must be synchronized deliberately before rebuilding
the foundation ROM.
