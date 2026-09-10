# World and Engine Scripts

The stock HGSS field-script archive mixed three unrelated ownership classes.
Tyler's fork separates both their author-facing identities and their physical
runtime archives.

- `a/0/1/2` contains only Header-owned **World Regular Scripts**.
- NARC 267 (`a/3/0/0`) contains only Header-owned **World Level Scripts**.
- NARC 269 (`a/3/0/2`) contains only protected **Engine Scripts**.

## Current stripped-world fixture

The proven retail regression fixture has now been removed from the active
foundation source:

- one editable no-op World Script remains as member `0000`;
- one editable empty World Level Script remains as member `0000`;
- 30 protected Engine Scripts are compact members `0000`–`0029`.

The sole Header 000 directly addresses World Script 000 and World Level Script
000. The retired retail migration manifests and repopulation tools were removed
after the user made the proven-source backup. HGE's modified common Script 003
and trainer Script 953 still build directly into protected Engine members 0003
and 0027.

Nintendo's original standard/common-script loader is retained byte-for-byte.
Its internal NARC ID 12 lookup is compatibility-routed to `a/3/0/2`, while the
custom current-map loader uses explicit World Script NARC ID 271 to reach
`a/0/1/2`. This avoids the replacement C loader that caused the Pokemon Center
asynchronous healing regression without merging either namespace again.

The native loader's 30-entry `sScriptBankMapping` is patched from retail
physical member numbers to the deterministic compact Engine IDs. The public
standard-script numbers and their Global Text banks are unchanged. Important
runtime routes include:

- common/misc and Nurse Joy: old 003 -> Engine 003;
- New Game `_std_init`: old 149 -> Engine 013;
- Apricorn trees: old 150 -> Engine 014;
- trainers: old 953 -> Engine 027;
- script ID zero fallback: old 140 -> Engine 006.

The validator checks all 30 mappings as one complete table, all 30 Engine
member entry tables and pointers, the zero-script fallback, the original loader
bytes, and both World Script loader call sites. A partial old/compact mapping is
rejected before a ROM can be packaged.

Protected Engine Scripts remain outside DSPRE's normal world-script namespace.
Adding or editing trainers later does not require exposing these engine members:
trainer data and trainer encounters remain author-owned, while Engine Script
027 is only the shared interpreter required to run those encounters.
