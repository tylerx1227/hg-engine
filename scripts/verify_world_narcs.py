#!/usr/bin/env python3
"""Post-build verification for Tyler's extended NARC namespace."""

from pathlib import Path
import re
import struct

import ndspy.narc


ROOT = Path(__file__).resolve().parent.parent
ARM9_BASE = 0x02000000
OVERLAY_129_BASE = 0x023D8060
OVERLAY_129_FILE_BASE = 0x023D8000
STOCK_TABLE_ADDRESS = 0x0210F210
REPOINT_SITES = (0x7520, 0x753C, 0x755C, 0x7578, 0x7598, 0x75B8, 0x7684, 0x7708)
CUSTOM_PATHS = ('a/3/0/0', 'a/3/0/1', 'a/3/0/2', 'a/3/0/3', 'a/0/1/2')
WORLD_HEADER_HOOKS = (
    ('World_MapHeader_GetAreaDataBank', 0x3B27C),
    ('World_MapHeader_GetMoveModelBank', 0x3B290),
    ('World_MapHeader_GetMatrixId', 0x3B2AC),
    ('World_MapHeader_GetMsgBank', 0x3B2C0),
    ('World_MapHeader_GetScriptsBank', 0x3B2D4),
    ('World_MapHeader_GetScriptHeaderBank', 0x3B2E8),
    ('World_MapHeader_GetDayMusicId', 0x3B2FC),
    ('World_MapHeader_GetNightMusicId', 0x3B310),
    ('World_MapHeader_HasWildEncounters', 0x3B324),
    ('World_MapHeader_GetWildEncounterBank', 0x3B344),
    ('World_MapHeader_GetEventsBank', 0x3B358),
    ('World_MapHeader_GetMapSec', 0x3B36C),
    ('World_MapHeader_GetAreaIcon', 0x3B388),
    ('World_MapHeader_GetMomCallIntroParam', 0x3B3A8),
    ('World_MapHeader_GetRegionNo', 0x3B3C8),
    ('World_MapHeader_GetWeatherType', 0x3B3E4),
    ('World_MapHeader_GetCameraType', 0x3B400),
    ('World_MapHeader_GetBattleBg', 0x3B41C),
    ('World_MapHeader_IsEscapeRopeAllowed', 0x3B438),
    ('World_MapHeader_IsFlyAllowed', 0x3B454),
    ('World_MapHeader_IsBikeAllowed', 0x3B470),
    ('World_MapHeader_CanPlacePhoneCalls', 0x3B48C),
    ('World_MapHeader_CanReceivePhoneCalls', 0x3B4A8),
    ('World_MapHeader_CanReceiveRadioSignal', 0x3B4C4),
    ('World_MapHeader_GetMapType', 0x3B4DC),
    ('World_MapHeader_GetFollowMode', 0x3B4F8),
    ('World_MapHeader_GetWorldMapCoords', 0x3B518),
    ('World_MapHeader_MapIsPokemonCenter', 0x3B5DC),
)
WORLD_IDENTITY_HOOKS = (
    ('World_LocalFieldDataDefaultsHook', 0x3B94C, bytes.fromhex('00 4B 18 47')),
    ('World_PlayerAvatarMapIdNoneHook', 0x5C568, bytes.fromhex('00 4D 28 47')),
    ('World_FollowerMapIdNoneHook', 0x6A13C, bytes.fromhex('00 4B 18 47')),
    ('World_PhotoMapIdNoneHook', 0x6AF14, bytes.fromhex('00 4A 10 47')),
)
OVERLAY_1_BASE = 0x021E5900
WORLD_IDENTITY_OVERLAY_1_HOOKS = (
    ('World_ApricornMapIdNoneHook', 0x02204AB0, bytes.fromhex('00 4B 18 47')),
)
WORLD_ROLE_ARM9_HOOKS = (
    ('World_UnionFeatureDisabled', 0x3B5CC, bytes.fromhex('00 4B 18 47')),
    ('World_MapRoleAbsent', 0x3B5FC, bytes.fromhex('00 4B 18 47')),
    ('World_UnionFeatureDisabled', 0x5337C, bytes.fromhex('00 4B 18 47')),
    ('World_UnionFeatureDisabled', 0x44480, bytes.fromhex('00 4B 18 47')),
    ('World_PartyUnionMapRestrictionBypass', 0x7C480, bytes.fromhex('00 4B 18 47')),
)
WORLD_ROLE_OVERLAY_1_HOOKS = (
    ('World_OverlayUnionMapBypass', 0x021F4450, bytes.fromhex('00 4A 10 47')),
)
WORLD_MAP_MARKING_HOOKS = (
    ('World_MapMarkingsSave_IsValid', 0x2F370, bytes.fromhex('00 4B 18 47')),
    ('World_MapMarkingsSave_Reset', 0x2F388, bytes.fromhex('00 4B 18 47')),
    ('World_MapMarkingsRAM_Reset', 0x2F3DC, bytes.fromhex('00 4B 18 47')),
    ('World_MapMarkingsRAM_IsInUseEraseIfNot', 0x2F400, bytes.fromhex('00 4B 18 47')),
)
WORLD_POKEGEAR_DIRECT_PATCHES = (
    (0x021E7B08, bytes.fromhex('E7 43')),
    (0x021EA3A2, bytes.fromhex('08 04 12 D5')),
    (0x021ED618, bytes.fromhex('02 DA')),
)
WORLD_POKEGEAR_HOOKS = (
    ('World_PokegearNoSelectionHook', 0x021EB20E, bytes.fromhex('01 4B 18 47 00 00')),
)
WORLD_SPAWN_HOOKS = (
    ('World_GetFlyWarpData', 0x3BA74),
    ('World_GetDeathWarpData', 0x3BAAC),
    ('World_GetSpecialSpawnWarpData', 0x3BAE8),
    ('World_FindDeathSpawnForMap', 0x3BB20),
    ('World_FindFlySpawnForMap', 0x3BB50),
    ('World_SetFlypointForMap', 0x3BB70),
)
WORLD_SPAWN_EXTERNAL_THUMB_TARGETS = (
    ('Save_VarsFlags_Get', 0x020503D1),
    ('Save_VarsFlags_FlypointFlagAction', 0x02066931),
)
WORLD_BLACKOUT_HOOKS = (
    ('World_BlackoutMessageKindHook', 0x52692),
    ('World_BlackoutScriptKindHook', 0x52932),
)
WORLD_BLACKOUT_EXTERNAL_THUMB_TARGETS = (
    ('Save_LocalFieldData_Get', 0x0203B9C5),
    ('LocalFieldData_GetBlackoutSpawn', 0x0203B995),
)
WORLD_CONFIG_HOOKS = (
    ('World_SetNewGamePosition', 0x3E398, bytes.fromhex('00 4B 18 47')),
    ('World_GameClearLocationsHook', 0x52D40, bytes.fromhex('00 4B 18 47')),
    ('World_EscapeRopeValidityHook', 0x653A8, bytes.fromhex('00 4B 18 47')),
    ('World_DigValidityHook', 0x686AE, bytes.fromhex('01 4B 18 47 00 00')),
    ('World_DynamicWarpFloorGuardHook', 0x43C44, bytes.fromhex('00 4B 18 47')),
    ('World_ContinueDynamicWarpGuardHook', 0x534DE, bytes.fromhex('01 4B 18 47 00 00')),
    ('World_DirectDynamicWarpGuardHook', 0x5419E, bytes.fromhex('01 4B 18 47 00 00')),
    ('World_MapHeader_IsOnMainMatrix', 0x3B564, bytes.fromhex('00 4B 18 47')),
    ('World_PokedexGeographyFallbackHook', 0x3C9D8, bytes.fromhex('00 4B 18 47')),
    ('World_PokegearGeographyFallbackHook', 0x92C60, bytes.fromhex('00 4B 18 47')),
    ('World_LoadMainMatrixForPokegearHook', 0x92C7A, bytes.fromhex('01 4B 18 47 00 00')),
)
WORLD_LOCATION_OVERLAY_1_HOOKS = (
    ('World_DynamicEventWarpGuardHook', 0x021E7BD8, bytes.fromhex('00 4B 18 47')),
)
WORLD_CONFIG_EXTERNAL_THUMB_TARGETS = (
    ('Save_LocalFieldData_Get', 0x0203B9C5),
)
ARCHIVES = (
    ('world/members/scripts', 'base/root/a/0/1/2'),
    ('world/members/level_scripts', 'base/root/a/3/0/0'),
    ('world/members/text', 'base/root/a/3/0/1'),
    ('world/members/headers', 'base/root/a/0/5/0'),
    ('world/members/events', 'base/root/a/0/3/2'),
    ('world/members/matrices', 'base/root/a/0/4/1'),
    ('world/members/maps', 'base/root/a/0/6/5'),
    ('world/members/area_data', 'base/root/a/0/4/2'),
    ('world/members/map_textures', 'base/root/a/0/4/4'),
    ('world/members/building_textures', 'base/root/a/0/7/0'),
    ('world/members/building_configs', 'base/root/a/0/4/3'),
    ('world/engine_scripts/members', 'base/root/a/3/0/2'),
    ('build/world_data_members', 'base/root/a/3/0/3'),
)
WORLD_RESOURCE_LOADER_HOOKS = (
    ('World_MapScriptHeader_ReadFromNarc', 0x3B8C4),
    ('World_LoadScriptsAndMessagesForCurrentMap', 0x4018C),
)
NATIVE_ENGINE_LOADER_PREFIX = bytes.fromhex('38 B5 0D 1C 11 1C 1C 1C')
ENGINE_MAPPING_OFFSET = 0xFA4A4
ENGINE_MAPPING_STOCK_BANKS = (
    263, 264, 2, 151, 952, 734, 144, 955, 954, 146,
    148, 136, 167, 166, 163, 149, 265, 143, 164, 0,
    4, 165, 262, 145, 141, 953, 953, 150, 1, 3,
)
ENGINE_STOCK_IDS = (
    0, 1, 2, 3, 4, 136, 140, 141, 143, 144,
    145, 146, 148, 149, 150, 151, 163, 164, 165, 166,
    167, 262, 263, 264, 265, 734, 952, 953, 954, 955,
)


