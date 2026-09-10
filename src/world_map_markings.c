#include "world_map_markings.h"

#include "world_header.h"

static BOOL World_MapMarkingsSave_PayloadIs(
    const WorldMapMarkingsSave *markings,
    u16 packedIcons,
    u16 word
) {
    u32 i;

    if (markings->packedIcons != packedIcons) {
        return FALSE;
    }

    for (i = 0; i < NELEMS(markings->words); i++) {
        if (markings->words[i] != word) {
            return FALSE;
        }
    }

    return TRUE;
}

BOOL World_MapMarkingsSave_IsValid(WorldMapMarkingsSave *markings) {
    if (markings->mapId == WORLD_MAP_MARKINGS_MAP_NONE) {
        return FALSE;
    }

    // Retail zero-fills the entire Pokegear save block on a new game. It can
    // also reset a used slot to map ID zero with all icon/word fields set to
    // their null values. Recognize both legacy empty representations without
    // rejecting a populated Header 000 entry.
    if (markings->mapId == 0) {
        if (World_MapMarkingsSave_PayloadIs(markings, 0, 0) ||
            World_MapMarkingsSave_PayloadIs(
                markings,
                0xFFFF,
                WORLD_MAP_MARKING_WORD_NONE
            )) {
            return FALSE;
        }
    }

    return World_IsValidMapId(markings->mapId);
}

void World_MapMarkingsSave_Reset(WorldMapMarkingsSave *markings) {
    u32 i;

    markings->mapId = WORLD_MAP_MARKINGS_MAP_NONE;
    markings->packedIcons = 0xFFFF;
    for (i = 0; i < NELEMS(markings->words); i++) {
        markings->words[i] = WORLD_MAP_MARKING_WORD_NONE;
    }
}

void World_MapMarkingsRAM_Reset(WorldMapMarkingsRAM *markings) {
    u32 i;

    markings->mapId = WORLD_MAP_MARKINGS_MAP_NONE;
    for (i = 0; i < NELEMS(markings->icons); i++) {
        markings->icons[i] = WORLD_MAP_MARKING_ICON_NONE;
        markings->words[i] = WORLD_MAP_MARKING_WORD_NONE;
    }
}

BOOL World_MapMarkingsRAM_IsInUseEraseIfNot(WorldMapMarkingsRAM *markings) {
    u32 i;

    for (i = 0; i < NELEMS(markings->icons); i++) {
        if (markings->icons[i] != WORLD_MAP_MARKING_ICON_NONE ||
            markings->words[i] != WORLD_MAP_MARKING_WORD_NONE) {
            return TRUE;
        }
    }

    markings->mapId = WORLD_MAP_MARKINGS_MAP_NONE;
    return FALSE;
}
