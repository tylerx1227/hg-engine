#include "world_spawn.h"
#include "world_config.h"
#include "world_narc.h"

extern void *LONG_CALL Save_VarsFlags_Get(void *saveData);
extern BOOL LONG_CALL Save_VarsFlags_FlypointFlagAction(
    void *varsFlags,
    int action,
    u32 flypointFlagIndex
);
extern void *LONG_CALL Save_LocalFieldData_Get(void *saveData);
extern u16 LONG_CALL LocalFieldData_GetBlackoutSpawn(void *localFieldData);

static WorldSpawn sWorldSpawnCache;
static u16 sWorldSpawnCacheId;
static u16 sWorldSpawnCount;
static BOOL sWorldSpawnCacheValid;
static BOOL sWorldSpawnCountValid;

static const WorldSpawn sFallbackWorldSpawn = {
    .magic = WORLD_SPAWN_MAGIC,
    .version = WORLD_DATA_VERSION,
    .recordSize = sizeof(WorldSpawn),
    .flags = WORLD_SPAWN_BLACKOUT,
    .recoveryKind = WORLD_RECOVERY_HOME,
    .flypointFlagIndex = WORLD_FLYPOINT_NONE,
    .recoveryScriptId = WORLD_SCRIPT_DEFAULT,
    .deathWarp = { 0, -1, 6, 6, 1 },
    .flyWarp = { 0, -1, 6, 6, 1 },
    .specialWarp = { 0, -1, 6, 6, 1 },
};

static BOOL World_SpawnIsValid(const WorldSpawn *spawn) {
    return spawn->magic == WORLD_SPAWN_MAGIC &&
           spawn->version == WORLD_DATA_VERSION &&
           spawn->recordSize == sizeof(WorldSpawn) &&
           spawn->recoveryKind <= WORLD_RECOVERY_CUSTOM;
}

static void *World_OpenDataNarc(void) {
    void *narc = NARC_New(NARC_WORLD_DATA, 0);
    if (narc == NULL) {
        GF_ASSERT(FALSE);
        return NULL;
    }
    if (NARC_GetFileCount(narc) < 2) {
        GF_ASSERT(FALSE);
        NARC_Delete(narc);
        return NULL;
    }
    sWorldSpawnCount = NARC_GetFileCount(narc) - 1;
    sWorldSpawnCountValid = TRUE;
    return narc;
}

u16 World_GetInitialSpawnId(void) {
    return World_GetConfig()->initialSpawnId;
}

u16 World_GetSpawnCount(void) {
    void *narc;
    if (sWorldSpawnCountValid) {
        return sWorldSpawnCount;
    }
    narc = World_OpenDataNarc();
    if (narc == NULL) {
        return 1;
    }
    NARC_Delete(narc);
    return sWorldSpawnCount;
}

BOOL World_IsValidSpawnId(u32 spawnId) {
    return spawnId > 0 && spawnId <= World_GetSpawnCount();
}

static const WorldSpawn *World_GetSpawnOrInitial(u32 spawnId) {
    void *narc;

    if (!World_IsValidSpawnId(spawnId)) {
        GF_ASSERT(FALSE);
        spawnId = World_GetInitialSpawnId();
    }
    if (sWorldSpawnCacheValid && sWorldSpawnCacheId == spawnId) {
        return &sWorldSpawnCache;
    }

    narc = World_OpenDataNarc();
    if (narc == NULL || spawnId > sWorldSpawnCount ||
        NARC_GetMemberSize(narc, spawnId) != sizeof(WorldSpawn)) {
        GF_ASSERT(FALSE);
        if (narc != NULL) {
            NARC_Delete(narc);
        }
        sWorldSpawnCache = sFallbackWorldSpawn;
    } else {
        NARC_ReadWholeMember(narc, spawnId, &sWorldSpawnCache);
        NARC_Delete(narc);
        if (!World_SpawnIsValid(&sWorldSpawnCache)) {
            GF_ASSERT(FALSE);
            sWorldSpawnCache = sFallbackWorldSpawn;
        }
    }
    sWorldSpawnCacheId = spawnId;
    sWorldSpawnCacheValid = TRUE;
    return &sWorldSpawnCache;
}

void World_GetFlyWarpData(u32 spawnId, WorldLocation *destination) {
    *destination = World_GetSpawnOrInitial(spawnId)->flyWarp;
}

void World_GetDeathWarpData(u32 spawnId, WorldLocation *destination) {
    *destination = World_GetSpawnOrInitial(spawnId)->deathWarp;
}

void World_GetSpecialSpawnWarpData(u32 spawnId, WorldLocation *destination) {
    *destination = World_GetSpawnOrInitial(spawnId)->specialWarp;
}

static u16 World_FindSpawnForMap(u32 mapId, BOOL death) {
    void *narc = World_OpenDataNarc();
    WorldSpawn spawn;
    u16 i;

    if (narc == NULL) {
        return 0;
    }
    for (i = 1; i <= sWorldSpawnCount; i++) {
        if (NARC_GetMemberSize(narc, i) != sizeof(WorldSpawn)) {
            continue;
        }
        NARC_ReadWholeMember(narc, i, &spawn);
        if (!World_SpawnIsValid(&spawn)) {
            continue;
        }
        if (death) {
            if ((spawn.flags & WORLD_SPAWN_BLACKOUT) &&
                spawn.deathWarp.mapId == (s32)mapId) {
                NARC_Delete(narc);
                return i;
            }
        } else if (spawn.flyWarp.mapId == (s32)mapId) {
            NARC_Delete(narc);
            return i;
        }
    }
    NARC_Delete(narc);
    return 0;
}

u16 World_FindDeathSpawnForMap(u32 mapId) {
    return World_FindSpawnForMap(mapId, TRUE);
}

u16 World_FindFlySpawnForMap(u32 mapId) {
    return World_FindSpawnForMap(mapId, FALSE);
}

void World_SetFlypointForMap(void *fieldSystem, u32 mapId) {
    u16 spawnId = World_FindFlySpawnForMap(mapId);
    void *saveData;
    void *varsFlags;
    const WorldSpawn *spawn;

    if (spawnId == 0) {
        return;
    }
    spawn = World_GetSpawnOrInitial(spawnId);
    if (!(spawn->flags & WORLD_SPAWN_FLY) ||
        spawn->flypointFlagIndex == WORLD_FLYPOINT_NONE) {
        return;
    }
    saveData = *(void **)((u8 *)fieldSystem + 0xC);
    varsFlags = Save_VarsFlags_Get(saveData);
    Save_VarsFlags_FlypointFlagAction(varsFlags, 1, spawn->flypointFlagIndex);
}

WorldRecoveryKind World_GetRecoveryKind(u32 spawnId) {
    return (WorldRecoveryKind)World_GetSpawnOrInitial(spawnId)->recoveryKind;
}

BOOL World_BlackoutUsesHomeRecovery(void *fieldSystem) {
    void *saveData = *(void **)((u8 *)fieldSystem + 0xC);
    void *localFieldData = Save_LocalFieldData_Get(saveData);
    u16 spawnId = LocalFieldData_GetBlackoutSpawn(localFieldData);

    return World_GetRecoveryKind(spawnId) == WORLD_RECOVERY_HOME;
}
