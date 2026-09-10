#include "world_config.h"
#include "world_header.h"
#include "world_narc.h"

extern void *LONG_CALL Save_LocalFieldData_Get(void *saveData);

static WorldConfig sWorldConfig;
static BOOL sWorldConfigLoaded;

static const WorldConfig sFallbackWorldConfig = {
    .magic = WORLD_CONFIG_MAGIC,
    .version = WORLD_DATA_VERSION,
    .recordSize = sizeof(WorldConfig),
    .featureFlags = 0,
    .initialSpawnId = 1,
    .mainMatrixId = 0,
    .newGameStart = { 0, -1, 6, 6, 1 },
    .postGameCurrentPosition = { 0, -1, 6, 6, 1 },
    .postGameSpecialSpawn = { 0, -1, 6, 6, 1 },
    .reserved = 0,
};

static BOOL World_ConfigIsValid(const WorldConfig *config) {
    return config->magic == WORLD_CONFIG_MAGIC &&
           config->version == WORLD_DATA_VERSION &&
           config->recordSize == sizeof(WorldConfig) &&
           config->initialSpawnId > 0;
}

const WorldConfig *World_GetConfig(void) {
    void *narc;

    if (sWorldConfigLoaded) {
        return &sWorldConfig;
    }

    narc = NARC_New(NARC_WORLD_DATA, 0);
    if (narc == NULL || NARC_GetFileCount(narc) < 2 ||
        NARC_GetMemberSize(narc, 0) != sizeof(WorldConfig)) {
        GF_ASSERT(FALSE);
        if (narc != NULL) {
            NARC_Delete(narc);
        }
        sWorldConfig = sFallbackWorldConfig;
        sWorldConfigLoaded = TRUE;
        return &sWorldConfig;
    }

    NARC_ReadWholeMember(narc, 0, &sWorldConfig);
    NARC_Delete(narc);
    if (!World_ConfigIsValid(&sWorldConfig)) {
        GF_ASSERT(FALSE);
        sWorldConfig = sFallbackWorldConfig;
    }
    sWorldConfigLoaded = TRUE;
    return &sWorldConfig;
}

BOOL World_MapHeader_IsOnMainMatrix(u32 mapId) {
    return World_IsValidMapId(mapId) &&
           World_MapHeader_GetMatrixId(mapId) == World_GetConfig()->mainMatrixId;
}

u32 World_GetMainMatrixMapId(void) {
    const WorldConfig *config = World_GetConfig();
    u32 mapId;
    u32 headerCount;

    if (config->newGameStart.mapId >= 0 &&
        World_MapHeader_IsOnMainMatrix((u32)config->newGameStart.mapId)) {
        return (u32)config->newGameStart.mapId;
    }

    headerCount = World_GetHeaderCount();
    for (mapId = 0; mapId < headerCount; mapId++) {
        if (World_MapHeader_IsOnMainMatrix(mapId)) {
            return mapId;
        }
    }

    GF_ASSERT(FALSE);
    return config->newGameStart.mapId >= 0 ?
           (u32)config->newGameStart.mapId : WORLD_HEADER_INVALID_ID;
}

BOOL World_LocationIsValid(const WorldLocation *location) {
    return location != NULL && location->mapId >= 0 &&
           World_IsValidMapId((u32)location->mapId);
}

BOOL World_FieldSystemHasValidSpecialSpawn(void *fieldSystem) {
    void *saveData = *(void **)((u8 *)fieldSystem + 0xC);
    u8 *localFieldData = Save_LocalFieldData_Get(saveData);
    const WorldLocation *specialSpawn =
        (const WorldLocation *)(localFieldData + 0x50);

    return World_LocationIsValid(specialSpawn);
}

void World_SetNewGamePosition(void *saveData) {
    WorldLocation *currentPosition =
        (WorldLocation *)Save_LocalFieldData_Get(saveData);

    *currentPosition = World_GetConfig()->newGameStart;
}

void World_SetPostGameLocations(WorldLocation *currentPosition,
                                WorldLocation *specialSpawn) {
    const WorldConfig *config = World_GetConfig();

    *currentPosition = config->postGameCurrentPosition;
    *specialSpawn = config->postGameSpecialSpawn;
}
