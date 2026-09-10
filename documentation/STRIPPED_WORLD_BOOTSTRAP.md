# Stripped World Bootstrap

The active foundation now starts from one author-owned world record in every
world collection that has completed routing:

- Header 000 (`BOOTSTRAP`)
- World Script 000 (one valid `End` script)
- World Level Script 000 (empty; no automatic trigger)
- World Text 000 (one valid empty message)
- Event File 000 (no objects, warps, triggers, or signs)
- Matrix 000 (`main`, 47x17)
- Map/LandData 000 (maintained blank template; zero buildings and neutral permissions)
- Area Data 000
- Map Texture 000
- Building Texture 000
- Building Configuration 000
- WorldSpawn 1 (safe Header-000 blackout/home route; Fly disabled)

Matrix 000 contains Header 000 in every Header cell, altitude zero in every
cell, author-owned LandData 000 in starting cell (0,0), and empty (`0xFFFF`)
LandData references everywhere else. Header 000 uses Area Data 000, which uses
map texture 000, building texture 000, and building configuration 000. Map 000
retains a valid model and terrain but contains no building records and no
retail-room placement data. The texture/config archives remain valid authoring
defaults. Building-model reindexing remains a separate dependency stage, but
the bootstrap Map no longer references any building model records.

The author-visible Header fields are neutralized where they do not affect that
geometry: world-map coordinates are (0,0), the protected location-name index is
000, and day/night music is the generic Mystery Zone track 1000.

No unrelated retail Header, World Script, World Level Script, World Text,
Event File, Map, Area Data, map texture, building texture, building
configuration, Fly destination, blackout destination, or internal map name
remains in the active foundation source. The 30 protected Engine Scripts and protected Global Text banks remain
isolated because the game engine still consumes them.

This change intentionally invalidates the world positions stored in old save
files. Runtime testing must start with a new in-game save. The minimum gate is:

1. Complete the Professor Oak opening and enter Header 000.
2. Confirm the room renders and the player can move.
3. Save, reset, and Continue from that new save.
4. Open the built ROM as a fresh DSPRE project and confirm exactly one Header,
   World Script, World Level Script, World Text bank, Event File, Map, Area
   Data, map texture, building texture, and building configuration.

The room has no warp because Event File 000 is intentionally empty. That is a
successful stripped-world condition, not a missing retail exit.
