#include "world_header.h"

typedef struct WorldHeaderCache {
    WorldMapHeader header;
    u32 mapId;
    BOOL valid;
} WorldHeaderCache;

static WorldHeaderCache sWorldHeaderCache;
static u16 sWorldHeaderCount;
static BOOL sWorldHeaderCountValid;

static const WorldMapHeader sInvalidWorldHeader = {
    .wildEncounterBank = WORLD_ENCOUNTER_NONE,
    .areaDataBank = 0xFF,
    .moveModelBank = 0xF,
    .matrixId = 0xFFFF,
    .scriptsBank = 0xFFFF,
    .scriptHeaderBank = 0xFFFF,
    .msgBank = 0xFFFF,
    .eventsBank = 0xFFFF,
};

static void World_SetHeaderCount(void *narc) {
    sWorldHeaderCount = NARC_GetFileCount(narc);
    sWorldHeaderCountValid = TRUE;
}

u16 World_GetHeaderCount(void) {
    void *narc;

    if (sWorldHeaderCountValid) {
        return sWorldHeaderCount;
    }

    narc = NARC_New(WORLD_HEADER_NARC_ID, 0);
    if (narc == NULL) {
        GF_ASSERT(FALSE);
        return 0;
    }

    World_SetHeaderCount(narc);
    NARC_Delete(narc);
    return sWorldHeaderCount;
}

BOOL World_IsValidMapId(u32 mapId) {
    return mapId < World_GetHeaderCount();
}

const WorldMapHeader *World_GetMapHeader(u32 mapId) {
    void *narc;

    if (sWorldHeaderCache.valid && sWorldHeaderCache.mapId == mapId) {
        return &sWorldHeaderCache.header;
    }

    narc = NARC_New(WORLD_HEADER_NARC_ID, 0);
    if (narc == NULL) {
        GF_ASSERT(FALSE);
        return &sInvalidWorldHeader;
    }

    World_SetHeaderCount(narc);
    if (mapId >= sWorldHeaderCount ||
        NARC_GetMemberSize(narc, mapId) != sizeof(WorldMapHeader)) {
        GF_ASSERT(FALSE);
        NARC_Delete(narc);
        return &sInvalidWorldHeader;
    }

    NARC_ReadWholeMember(narc, mapId, &sWorldHeaderCache.header);
    NARC_Delete(narc);
    sWorldHeaderCache.mapId = mapId;
    sWorldHeaderCache.valid = TRUE;
    return &sWorldHeaderCache.header;
}

u8 World_MapHeader_GetAreaDataBank(u32 mapId) {
    return World_GetMapHeader(mapId)->areaDataBank;
}

u16 World_MapHeader_GetMoveModelBank(u32 mapId) {
    return World_GetMapHeader(mapId)->moveModelBank;
}

u16 World_MapHeader_GetMatrixId(u32 mapId) {
    return World_GetMapHeader(mapId)->matrixId;
}

u16 World_MapHeader_GetMsgBank(u32 mapId) {
    return World_GetMapHeader(mapId)->msgBank;
}

u16 World_MapHeader_GetScriptsBank(u32 mapId) {
    return World_GetMapHeader(mapId)->scriptsBank;
}

u16 World_MapHeader_GetScriptHeaderBank(u32 mapId) {
    return World_GetMapHeader(mapId)->scriptHeaderBank;
}

u16 World_MapHeader_GetDayMusicId(u32 mapId) {
    return World_GetMapHeader(mapId)->dayMusicId;
}

u16 World_MapHeader_GetNightMusicId(u32 mapId) {
    return World_GetMapHeader(mapId)->nightMusicId;
}

BOOL World_MapHeader_HasWildEncounters(u32 mapId) {
    return World_GetMapHeader(mapId)->wildEncounterBank != WORLD_ENCOUNTER_NONE;
}

u8 World_MapHeader_GetWildEncounterBank(u32 mapId) {
    return World_GetMapHeader(mapId)->wildEncounterBank;
}

u16 World_MapHeader_GetEventsBank(u32 mapId) {
    return World_GetMapHeader(mapId)->eventsBank;
}

u32 World_MapHeader_GetMapSec(u32 mapId) {
    return World_GetMapHeader(mapId)->mapsec;
}

u8 World_MapHeader_GetAreaIcon(u32 mapId) {
    return World_GetMapHeader(mapId)->areaIcon;
}

u8 World_MapHeader_GetMomCallIntroParam(u32 mapId) {
    return World_GetMapHeader(mapId)->momCallIntroParam;
}

u32 World_MapHeader_GetRegionNo(u32 mapId) {
    return World_GetMapHeader(mapId)->regionNo;
}

u32 World_MapHeader_GetWeatherType(u32 mapId) {
    return World_GetMapHeader(mapId)->weather;
}

u32 World_MapHeader_GetCameraType(u32 mapId) {
    return World_GetMapHeader(mapId)->cameraType;
}

u32 World_MapHeader_GetBattleBg(u32 mapId) {
    return World_GetMapHeader(mapId)->battleBg;
}

BOOL World_MapHeader_IsEscapeRopeAllowed(u32 mapId) {
    return World_GetMapHeader(mapId)->escapeRopeAllowed;
}

BOOL World_MapHeader_IsFlyAllowed(u32 mapId) {
    return World_GetMapHeader(mapId)->flyAllowed;
}

BOOL World_MapHeader_IsBikeAllowed(u32 mapId) {
    return World_GetMapHeader(mapId)->bikeAllowed;
}

BOOL World_MapHeader_CanPlacePhoneCalls(u32 mapId) {
    return World_GetMapHeader(mapId)->outgoingCalls;
}

BOOL World_MapHeader_CanReceivePhoneCalls(u32 mapId) {
    return World_GetMapHeader(mapId)->incomingCalls;
}

BOOL World_MapHeader_CanReceiveRadioSignal(u32 mapId) {
    return World_GetMapHeader(mapId)->radioSignal;
}

u32 World_MapHeader_GetMapType(u32 mapId) {
    return World_GetMapHeader(mapId)->mapType;
}

u8 World_MapHeader_GetFollowMode(u32 mapId) {
    return World_GetMapHeader(mapId)->followMode;
}

void World_MapHeader_GetWorldMapCoords(u32 mapId, s16 *x, s16 *y) {
    const WorldMapHeader *header = World_GetMapHeader(mapId);

    *x = header->worldMapX;
    *y = header->worldMapY;
}

BOOL World_MapHeader_MapIsPokemonCenter(u32 mapId) {
    return World_IsValidMapId(mapId) &&
           World_MapHeader_GetMapType(mapId) == WORLD_MAP_TYPE_POKEMON_CENTER;
}
