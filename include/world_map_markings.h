#ifndef WORLD_MAP_MARKINGS_H
#define WORLD_MAP_MARKINGS_H

#include "types.h"

#define WORLD_MAP_MARKINGS_MAP_NONE 0xFFFF
#define WORLD_MAP_MARKING_ICON_NONE  0xF
#define WORLD_MAP_MARKING_WORD_NONE  0xFFFF

typedef struct WorldMapMarkingsRAM {
    u32 mapId;
    u8 icons[4];
    u16 words[4];
} WorldMapMarkingsRAM;

typedef struct WorldMapMarkingsSave {
    u16 mapId;
    u16 packedIcons;
    u16 words[4];
} WorldMapMarkingsSave;

typedef char WorldMapMarkingsRAMSizeMustBe16[
    sizeof(WorldMapMarkingsRAM) == 16 ? 1 : -1
];
typedef char WorldMapMarkingsSaveSizeMustBe12[
    sizeof(WorldMapMarkingsSave) == 12 ? 1 : -1
];

BOOL World_MapMarkingsSave_IsValid(WorldMapMarkingsSave *markings);
void World_MapMarkingsSave_Reset(WorldMapMarkingsSave *markings);
void World_MapMarkingsRAM_Reset(WorldMapMarkingsRAM *markings);
BOOL World_MapMarkingsRAM_IsInUseEraseIfNot(WorldMapMarkingsRAM *markings);

#endif
