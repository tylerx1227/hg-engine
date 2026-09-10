# Protected Global Text

The following `data/text` files are engine/global databases, not Header-owned
map dialogue:

- `279.txt` — primary location names indexed by the Header map-section field.
- `280.txt` — secondary/met-location names.
- `281.txt` — special met-location names.
- `445.txt` — New Game player/friend default-name data.

They are tracked source so an HG-Engine rebuild cannot silently restore their
contents from the donor ROM. Their wording may be customized here. Bank 279
may contain 1–256 entries because an HGSS Header stores its location-name ID in
one byte. Appending is safe; removing or reordering entries requires updating
every Header that refers to the affected indices. The other protected banks
retain fixed counts until their consumers are deliberately audited.

Tyler's author-facing World Text namespace is a separate archive (`a/3/0/1`,
NARC ID 268). The active stripped foundation contains only World Text 000, a
valid one-entry empty HGSS message bank. The temporary 398-bank retail fixture
and its migration tooling were removed after the proven-source backup.

Ordinary current-map dialogue now loads from World Text. Location names still
load from protected global bank 279. In the DSPRE fork, the normal Text Editor
and the Header Editor's `Open Texts` action target World Text. Location names are
reached separately through `Other Editors -> Location Names (Protected Global
Text)`; its archive selector is locked to bank 279.
