#ifndef WORLD_CONFIG_H
#define WORLD_CONFIG_H

#include "world_spawn.h"

typedef struct WorldConfig {
    u32 magic;
    u16 version;
    u16 recordSize;
    u32 featureFlags;
    u16 initialSpawnId;
    u16 mainMatrixId;
    WorldLocation newGameStart;
    WorldLocation postGameCurrentPosition;
    WorldLocation postGameSpecialSpawn;
    u32 reserved;
} WorldConfig;

#define WORLD_CONFIG_MAGIC 0x4C525754

typedef char WorldConfigSizeMustBe80[sizeof(WorldConfig) == 80 ? 1 : -1];

const WorldConfig *World_GetConfig(void);
u32 World_GetMainMatrixMapId(void);
BOOL World_MapHeader_IsOnMainMatrix(u32 mapId);
BOOL World_LocationIsValid(const WorldLocation *location);
BOOL World_FieldSystemHasValidSpecialSpawn(void *fieldSystem);
void World_SetNewGamePosition(void *saveData);
void World_SetPostGameLocations(WorldLocation *currentPosition,
                                WorldLocation *specialSpawn);

#endif
