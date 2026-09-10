#include "message.h"
#include "pokemon.h"
#include "script.h"
#include "world_header.h"
#include "world_narc.h"

#define HEAP_ID_FIELD2 11

void World_LoadScriptsAndMessagesForCurrentMap(FieldSystem *fieldSystem, SCRIPTCONTEXT *ctx) {
    u32 mapId = fieldSystem->location->mapId;

    ctx->mapScripts = AllocAndReadWholeNarcMemberByIdPair(
        NARC_WORLD_SCRIPTS,
        World_MapHeader_GetScriptsBank(mapId),
        HEAP_ID_FIELD2
    );
    ctx->msg_data = NewMsgDataFromNarc(
        MSGDATA_LOAD_LAZY,
        NARC_WORLD_TEXT,
        World_MapHeader_GetMsgBank(mapId),
        HEAP_ID_FIELD2
    );
}
