#include "types.h"
#include "world_header.h"
#include "world_narc.h"

typedef struct WorldMapEventsPrefix {
    u32 counts[4];
    void *tables[4];
    u8 eventData[0x800];
    u8 scriptHeader[0x100];
} WorldMapEventsPrefix;

void World_MapScriptHeader_ReadFromNarc(void *events, u32 mapId) {
    WorldMapEventsPrefix *mapEvents = events;
    u16 bank = World_MapHeader_GetScriptHeaderBank(mapId);

    MI_CpuClearFast(mapEvents->scriptHeader, sizeof(mapEvents->scriptHeader));
    ReadWholeNarcMemberByIdPair(
        mapEvents->scriptHeader,
        NARC_WORLD_LEVEL_SCRIPTS,
        bank
    );
}
