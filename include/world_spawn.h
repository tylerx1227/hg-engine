#ifndef WORLD_SPAWN_H
#define WORLD_SPAWN_H

#include "types.h"

#define WORLD_SPAWN_BLACKOUT (1 << 0)
#define WORLD_SPAWN_FLY      (1 << 1)
#define WORLD_FLYPOINT_NONE  0xFFFF
#define WORLD_SCRIPT_DEFAULT 0xFFFF
#define WORLD_SPAWN_MAGIC    0x50535754
#define WORLD_DATA_VERSION   1

typedef enum WorldRecoveryKind {
    WORLD_RECOVERY_HOME,
    WORLD_RECOVERY_CENTER,
    WORLD_RECOVERY_CUSTOM,
} WorldRecoveryKind;

typedef struct WorldLocation {
    s32 mapId;
    s32 warpId;
    s32 x;
    s32 z;
    s32 direction;
} WorldLocation;

typedef struct WorldSpawn {
    u32 magic;
    u16 version;
    u16 recordSize;
    u8 flags;
    u8 recoveryKind;
    u8 reserved0;
    u8 reserved1;
    u16 flypointFlagIndex;
    u16 recoveryScriptId;
    WorldLocation deathWarp;
    WorldLocation flyWarp;
    WorldLocation specialWarp;
    u32 reserved2;
} WorldSpawn;

typedef char WorldLocationSizeMustBe20[sizeof(WorldLocation) == 20 ? 1 : -1];
typedef char WorldSpawnSizeMustBe80[sizeof(WorldSpawn) == 80 ? 1 : -1];

u16 World_GetInitialSpawnId(void);
u16 World_GetSpawnCount(void);
BOOL World_IsValidSpawnId(u32 spawnId);
void World_GetFlyWarpData(u32 spawnId, WorldLocation *destination);
void World_GetDeathWarpData(u32 spawnId, WorldLocation *destination);
void World_GetSpecialSpawnWarpData(u32 spawnId, WorldLocation *destination);
u16 World_FindDeathSpawnForMap(u32 mapId);
u16 World_FindFlySpawnForMap(u32 mapId);
void World_SetFlypointForMap(void *fieldSystem, u32 mapId);
WorldRecoveryKind World_GetRecoveryKind(u32 spawnId);
BOOL World_BlackoutUsesHomeRecovery(void *fieldSystem);

#endif