def fail(message: str):
    raise RuntimeError(f'World NARC verification failed: {message}')


def read_symbol(symbol: str) -> int:
    pattern = re.compile(rf'^{re.escape(symbol)}:\s+([0-9A-Fa-f]+)\s*$')
    for line in (ROOT / 'offsets.ini').read_text(encoding='UTF-8').splitlines():
        match = pattern.match(line)
        if match:
            return int(match.group(1), 16)
    fail(f'{symbol} is missing from offsets.ini')


def read_c_string(data: bytes, address: int) -> str:
    offset = address - OVERLAY_129_BASE
    if offset < 0 or offset >= len(data):
        fail(f'custom path pointer 0x{address:08X} is outside Overlay 129')
    end = data.find(b'\0', offset)
    if end < 0:
        fail(f'custom path at 0x{address:08X} is not NUL terminated')
    return data[offset:end].decode('ascii')


def overlay_129_file_offset(address: int) -> int:
    """Map a linked Overlay 129 address into the packaged overlay file.

    build/output.bin begins at 0x023D8060, but scripts/make.py inserts it at
    file offset 0x60 in base/overlay/overlay_0129.bin.  The packaged file is
    therefore addressed from 0x023D8000, not OVERLAY_129_BASE.
    """
    return address - OVERLAY_129_FILE_BASE


