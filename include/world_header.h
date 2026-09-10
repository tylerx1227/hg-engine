#ifndef WORLD_HEADER_H
#define WORLD_HEADER_H

#include "types.h"

#define WORLD_HEADER_NARC_ID 50
#define WORLD_HEADER_SIZE    24
#define WORLD_HEADER_INVALID_ID 0xFFFFFFFF
#define WORLD_ENCOUNTER_NONE 0xFF
#define WORLD_MAP_TYPE_POKEMON_CENTER 5

typedef struct WorldMapHeader {
    u8 wildEncounterBank;
    u8 areaDataBank;
    u16 moveModelBank : 4;
    u16 worldMapX : 6;
    u16 worldMapY : 6;
    u16 matrixId;
    u16 scriptsBank;
    u16 scriptHeaderBank;
    u16 msgBank;
    u16 dayMusicId;
    u16 nightMusicId;
    u16 eventsBank;
    u16 mapsec : 8;
    u16 areaIcon : 4;
    u16 momCallIntroParam : 4;
    u32 regionNo : 1;
    u32 weather : 7;
    u32 mapType : 4;
    u32 cameraType : 6;
    u32 followMode : 2;
    u32 battleBg : 5;
    u32 bikeAllowed : 1;
    u32 runningAllowed_Unused : 1;
    u32 escapeRopeAllowed : 1;
    u32 flyAllowed : 1;
    u32 outgoingCalls : 1;
    u32 incomingCalls : 1;
    u32 radioSignal : 1;
} WorldMapHeader;

typedef char WorldMapHeaderSizeMustBe24[
    sizeof(WorldMapHeader) == WORLD_HEADER_SIZE ? 1 : -1
];

u16 World_GetHeaderCount(void);
BOOL World_IsValidMapId(u32 mapId);
const WorldMapHeader *World_GetMapHeader(u32 mapId);

u8 World_MapHeader_GetAreaDataBank(u32 mapId);
u16 World_MapHeader_GetMoveModelBank(u32 mapId);
u16 World_MapHeader_GetMatrixId(u32 mapId);
u16 World_MapHeader_GetMsgBank(u32 mapId);
u16 World_MapHeader_GetScriptsBank(u32 mapId);
u16 World_MapHeader_GetScriptHeaderBank(u32 mapId);
u16 World_MapHeader_GetDayMusicId(u32 mapId);
u16 World_MapHeader_GetNightMusicId(u32 mapId);
BOOL World_MapHeader_HasWildEncounters(u32 mapId);
u8 World_MapHeader_GetWildEncounterBank(u32 mapId);
u16 World_MapHeader_GetEventsBank(u32 mapId);
u32 World_MapHeader_GetMapSec(u32 mapId);
u8 World_MapHeader_GetAreaIcon(u32 mapId);
u8 World_MapHeader_GetMomCallIntroParam(u32 mapId);
u32 World_MapHeader_GetRegionNo(u32 mapId);
u32 World_MapHeader_GetWeatherType(u32 mapId);
u32 World_MapHeader_GetCameraType(u32 mapId);
u32 World_MapHeader_GetBattleBg(u32 mapId);
BOOL World_MapHeader_IsEscapeRopeAllowed(u32 mapId);
BOOL World_MapHeader_IsFlyAllowed(u32 mapId);
BOOL World_MapHeader_IsBikeAllowed(u32 mapId);
BOOL World_MapHeader_CanPlacePhoneCalls(u32 mapId);
BOOL World_MapHeader_CanReceivePhoneCalls(u32 mapId);
BOOL World_MapHeader_CanReceiveRadioSignal(u32 mapId);
u32 World_MapHeader_GetMapType(u32 mapId);
u8 World_MapHeader_GetFollowMode(u32 mapId);
void World_MapHeader_GetWorldMapCoords(u32 mapId, s16 *x, s16 *y);
BOOL World_MapHeader_MapIsPokemonCenter(u32 mapId);

#endif
