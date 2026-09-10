.text
.align 2
.thumb

.global World_MapRoleAbsent
.global World_UnionFeatureDisabled
World_MapRoleAbsent:
World_UnionFeatureDisabled:
    @ The stripped world has no Union Room or League Lobby role. This shared
    @ replacement is used for boolean map/reception checks and ScrCmd_286;
    @ returning FALSE also makes that command a harmless no-op instead of
    @ sending the player to Header 002.
    mov r0, #0
    bx lr

.align 2
.global World_PartyUnionMapRestrictionBypass
World_PartyUnionMapRestrictionBypass:
    @ Header 002 is an ordinary world Header, so skip the Griseous Orb message
    @ branch that used a direct current-map == 2 comparison.
    ldr r3, =0x0207C4B6 | 1
    bx r3

.pool

.align 2
.global World_OverlayUnionMapBypass
World_OverlayUnionMapBypass:
    @ Remove only Header 002 from this communication-map exclusion. Preserve
    @ the two genuine Wi-Fi battle-area IDs (4 and 5).
    cmp r1, #4
    beq 1f
    cmp r1, #5
    beq 1f
    ldr r2, =0x021F445C | 1
    bx r2
1:
    ldr r2, =0x021F4460 | 1
    bx r2

.pool

.align 2
.global World_PlayerAvatarMapIdNoneHook
World_PlayerAvatarMapIdNoneHook:
    @ Reproduce the four instructions displaced at 0x0205C568.
    mov r4, r0
    str r2, [sp, #0]
    mov r0, #1
    str r0, [sp, #4]

    @ The player object is not owned by a real map until normal field setup assigns it.
    mov r0, #0xFF
    lsl r0, #8
    add r0, #0xFF
    str r0, [sp, #8]

    @ Restore MapObject_Create's register arguments and continue at the first
    @ instruction not displaced by the absolute hook.
    mov r0, r1
    ldr r1, =0x0205C574 | 1
    bx r1

.pool

.align 2
.global World_ApricornMapIdNoneHook
World_ApricornMapIdNoneHook:
    @ The overlay hook uses r3 for its absolute jump. CreateJumpingApricornObj's
    @ prologue already saved the incoming r3 (the Z coordinate) at [sp, #12],
    @ so restore it from there before shuffling the call arguments. Using r1 as
    @ the jump register would destroy the incoming Apricorn sprite ID.

    @ Reproduce CreateJumpingApricornObj's stack arguments. The incoming r1
    @ is the Apricorn sprite ID; the final stack argument is a temporary
    @ MapObject owner and must not claim real world Header 001.
    str r1, [sp, #0]
    mov r4, #0
    str r4, [sp, #4]
    mov r1, #0xFF
    lsl r1, #8
    add r1, #0xFF
    str r1, [sp, #8]

    @ Finish the original register-argument shuffle. All four argument
    @ registers were live at the hook site, so r2's original Z coordinate is
    @ recovered from the r3 value saved by the retail function prologue.
    mov r1, r2
    ldr r2, [sp, #12]
    mov r3, #0

    @ Resume at the game's original BL MapObject_Create. r4 is no longer
    @ needed as the zero argument after r3 has been prepared, and the retail
    @ instruction after the call replaces r4 with the returned object.
    ldr r4, =0x02204AC0 | 1
    bx r4

.pool

.align 2
.global World_PhotoMapIdNoneHook
World_PhotoMapIdNoneHook:
    @ Replace the temporary photo object's map owner with 0xFFFF.
    mov r1, #0xFF
    lsl r1, #8
    add r1, #0xFF
    str r1, [sp, #8]

    @ Reproduce the remaining displaced argument setup. The original helper
    @ saved direction in r4 before this hook, so r2 is safe for the trampoline.
    mov r1, r3
    ldr r2, =0x0206AF1A | 1
    bx r2

.pool

.align 2
.global World_FollowerMapIdNoneHook
World_FollowerMapIdNoneHook:
    @ Reproduce the four instructions displaced at 0x0206A13C.
    str r0, [sp, #0]
    mov r0, #0x30
    str r0, [sp, #4]

    @ Leave r0 as the exact non-world MapObject owner 0x0000FFFF; the
    @ untouched instruction at 0x0206A144 stores it as argument seven.
    mov r0, #0xFF
    lsl r0, #8
    add r0, #0xFF
    ldr r3, =0x0206A144 | 1
    bx r3

.pool

.align 2
.global World_LocalFieldDataDefaultsHook
World_LocalFieldDataDefaultsHook:
    @ Save_LocalFieldData_Init has already zeroed all 0x80 bytes and initialized
    @ PlayerSaveData. Keep currentPosition untouched for the stock New Game
    @ start routine, but make every auxiliary Location explicitly invalid.
    mov r0, #0
    mvn r0, r0
    str r0, [r4, #0x14]  @ entrancePosition.mapId
    str r0, [r4, #0x18]  @ entrancePosition.warpId
    str r0, [r4, #0x28]  @ previousPosition.mapId
    str r0, [r4, #0x2C]  @ previousPosition.warpId
    str r0, [r4, #0x3C]  @ dynamicWarp.mapId
    str r0, [r4, #0x40]  @ dynamicWarp.warpId
    str r0, [r4, #0x50]  @ specialSpawn.mapId
    str r0, [r4, #0x54]  @ specialSpawn.warpId

    @ Seed the initial blackout destination from the HGE-owned WorldSpawn
    @ configuration rather than retaining retail's hardcoded spawn ID 1.
    bl World_GetInitialSpawnId
    mov r1, r4
    add r1, #0x68
    strh r0, [r1]
    pop {r4, pc}

.align 2
.global World_BlackoutMessageKindHook
World_BlackoutMessageKindHook:
    @ Blackout_DrawMessage used to recognize "home" solely as Header 063.
    @ Ask the saved WorldSpawn record instead. r5 is FieldSystem here.
    push {r2, lr}
    mov r0, r5
    bl World_BlackoutUsesHomeRecovery
    cmp r0, #0
    pop {r2, r3}
    mov lr, r3
    beq 1f

    @ The misaligned hook also displaced the home path's `mov r2, #0`.
    mov r2, #0
    ldr r3, =0x0205269C | 1
    bx r3
1:
    ldr r3, =0x020526A8 | 1
    bx r3

.pool

.align 2
.global World_BlackoutScriptKindHook
World_BlackoutScriptKindHook:
    @ Task_Blackout used to equate spawn ID 1 with Mom. Route the existing Mom
    @ and Pokemon Center scripts from WorldSpawn recovery metadata instead.
    push {r2, lr}
    mov r0, r5
    bl World_BlackoutUsesHomeRecovery
    cmp r0, #0
    pop {r2, r3}
    mov lr, r3
    beq 1f
    ldr r3, =0x02052946 | 1
    bx r3
1:
    ldr r3, =0x02052954 | 1
    bx r3

.pool

.align 2
.global World_GameClearLocationsHook
World_GameClearLocationsHook:
    @ CallTask_GameClear has already resolved both saved Location pointers.
    @ Replace its fixed Player Room / Outside Player Home copies with the two
    @ ROM-backed WorldConfig postgame destinations. Preserve eight-byte stack
    @ alignment across the C call and the callee-saved r4 register.
    push {r4, lr}
    ldr r0, [sp, #20]  @ original [sp, #12]: dynamicWarp/current position
    ldr r1, [sp, #16]  @ original [sp, #8]: specialSpawn
    bl World_SetPostGameLocations
    pop {r3, r4}
    mov lr, r4
    mov r4, r3

    @ The hook replaces both retail Location copy calls, so resume immediately
    @ after the second call.
    ldr r3, =0x02052D4C | 1
    bx r3

.pool

.align 2
.global World_EscapeRopeValidityHook
World_EscapeRopeValidityHook:
    @ ItemCheckUseFunc_EscapeRope reaches this point only after the ordinary
    @ cave and Header permission checks. The Ruins of Alph special case
    @ returns earlier and remains untouched because it does not consume the
    @ saved specialSpawn destination.
    cmp r0, #1
    bne 1f
    ldr r0, [r4, #0x14]  @ ItemCheckUseData.fieldSystem
    bl World_FieldSystemHasValidSpecialSpawn
    cmp r0, #0
    beq 1f
    mov r0, #0          @ ITEMUSEERROR_OKAY
    pop {r4, pc}
1:
    mov r0, #0
    mvn r0, r0          @ ITEMUSEERROR_OAKSWORDS / unavailable
    pop {r4, pc}

.align 2
.global World_DigValidityHook
World_DigValidityHook:
    @ FieldMove_CheckDig has already checked the map permissions, follower,
    @ and Rocket costume. Preserve the costume error and require a valid
    @ saved specialSpawn before reporting that Dig can be used.
    cmp r0, #1
    beq 1f
    ldr r0, [r4, #4]    @ FieldMoveCheckData.fieldSystem
    bl World_FieldSystemHasValidSpecialSpawn
    cmp r0, #0
    beq 2f
    mov r0, #0          @ FIELD_MOVE_RESPONSE_OK
    pop {r4, pc}
1:
    mov r0, #5          @ FIELD_MOVE_RESPONSE_NOT_NOW
    pop {r4, pc}
2:
    mov r0, #1          @ FIELD_MOVE_RESPONSE_NOT_HERE
    pop {r4, pc}

.pool

.align 2
.global World_DynamicWarpFloorGuardHook
World_DynamicWarpFloorGuardHook:
    @ Save_LocalFieldData_Get has returned the LocalFieldData pointer in r0.
    @ Do not pass the invalid map ID -1 to MapNumToFloorNo. Scripts receive a
    @ defined neutral floor value of zero until a real dynamic warp is set.
    add r0, #0x3C
    mov r5, r0
    bl World_LocationIsValid
    cmp r0, #0
    beq 1f
    ldr r0, [r5, #0]
    ldr r3, =0x021EE81C | 1  @ MapNumToFloorNo
    blx r3
    b 2f
1:
    mov r0, #0
2:
    ldr r3, =0x02043C4E | 1
    bx r3

.pool

.align 2
.global World_DynamicEventWarpGuardHook
World_DynamicEventWarpGuardHook:
    @ Save_LocalFieldData_Get has returned LocalFieldData in r0. A special
    @ Event warp (Header 0xFFF / anchor 0x100) must never copy an unset dynamic
    @ destination into the pending map load.
    add r0, #0x3C
    push {r0, r1}
    bl World_LocationIsValid
    pop {r1, r2}
    cmp r0, #0
    beq 1f

    @ Recreate the first displaced copy instruction, then resume the remaining
    @ retail Location copy with r2 advanced by eight bytes.
    mov r2, r1
    ldmia r2!, {r0, r1}
    ldr r3, =0x021E7BE0 | 1
    bx r3
1:
    mov r0, #0
    pop {r3, r4, r5, r6, r7, pc}

.pool

.align 2
.global World_ContinueDynamicWarpGuardHook
World_ContinueDynamicWarpGuardHook:
    @ The deferred/Union Continue flag has already been cleared and any valid
    @ reception exit has been generated. If no valid dynamic destination now
    @ exists, fall back to the normal Continue path instead of loading map -1.
    mov r0, r6
    add r0, #0x3C
    bl World_LocationIsValid
    cmp r0, #0
    beq 1f
    mov r1, r6
    add r1, #0x3C
    mov r0, r4
    ldr r3, =0x020534E8 | 1
    bx r3
1:
    ldr r3, =0x02053502 | 1
    bx r3

.pool

.align 2
.global World_DirectDynamicWarpGuardHook
World_DirectDynamicWarpGuardHook:
    @ ScrCmd_449's direct dynamic-warp task must be a harmless no-op until a
    @ script or engine path has stored a legitimate destination.
    add r0, #0x3C
    push {r0, r1}
    bl World_LocationIsValid
    pop {r1, r2}
    cmp r0, #0
    beq 1f
    mov r0, #0
    str r0, [r4, #0x70]
    ldr r3, =0x020541A8 | 1
    bx r3
1:
    pop {r4, pc}

.pool

.align 2
.global World_PokedexGeographyFallbackHook
World_PokedexGeographyFallbackHook:
    @ The Pokédex uses specialSpawn coordinates when an interior Header has no
    @ explicit world-map coordinates. An untouched new save has no such spawn;
    @ use the neutral origin rather than consuming uninitialised geography.
    push {r4, lr}
    ldr r0, [sp, #16]   @ original [sp, #8]: specialSpawn
    bl World_LocationIsValid
    cmp r0, #0
    beq 1f
    ldr r0, [sp, #16]
    ldr r1, [r0, #8]
    ldr r2, [r0, #12]
    b 2f
1:
    mov r1, #0
    mov r2, #0
2:
    str r1, [r5, #16]
    str r2, [r5, #20]
    pop {r3, r4}
    mov lr, r4
    mov r4, r3
    ldr r3, =0x0203C9E4 | 1
    bx r3

.pool

.align 2
.global World_PokegearGeographyFallbackHook
World_PokegearGeographyFallbackHook:
    @ Apply the same defined origin to Pokégear before it resolves a cell in
    @ the configurable main matrix.
    push {r6, lr}
    mov r0, r6
    bl World_LocationIsValid
    cmp r0, #0
    beq 1f
    ldr r0, [r6, #8]
    ldr r2, [r6, #12]
    b 2f
1:
    mov r0, #0
    mov r2, #0
2:
    str r0, [r4, #8]
    str r2, [r4, #12]
    pop {r3, r6}
    mov lr, r6
    mov r6, r3
    add r1, sp, #8
    add r1, #2
    ldr r3, =0x02092C6C | 1
    bx r3

.pool

.align 2
.global World_LoadMainMatrixForPokegearHook
World_LoadMainMatrixForPokegearHook:
    @ FieldSystem_InitPokegearArgs has allocated its temporary MapMatrix in
    @ r6. Replace MAP_NEW_BARK with a Header that belongs to the ROM-configured
    @ main matrix, then perform the displaced MapMatrix_Load call.
    push {r4, lr}
    bl World_GetMainMatrixMapId
    mov r1, r6
    ldr r3, =0x0203AFB4 | 1  @ MapMatrix_Load
    blx r3
    pop {r3, r4}
    mov lr, r4
    mov r4, r3
    @ The misaligned long hook also replaces the following `add r0, sp, #8`.
    add r0, sp, #8
    ldr r3, =0x02092C84 | 1
    bx r3

.pool

.align 2
.global World_PokegearNoSelectionHook
World_PokegearNoSelectionHook:
    @ This replaces the final eight bytes of the no-selection path in
    @ ov101_021EB1E0. r5 is the PokegearMapAppData pointer and 0x152 is its
    @ u16 lastSelectedMapID field.
    mov r1, #1
    neg r1, r1
    ldr r0, =0x152
    strh r1, [r5, r0]

    @ Reproduce the displaced stack teardown and return from the retail
    @ function. No continuation inside Overlay 101 is required.
    add sp, #32
    pop {r3, r4, r5, r6, r7, pc}

.pool