def verify_table_and_repoints():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    overlay = (ROOT / 'build/output.bin').read_bytes()
    table_address = read_symbol('gWorldNarcFileList')

    for site in REPOINT_SITES:
        actual = struct.unpack_from('<I', arm9, site)[0]
        if actual != table_address:
            fail(f'ARM9+0x{site:06X} contains 0x{actual:08X}, not 0x{table_address:08X}')

    table_offset = table_address - OVERLAY_129_BASE
    if table_offset < 0 or table_offset + 272 * 4 > len(overlay):
        fail('gWorldNarcFileList is outside the linked Overlay 129 image')
    extended = struct.unpack_from('<272I', overlay, table_offset)

    stock_offset = STOCK_TABLE_ADDRESS - ARM9_BASE
    stock = struct.unpack_from('<267I', arm9, stock_offset)
    if extended[:12] != stock[:12] or extended[13:267] != stock[13:267]:
        fail('Retail NARC IDs other than compatibility ID 12 changed')
    if read_c_string(overlay, extended[12]) != 'a/3/0/2':
        fail('compatibility ID 12 does not route Nintendo\'s native loader to Engine Scripts')

    actual_custom_paths = tuple(read_c_string(overlay, pointer) for pointer in extended[267:])
    if actual_custom_paths != CUSTOM_PATHS:
        fail(f'custom paths are {actual_custom_paths}, expected {CUSTOM_PATHS}')

    print(f'Extended table verified at 0x{table_address:08X}; all eight ARM9 repoints match.')


def verify_world_header_hooks():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    expected_prefix = bytes.fromhex('00 4B 18 47')
    for symbol, offset in WORLD_HEADER_HOOKS:
        actual_prefix = arm9[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )
    print(f'All {len(WORLD_HEADER_HOOKS)} Dynamic Header accessor hooks verified.')


def verify_world_identity_hooks():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    for symbol, offset, expected_prefix in WORLD_IDENTITY_HOOKS:
        actual_prefix = arm9[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    overlay_1 = (ROOT / 'base/overlay/overlay_0001.bin').read_bytes()
    for symbol, address, expected_prefix in WORLD_IDENTITY_OVERLAY_1_HOOKS:
        offset = address - OVERLAY_1_BASE
        actual_prefix = overlay_1[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', overlay_1, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} hook at Overlay 1 address 0x{address:08X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    total = len(WORLD_IDENTITY_HOOKS) + len(WORLD_IDENTITY_OVERLAY_1_HOOKS)
    print(f'All {total} World identity hooks verified.')


def verify_world_role_gates():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    for symbol, offset, expected_prefix in WORLD_ROLE_ARM9_HOOKS:
        actual_prefix = arm9[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} role gate at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    overlay_1 = (ROOT / 'base/overlay/overlay_0001.bin').read_bytes()
    for symbol, address, expected_prefix in WORLD_ROLE_OVERLAY_1_HOOKS:
        offset = address - OVERLAY_1_BASE
        actual_prefix = overlay_1[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', overlay_1, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} role gate at Overlay 1 address 0x{address:08X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    total = len(WORLD_ROLE_ARM9_HOOKS) + len(WORLD_ROLE_OVERLAY_1_HOOKS)
    print(f'All {total} stripped-world role gates verified.')


def verify_world_map_marking_hooks():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    for symbol, offset, expected_prefix in WORLD_MAP_MARKING_HOOKS:
        actual_prefix = arm9[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    print(f'All {len(WORLD_MAP_MARKING_HOOKS)} Map Markings sentinel hooks verified.')


def verify_world_pokegear_patches():
    overlay_base = 0x021E7740
    overlay = (ROOT / 'base/overlay/overlay_0101.bin').read_bytes()
    if len(overlay) != 0x13BC0:
        fail(f'Overlay 101 was not decompressed to its audited runtime size: {len(overlay)}')

    y9 = (ROOT / 'base/overarm9.bin').read_bytes()
    compression = struct.unpack_from('<I', y9, 101 * 0x20 + 0x1C)[0]
    if compression != 0:
        fail(f'Overlay 101 still has compression metadata 0x{compression:08X}')

    for address, expected in WORLD_POKEGEAR_DIRECT_PATCHES:
        offset = address - overlay_base
        actual = overlay[offset:offset + len(expected)]
        if actual != expected:
            fail(
                f'Pokegear patch at 0x{address:08X} is {actual.hex(" ").upper()}, '
                f'expected {expected.hex(" ").upper()}'
            )

    for symbol, address, expected_prefix in WORLD_POKEGEAR_HOOKS:
        offset = address - overlay_base
        actual_prefix = overlay[offset:offset + len(expected_prefix)]
        actual_pointer = struct.unpack_from('<I', overlay, offset + len(expected_prefix))[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} Pokegear hook at 0x{address:08X} is '
                f'{actual_prefix.hex(" ").upper()} -> 0x{actual_pointer:08X}, '
                f'expected {expected_prefix.hex(" ").upper()} -> 0x{expected_pointer:08X}'
            )

    total = len(WORLD_POKEGEAR_DIRECT_PATCHES) + len(WORLD_POKEGEAR_HOOKS)
    print(f'All {total} Pokegear Header 000 reclamation sites verified.')


def verify_world_spawn_hooks():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    expected_prefix = bytes.fromhex('00 4B 18 47')
    for symbol, offset in WORLD_SPAWN_HOOKS:
        actual_prefix = arm9[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} WorldSpawn hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    # LONG_CALL must retain bit 0 on these function addresses. A linker-created
    # ARM-state veneer to the even address crashes as soon as a Fly map matches.
    overlay_129 = (ROOT / 'base/overlay/overlay_0129.bin').read_bytes()
    function_offset = overlay_129_file_offset(read_symbol('World_SetFlypointForMap'))
    function_code = overlay_129[function_offset:function_offset + 0x100]
    for label, target in WORLD_SPAWN_EXTERNAL_THUMB_TARGETS:
        encoded = struct.pack('<I', target)
        if encoded not in function_code:
            fail(
                f'{label} Thumb target 0x{target:08X} is absent from Overlay 129; '
                'the WorldSpawn call may have lost LONG_CALL interworking.'
            )
    if function_code.count(bytes.fromhex('98 47')) < 2:
        fail('World_SetFlypointForMap does not contain both required BLX r3 calls.')

    expected_blackout_prefix = bytes.fromhex('01 4B 18 47 00 00')
    for symbol, offset in WORLD_BLACKOUT_HOOKS:
        actual_prefix = arm9[offset:offset + 6]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 6)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_blackout_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} blackout hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    blackout_function_offset = overlay_129_file_offset(
        read_symbol('World_BlackoutUsesHomeRecovery')
    )
    blackout_function_code = overlay_129[blackout_function_offset:blackout_function_offset + 0x100]
    for label, target in WORLD_BLACKOUT_EXTERNAL_THUMB_TARGETS:
        if struct.pack('<I', target) not in blackout_function_code:
            fail(
                f'{label} Thumb target 0x{target:08X} is absent from the blackout helper; '
                'its LONG_CALL interworking may be unsafe.'
            )
    if blackout_function_code.count(bytes.fromhex('98 47')) < 2:
        fail('World_BlackoutUsesHomeRecovery does not contain both required BLX r3 calls.')

    total = len(WORLD_SPAWN_HOOKS) + len(WORLD_BLACKOUT_HOOKS)
    print(f'All {total} WorldSpawn and blackout hooks verified.')


def verify_world_config_hooks():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    for symbol, offset, expected_prefix in WORLD_CONFIG_HOOKS:
        actual_prefix = arm9[offset:offset + len(expected_prefix)]
        actual_pointer = struct.unpack_from('<I', arm9, offset + len(expected_prefix))[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} WorldConfig hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    overlay_1 = (ROOT / 'base/overlay/overlay_0001.bin').read_bytes()
    for symbol, address, expected_prefix in WORLD_LOCATION_OVERLAY_1_HOOKS:
        offset = address - OVERLAY_1_BASE
        actual_prefix = overlay_1[offset:offset + len(expected_prefix)]
        actual_pointer = struct.unpack_from(
            '<I', overlay_1, offset + len(expected_prefix)
        )[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} Location guard at Overlay 1 address 0x{address:08X} '
                f'targets 0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )

    overlay_129 = (ROOT / 'base/overlay/overlay_0129.bin').read_bytes()
    function_offset = overlay_129_file_offset(read_symbol('World_SetNewGamePosition'))
    function_code = overlay_129[function_offset:function_offset + 0x80]
    for label, target in WORLD_CONFIG_EXTERNAL_THUMB_TARGETS:
        if struct.pack('<I', target) not in function_code:
            fail(
                f'{label} Thumb target 0x{target:08X} is absent from the New Game helper; '
                'its LONG_CALL interworking may be unsafe.'
            )
    if bytes.fromhex('98 47') not in function_code:
        fail('World_SetNewGamePosition does not contain its required BLX r3 call.')

    game_clear_offset = overlay_129_file_offset(
        read_symbol('World_GameClearLocationsHook')
    )
    game_clear_code = overlay_129[game_clear_offset:game_clear_offset + 0x80]
    continuation = 0x02052D4C | 1
    if struct.pack('<I', continuation) not in game_clear_code:
        fail(
            f'World_GameClearLocationsHook does not resume at the audited '
            f'continuation 0x{continuation:08X}.'
        )

    floor_guard_offset = overlay_129_file_offset(
        read_symbol('World_DynamicWarpFloorGuardHook')
    )
    floor_guard_code = overlay_129[floor_guard_offset:floor_guard_offset + 0x80]
    for label, target in (
        ('MapNumToFloorNo', 0x021EE81C | 1),
        ('dynamic-floor continuation', 0x02043C4E | 1),
    ):
        if struct.pack('<I', target) not in floor_guard_code:
            fail(f'{label} target 0x{target:08X} is absent from the floor guard.')

    event_guard_offset = overlay_129_file_offset(
        read_symbol('World_DynamicEventWarpGuardHook')
    )
    event_guard_code = overlay_129[event_guard_offset:event_guard_offset + 0x80]
    event_continuation = 0x021E7BE0 | 1
    if struct.pack('<I', event_continuation) not in event_guard_code:
        fail(
            f'World_DynamicEventWarpGuardHook does not resume at '
            f'0x{event_continuation:08X}.'
        )

    for symbol, targets in (
        ('World_ContinueDynamicWarpGuardHook', (0x020534E8 | 1, 0x02053502 | 1)),
        ('World_DirectDynamicWarpGuardHook', (0x020541A8 | 1,)),
        ('World_PokedexGeographyFallbackHook', (0x0203C9E4 | 1,)),
        ('World_PokegearGeographyFallbackHook', (0x02092C6C | 1,)),
        ('World_LoadMainMatrixForPokegearHook', (0x0203AFB4 | 1, 0x02092C84 | 1)),
    ):
        function_offset = overlay_129_file_offset(read_symbol(symbol))
        function_code = overlay_129[function_offset:function_offset + 0x80]
        for target in targets:
            if struct.pack('<I', target) not in function_code:
                fail(f'{symbol} does not contain continuation 0x{target:08X}.')

    total = len(WORLD_CONFIG_HOOKS) + len(WORLD_LOCATION_OVERLAY_1_HOOKS)
    print(f'All {total} WorldConfig/Location hooks verified.')


def verify_archives():
    for source_name, archive_name in ARCHIVES:
        source = ROOT / source_name
        archive = ROOT / archive_name
        expected = [entry.read_bytes() for entry in sorted(source.iterdir())]
        actual = ndspy.narc.NARC.fromFile(archive).files
        if actual != expected:
            fail(f'{archive_name} does not match {source_name}')
        print(f'Archive verified: {archive_name} ({len(actual)} member(s))')

    source_names = (ROOT / 'world/mapname.bin').read_bytes()
    installed_names = (ROOT / 'base/root/fielddata/maptable/mapname.bin').read_bytes()
    if installed_names != source_names:
        fail('installed mapname.bin does not match the canonical stripped-world table')
    print('Internal Header-name table verified: 1 member (BOOTSTRAP).')

def verify_world_resource_loader_hooks():
    arm9 = (ROOT / 'base/arm9.bin').read_bytes()
    if arm9[0x40168:0x40170] != NATIVE_ENGINE_LOADER_PREFIX:
        fail('Nintendo standard/common-script loader was not restored exactly')
    stock_to_engine = {stock_id: engine_id for engine_id, stock_id in enumerate(ENGINE_STOCK_IDS)}
    expected_banks = tuple(stock_to_engine[stock_id] for stock_id in ENGINE_MAPPING_STOCK_BANKS)
    actual_banks = tuple(
        struct.unpack_from('<H', arm9, ENGINE_MAPPING_OFFSET + index * 6 + 2)[0]
        for index in range(30)
    )
    if actual_banks != expected_banks:
        fail(f'standard-script Engine member mapping is {actual_banks}, expected {expected_banks}')
    if arm9[0x40156:0x40158] != bytes.fromhex('06 22'):
        fail('scriptId-zero fallback does not load Engine Script 006')
    expected_prefix = bytes.fromhex('00 4B 18 47')
    for symbol, offset in WORLD_RESOURCE_LOADER_HOOKS:
        actual_prefix = arm9[offset:offset + 4]
        actual_pointer = struct.unpack_from('<I', arm9, offset + 4)[0]
        expected_pointer = read_symbol(symbol) | 1
        if actual_prefix != expected_prefix or actual_pointer != expected_pointer:
            fail(
                f'{symbol} loader hook at ARM9+0x{offset:06X} targets '
                f'0x{actual_pointer:08X}, expected 0x{expected_pointer:08X}'
            )
    print(f'All {len(WORLD_RESOURCE_LOADER_HOOKS)} World resource loader hooks verified.')


def main():
    verify_table_and_repoints()
    verify_world_header_hooks()
    verify_world_identity_hooks()
    verify_world_role_gates()
    verify_world_map_marking_hooks()
    verify_world_pokegear_patches()
    verify_world_spawn_hooks()
    verify_world_config_hooks()
    verify_world_resource_loader_hooks()
    verify_archives()
    print('World NARC post-build verification passed.')


if __name__ == '__main__':
    main()
