from collections import namedtuple
import struct
from game_wrappers.base import GameWrapper
from utils import EmeraldCharmap


# Pokemon Emerald Sym Addresses
# https://raw.githubusercontent.com/pret/pokeemerald/symbols/pokeemerald.sym

_addresses = {
    "gPlayerPartyCount":            0x020244e9,
    "gPlayerParty":                 0x020244ec,
    "gSaveBlock1Ptr":               0x03005d8c,
    "gSaveBlock2Ptr":               0x03005d90,
    "gPokemonStoragePtr":           0x03005d94,
    "gSpeciesNames":                0x083185c8,
    "sSpeciesToHoennPokedexNum":    0x0831d94c,
    "sSpeciesToNationalPokedexNum": 0x0831dc82,
    "sHoennToNationalOrder":        0x0831dfb8,
    "gItems":                       0x085839a0,
}

_charmap = EmeraldCharmap()


# struct layouts and constants taken from pret/pokeemerald:
# https://github.com/pret/pokeemerald/blob/master/include/pokemon.h
# https://github.com/pret/pokeemerald/blob/master/include/global.h


## Constants

POKEMON_NAME_LENGTH = 10
PLAYER_NAME_LENGTH = 7
PC_ITEMS_COUNT = 50
BAG_ITEMS_COUNT = 30
BAG_KEYITEMS_COUNT = 30
BAG_POKEBALLS_COUNT = 16
BAG_TMHM_COUNT = 64
BAG_BERRIES_COUNT = 46

NUM_SPECIES = 412
NUM_DEX_FLAG_BYTES = (NUM_SPECIES + 7) // 8

TOTAL_BOXES_COUNT = 14
IN_BOX_COUNT = 30
BOX_NAME_LENGTH = 8


## Flag IDs

FLAG_DEFEATED_RUSTBORO_GYM =        0x4F0
FLAG_DEFEATED_DEWFORD_GYM =         0x4F1
FLAG_DEFEATED_MAUVILLE_GYM =        0x4F2
FLAG_DEFEATED_LAVARIDGE_GYM =       0x4F3
FLAG_DEFEATED_PETALBURG_GYM =       0x4F4
FLAG_DEFEATED_FORTREE_GYM =         0x4F5
FLAG_DEFEATED_MOSSDEEP_GYM =        0x4F6
FLAG_DEFEATED_SOOTOPOLIS_GYM =      0x4F7
FLAG_DEFEATED_METEOR_FALLS_STEVEN = 0x4F8

FLAG_DEFEATED_ELITE_4_SIDNEY =      0x4FB
FLAG_DEFEATED_ELITE_4_PHOEBE =      0x4FC
FLAG_DEFEATED_ELITE_4_GLACIA =      0x4FD
FLAG_DEFEATED_ELITE_4_DRAKE =       0x4FE

SYSTEM_FLAGS =                      0x860
FLAG_SYS_POKEMON_GET =              SYSTEM_FLAGS + 0x0
FLAG_SYS_POKEDEX_GET =              SYSTEM_FLAGS + 0x1
FLAG_SYS_POKENAV_GET =              SYSTEM_FLAGS + 0x2
FLAG_RECEIVED_POKEDEX_FROM_BIRCH =  SYSTEM_FLAGS + 0x84

FLAG_BADGE01_GET =                  SYSTEM_FLAGS + 0x7
FLAG_BADGE02_GET =                  SYSTEM_FLAGS + 0x8
FLAG_BADGE03_GET =                  SYSTEM_FLAGS + 0x9
FLAG_BADGE04_GET =                  SYSTEM_FLAGS + 0xa
FLAG_BADGE05_GET =                  SYSTEM_FLAGS + 0xb
FLAG_BADGE06_GET =                  SYSTEM_FLAGS + 0xc
FLAG_BADGE07_GET =                  SYSTEM_FLAGS + 0xd
FLAG_BADGE08_GET =                  SYSTEM_FLAGS + 0xe

FLAG_VISITED_LITTLEROOT_TOWN =      SYSTEM_FLAGS + 0xF
FLAG_VISITED_OLDALE_TOWN =          SYSTEM_FLAGS + 0x10
FLAG_VISITED_DEWFORD_TOWN =         SYSTEM_FLAGS + 0x11
FLAG_VISITED_LAVARIDGE_TOWN =       SYSTEM_FLAGS + 0x12
FLAG_VISITED_FALLARBOR_TOWN =       SYSTEM_FLAGS + 0x13
FLAG_VISITED_VERDANTURF_TOWN =      SYSTEM_FLAGS + 0x14
FLAG_VISITED_PACIFIDLOG_TOWN =      SYSTEM_FLAGS + 0x15
FLAG_VISITED_PETALBURG_CITY =       SYSTEM_FLAGS + 0x16
FLAG_VISITED_SLATEPORT_CITY =       SYSTEM_FLAGS + 0x17
FLAG_VISITED_MAUVILLE_CITY =        SYSTEM_FLAGS + 0x18
FLAG_VISITED_RUSTBORO_CITY =        SYSTEM_FLAGS + 0x19
FLAG_VISITED_FORTREE_CITY =         SYSTEM_FLAGS + 0x1A
FLAG_VISITED_LILYCOVE_CITY =        SYSTEM_FLAGS + 0x1B
FLAG_VISITED_MOSSDEEP_CITY =        SYSTEM_FLAGS + 0x1C
FLAG_VISITED_SOOTOPOLIS_CITY =      SYSTEM_FLAGS + 0x1D
FLAG_VISITED_EVER_GRANDE_CITY =     SYSTEM_FLAGS + 0x1E

FLAG_IS_CHAMPION =                  SYSTEM_FLAGS + 0x1F


PokemonSubstruct0_spec = (
    ("species", "H"),
    ("heldItem", "H"),
    ("experience", "I"),
    ("ppBonuses", "B"),
    ("friendship", "B"),
    ("unknown", "H"),
)
PokemonSubstruct0 = namedtuple("PokemonSubstruct0", [x[0] for x in PokemonSubstruct0_spec])
PokemonSubstruct0_format = "".join([x[1] for x in PokemonSubstruct0_spec])

PokemonSubstruct1_spec = None
PokemonSubstruct1 = namedtuple("PokemonSubstruct1", ("moves", "pp"))
PokemonSubstruct1_format = "4H4B"

PokemonSubstruct2_spec = (
    ("hpEV", "B"),
    ("attackEV", "B"),
    ("defenseEV", "B"),
    ("speedEV", "B"),
    ("spAttackEV", "B"),
    ("spDefenseEV", "B"),
    ("cool", "B"),
    ("beauty", "B"),
    ("cute", "B"),
    ("smart", "B"),
    ("tough", "B"),
    ("sheen", "B"),
)
PokemonSubstruct2 = namedtuple("PokemonSubstruct2", [x[0] for x in PokemonSubstruct2_spec])
PokemonSubstruct2_format = "".join([x[1] for x in PokemonSubstruct2_spec])

PokemonSubstruct3_spec = None
PokemonSubstruct3_format = "III"
PokemonSubstruct3 = namedtuple("PokemonSubstruct3", (
    "pokerus",
    "metLocation",
    "metLevel",
    "metGame",
    "pokeball",
    "otGender",
    "hpIV",
    "attackIV",
    "defenseIV",
    "speedIV",
    "spAttackIV",
    "spDefenseIV",
    "isEgg",
    "abilityNum",
    "ribbons",
))


BoxPokemon_spec = (
    ("personality", "I"),
    ("otId", "I"),
    ("nickname", f"{POKEMON_NAME_LENGTH}s"),
    ("language", "B"),
    ("flags", "B"),
    ("otName", f"{PLAYER_NAME_LENGTH}s"),
    ("markings", "B"),
    ("checksum", "H"),
    ("unknown", "H"),
    ("substructs", f"{48}s"),
)
BoxPokemon = namedtuple("BoxPokemon", [x[0] for x in BoxPokemon_spec])
BoxPokemon_format = "".join([x[1] for x in BoxPokemon_spec])


Pokemon_spec = (
    ("box", f"{struct.calcsize(BoxPokemon_format)}s"),
    ("status", "I"),
    ("level", "B"),
    ("mail", "B"),
    ("hp", "H"),
    ("maxHp", "H"),
    ("attack", "H"),
    ("defense", "H"),
    ("speed", "H"),
    ("spAttack", "H"),
    ("spDefense", "H"),
)
Pokemon = namedtuple("Pokemon", [x[0] for x in Pokemon_spec])
Pokemon_format = "".join([x[1] for x in Pokemon_spec])


Pokedex_spec = (
    ("order", "B"),
    ("mode", "B"),
    ("nationalMagic", "B"),
    ("padding1", "B"),
    ("unownPersonality", "I"),
    ("spindaPersonality", "I"),
    ("padding2", "4s"),
    ("owned", f"{NUM_DEX_FLAG_BYTES}s"),
    ("seen", f"{NUM_DEX_FLAG_BYTES}s"),
)
Pokedex = namedtuple("Pokedex", [x[0] for x in Pokedex_spec])
Pokedex_format = "".join([x[1] for x in Pokedex_spec])


Coords16_spec = (
    ("x", "H"),
    ("y", "H"),
)
Coords16 = namedtuple("Coords16", [x[0] for x in Coords16_spec])
Coords16_format = "".join([x[1] for x in Coords16_spec])

WarpData_spec = (
    ("mapGroup", "b"),
    ("mapNum", "b"),
    ("warpId", "bx"),
    ("x", "H"),
    ("y", "H"),
)
WarpData = namedtuple("WarpData", [x[0] for x in WarpData_spec])
WarpData_format = "".join([x[1] for x in WarpData_spec])

ItemSlot_spec = (
    ("itemId", "H"),
    ("quantity", "H"),
)
ItemSlot = namedtuple("ItemSlot", [x[0] for x in ItemSlot_spec])
ItemSlot_format = "".join([x[1] for x in ItemSlot_spec])

SaveBlock2_spec = (
    ("playerName", f"{PLAYER_NAME_LENGTH + 1}s"),
    ("playerGender", "B"),
    ("specialSaveWarpFlags", "B"),
    ("playerTrainerId", "4s"),
    ("playTimeHours", "H"),
    ("playTimeMinutes", "B"),
    ("playTimeSeconds", "B"),
    ("playTimeVBlanks", "B"),
    ("optionsButtonMode", "B"),
    ("options", "H"),
    ("padding1", "2s"),
    ("pokedex", f"{struct.calcsize(Pokedex_format)}s"),
    ("filler_90", "8s"),
    ("localTimeOffset", "8s"),
    ("lastBerryTreeUpdate", "8s"),
    ("gcnLinkFlags", "I"),
    ("encryptionKey", "I"),
    ("rest", f"{0xe7c}s"),
)
SaveBlock2 = namedtuple("SaveBlock2", [x[0] for x in SaveBlock2_spec])
SaveBlock2_format = "".join([x[1] for x in SaveBlock2_spec])

SaveBlock1_spec = (
    ("pos", f"{struct.calcsize(Coords16_format)}s"),
    ("location", f"{struct.calcsize(WarpData_format)}s"),
    ("continueGameWarp", f"{struct.calcsize(WarpData_format)}s"),
    ("dynamicWarp", f"{struct.calcsize(WarpData_format)}s"),
    ("lastHealLocation", f"{struct.calcsize(WarpData_format)}s"),
    ("escapeWarp", f"{struct.calcsize(WarpData_format)}s"),
    ("savedMusic", "H"),
    ("weather", "B"),
    ("weatherCycleStage", "B"),
    ("flashLevel", "B"),
    ("padding1", "B"),
    ("mapLayoutId", "H"),
    ("mapView", f"{0x200}s"),
    ("playerPartyCount", "B"),
    ("padding2", "3s"),
    ("playerParty", f"{600}s"),
    ("money", "I"),
    ("coins", "H"),
    ("registeredItem", "H"),
    ("pcItems", f"{struct.calcsize(ItemSlot_format) * PC_ITEMS_COUNT}s"),
    ("bagPocket_Items", f"{struct.calcsize(ItemSlot_format) * BAG_ITEMS_COUNT}s"),
    ("bagPocket_KeyItems", f"{struct.calcsize(ItemSlot_format) * BAG_KEYITEMS_COUNT}s"),
    ("bagPocket_PokeBalls", f"{struct.calcsize(ItemSlot_format) * BAG_POKEBALLS_COUNT}s"),
    ("bagPocket_TMHM", f"{struct.calcsize(ItemSlot_format) * BAG_TMHM_COUNT}s"),
    ("bagPocket_Berries", f"{struct.calcsize(ItemSlot_format) * BAG_BERRIES_COUNT}s"),
    ("pokeblocks", f"{320}s"),
    ("seen1", f"{NUM_DEX_FLAG_BYTES}s"),
    ("berryBlenderRecords", "6s"),
    ("unused", "6s"),
    ("trainerRematchStepCounter", "H"),
    ("trainedRematches", "100s"),
    ("padding3", "2s"),
    ("objectEvents", f"{576}s"),
    ("objectEventTemplates", f"{1536}s"),
    ("flags", f"{300}s"),
    ("rest", f"{0x29ec}s"),
)
SaveBlock1 = namedtuple("SaveBlock1", [x[0] for x in SaveBlock1_spec])
SaveBlock1_format = "".join([x[1] for x in SaveBlock1_spec])


PokemonStorage_spec = (
    ("currentBox", "B"),
    ("boxes", f"{struct.calcsize(BoxPokemon_format) * TOTAL_BOXES_COUNT * IN_BOX_COUNT}s"),
    ("boxNames", f"{TOTAL_BOXES_COUNT * (BOX_NAME_LENGTH + 1)}s"),
    ("boxWallpapers", f"{TOTAL_BOXES_COUNT}s"),
)
PokemonStorage = namedtuple("PokemonStorage", [x[0] for x in PokemonStorage_spec])
PokemonStorage_format = "".join([x[1] for x in PokemonStorage_spec])


def parse_box_pokemon(data):
    box = BoxPokemon._make(struct.unpack("<" + BoxPokemon_format, data))
    box = box._replace(nickname=_charmap.decode(box.nickname))
    box = box._replace(otName=_charmap.decode(box.otName))
    
    key = box.otId ^ box.personality
    substructs_raw = struct.unpack("<" + "I" * 12, box.substructs)
    substructs = [x ^ key for x in substructs_raw]

    substructSelector = [
		[0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 3, 1, 2],
		[0, 2, 3, 1], [0, 3, 2, 1], [1, 0, 2, 3], [1, 0, 3, 2],
		[2, 0, 1, 3], [3, 0, 1, 2], [2, 0, 3, 1], [3, 0, 2, 1],
		[1, 2, 0, 3], [1, 3, 0, 2], [2, 1, 0, 3], [3, 1, 0, 2],
		[2, 3, 0, 1], [3, 2, 0, 1], [1, 2, 3, 0], [1, 3, 2, 0],
		[2, 1, 3, 0], [3, 1, 2, 0], [2, 3, 1, 0], [3, 2, 1, 0],
    ]
    # get substruct permutation by personality mod 24
    perm = substructSelector[box.personality % 24]
    substruct0 = substructs[3 * perm[0] : 3 * (perm[0] + 1)]
    substruct1 = substructs[3 * perm[1] : 3 * (perm[1] + 1)]
    substruct2 = substructs[3 * perm[2] : 3 * (perm[2] + 1)]
    substruct3 = substructs[3 * perm[3] : 3 * (perm[3] + 1)]

    substruct0 = PokemonSubstruct0._make(struct.unpack("<" + PokemonSubstruct0_format, struct.pack("<" + "I" * 3, *substruct0)))
    substruct2 = PokemonSubstruct2._make(struct.unpack("<" + PokemonSubstruct2_format, struct.pack("<" + "I" * 3, *substruct2)))

    x1, x2, x3 = substruct1
    substruct1 = PokemonSubstruct1(
        [
            (x1 >> 0)  & 0xFFFF,
            (x1 >> 16) & 0xFFFF,
            (x2 >> 32) & 0xFFFF,
            (x2 >> 48) & 0xFFFF,
        ],
        [
            (x3 >> 0)  & 0xFF,
            (x3 >> 8)  & 0xFF,
            (x3 >> 16) & 0xFF,
            (x3 >> 24) & 0xFF,
        ]
    )
    
    x1, x2, x3 = substruct3
    substruct3 = PokemonSubstruct3(
        (x1 >> 0)  & 0xFF,
        (x1 >> 8)  & 0xFFFF,
        (x1 >> 16) & 0b01111111,
        (x1 >> 23) & 0xF,
        (x1 >> 27) & 0xF,
        (x1 >> 31) & 0b1,
        (x2 >> 0)  & 0b00011111,
        (x2 >> 5)  & 0b00011111,
        (x2 >> 10) & 0b00011111,
        (x2 >> 15) & 0b00011111,
        (x2 >> 20) & 0b00011111,
        (x2 >> 25) & 0b00011111,
        (x2 >> 30) & 0b1,
        (x2 >> 31) & 0b1,
        x3,
    )

    box = box._replace(substructs=(
        substruct0._asdict(),
        substruct1._asdict(),
        substruct2._asdict(),
        substruct3._asdict(),
    ))

    box = box._asdict()
    del box["unknown"]
    del box["substructs"][0]["unknown"]
    return box

def parse_pokemon(data):
    pokemon = Pokemon._make(struct.unpack("<" + Pokemon_format, data))
    box = parse_box_pokemon(pokemon.box)
    pokemon = pokemon._replace(box=box)
    return pokemon._asdict()


def read_save_block_2(gba):
    save_block_2_ptr = gba.read_u32(_addresses["gSaveBlock2Ptr"])
    save_block_2_data = gba.read_memory(save_block_2_ptr, struct.calcsize(SaveBlock2_format))
    save_block_2 = SaveBlock2._make(struct.unpack("<" + SaveBlock2_format, save_block_2_data))
    save_block_2 = save_block_2._replace(playerName=_charmap.decode(save_block_2.playerName))
    save_block_2 = save_block_2._replace(pokedex=Pokedex._make(struct.unpack("<" + Pokedex_format, save_block_2.pokedex))._asdict())
    return save_block_2._asdict()

def read_save_block_1(gba):
    save_block_1_ptr = gba.read_u32(_addresses["gSaveBlock1Ptr"])
    save_block_1_data = gba.read_memory(save_block_1_ptr, struct.calcsize(SaveBlock1_format))
    save_block_1 = SaveBlock1._make(struct.unpack("<" + SaveBlock1_format, save_block_1_data))
    
    # parse nested structs
    save_block_1 = save_block_1._replace(pos=Coords16._make(struct.unpack("<" + Coords16_format, save_block_1.pos))._asdict())
    save_block_1 = save_block_1._replace(location=WarpData._make(struct.unpack("<" + WarpData_format, save_block_1.location))._asdict())
    save_block_1 = save_block_1._replace(continueGameWarp=WarpData._make(struct.unpack("<" + WarpData_format, save_block_1.continueGameWarp))._asdict())
    save_block_1 = save_block_1._replace(dynamicWarp=WarpData._make(struct.unpack("<" + WarpData_format, save_block_1.dynamicWarp))._asdict())
    save_block_1 = save_block_1._replace(lastHealLocation=WarpData._make(struct.unpack("<" + WarpData_format, save_block_1.lastHealLocation))._asdict())
    save_block_1 = save_block_1._replace(escapeWarp=WarpData._make(struct.unpack("<" + WarpData_format, save_block_1.escapeWarp))._asdict())

    player_party_count = save_block_1.playerPartyCount
    save_block_1 = save_block_1._replace(playerParty=[
        parse_pokemon(save_block_1.playerParty[i:i+struct.calcsize(Pokemon_format)])
        for i in range(0, player_party_count * struct.calcsize(Pokemon_format), struct.calcsize(Pokemon_format))
    ])

    save_block_1 = save_block_1._replace(pcItems=[
        ItemSlot._make(struct.unpack("<" + ItemSlot_format, save_block_1.pcItems[i:i+struct.calcsize(ItemSlot_format)]))._asdict()
        for i in range(0, len(save_block_1.pcItems), struct.calcsize(ItemSlot_format))
    ])
    save_block_1 = save_block_1._replace(bagPocket_Items=[
        ItemSlot._make(struct.unpack("<" + ItemSlot_format, save_block_1.bagPocket_Items[i:i+struct.calcsize(ItemSlot_format)]))._asdict()
        for i in range(0, len(save_block_1.bagPocket_Items), struct.calcsize(ItemSlot_format))
    ])
    save_block_1 = save_block_1._replace(bagPocket_KeyItems=[
        ItemSlot._make(struct.unpack("<" + ItemSlot_format, save_block_1.bagPocket_KeyItems[i:i+struct.calcsize(ItemSlot_format)]))._asdict()
        for i in range(0, len(save_block_1.bagPocket_KeyItems), struct.calcsize(ItemSlot_format))
    ])
    save_block_1 = save_block_1._replace(bagPocket_PokeBalls=[
        ItemSlot._make(struct.unpack("<" + ItemSlot_format, save_block_1.bagPocket_PokeBalls[i:i+struct.calcsize(ItemSlot_format)]))._asdict()
        for i in range(0, len(save_block_1.bagPocket_PokeBalls), struct.calcsize(ItemSlot_format))
    ])
    save_block_1 = save_block_1._replace(bagPocket_TMHM=[
        ItemSlot._make(struct.unpack("<" + ItemSlot_format, save_block_1.bagPocket_TMHM[i:i+struct.calcsize(ItemSlot_format)]))._asdict()
        for i in range(0, len(save_block_1.bagPocket_TMHM), struct.calcsize(ItemSlot_format))
    ])
    save_block_1 = save_block_1._replace(bagPocket_Berries=[
        ItemSlot._make(struct.unpack("<" + ItemSlot_format, save_block_1.bagPocket_Berries[i:i+struct.calcsize(ItemSlot_format)]))._asdict()
        for i in range(0, len(save_block_1.bagPocket_Berries), struct.calcsize(ItemSlot_format))
    ])

    return save_block_1._asdict()


def read_pokemon_storage(gba):
    pokemon_storage_ptr = gba.read_u32(_addresses["gPokemonStoragePtr"])
    pokemon_storage_data = gba.read_memory(pokemon_storage_ptr, struct.calcsize(PokemonStorage_format))
    pokemon_storage = PokemonStorage._make(struct.unpack("<" + PokemonStorage_format, pokemon_storage_data))
    
    box_mon_size = struct.calcsize(BoxPokemon_format)
    box_size = box_mon_size * IN_BOX_COUNT
    pokemon_storage = pokemon_storage._replace(boxes=[
        [
            parse_box_pokemon(pokemon_storage.boxes[i:i+box_mon_size])
            for i in range(j * box_size, (j + 1) * box_size, box_mon_size)
        ]
        for j in range(TOTAL_BOXES_COUNT)
    ])
    pokemon_storage = pokemon_storage._replace(boxNames=[
        _charmap.decode(pokemon_storage.boxNames[i:i+BOX_NAME_LENGTH])
        for i in range(0, len(pokemon_storage.boxNames), BOX_NAME_LENGTH + 1)
    ])
    return pokemon_storage._asdict()


def read_species_names(gba):
    species_names_ptr = _addresses["gSpeciesNames"]
    species_names_data = gba.read_memory(species_names_ptr, NUM_SPECIES * (POKEMON_NAME_LENGTH +1))
    species_names = [
        _charmap.decode(species_names_data[i:i+POKEMON_NAME_LENGTH+1])
        for i in range(0, len(species_names_data), POKEMON_NAME_LENGTH+1)
    ]
    return species_names


def get_flag(flags, flag_id):
    if flag_id // 8 >= len(flags) or flag_id < 0:
        return False
    return bool((flags[flag_id // 8] >> (flag_id % 8)) & 1)

def get_game_state(gba):
    save_block_1 = read_save_block_1(gba)
    save_block_2 = read_save_block_2(gba)
    pokemon_storage = read_pokemon_storage(gba)
    flags = save_block_1["flags"]
    species_names = read_species_names(gba)

    state = {}
    state["money"] = save_block_1["money"] ^ save_block_2["encryptionKey"]
    state["pos"] = save_block_1["pos"]
    state["location"] = save_block_1["location"]
    state["lastHealLocation"] = save_block_1["lastHealLocation"]
    state["wheather"] = save_block_1["weather"]
    state["badges"] = [
        get_flag(flags, FLAG_BADGE01_GET),
        get_flag(flags, FLAG_BADGE02_GET),
        get_flag(flags, FLAG_BADGE03_GET),
        get_flag(flags, FLAG_BADGE04_GET),
        get_flag(flags, FLAG_BADGE05_GET),
        get_flag(flags, FLAG_BADGE06_GET),
        get_flag(flags, FLAG_BADGE07_GET),
        get_flag(flags, FLAG_BADGE08_GET),
    ]
    state["num_badges"] = sum(state["badges"])
    state["has_pokedex"] = get_flag(flags, FLAG_SYS_POKEDEX_GET)
    state["has_pokenav"] = get_flag(flags, FLAG_SYS_POKENAV_GET)
    state["is_champion"] = get_flag(flags, FLAG_IS_CHAMPION)

    state["visited_cities"] = {
        "littleroot": get_flag(flags, FLAG_VISITED_LITTLEROOT_TOWN),
        "oldale": get_flag(flags, FLAG_VISITED_OLDALE_TOWN),
        "dewford": get_flag(flags, FLAG_VISITED_DEWFORD_TOWN),
        "lavaridge": get_flag(flags, FLAG_VISITED_LAVARIDGE_TOWN),
        "fallarbor": get_flag(flags, FLAG_VISITED_FALLARBOR_TOWN),
        "verdanturf": get_flag(flags, FLAG_VISITED_VERDANTURF_TOWN),
        "pacifidlog": get_flag(flags, FLAG_VISITED_PACIFIDLOG_TOWN),
        "petalburg": get_flag(flags, FLAG_VISITED_PETALBURG_CITY),
        "slateport": get_flag(flags, FLAG_VISITED_SLATEPORT_CITY),
        "mauville": get_flag(flags, FLAG_VISITED_MAUVILLE_CITY),
        "rustboro": get_flag(flags, FLAG_VISITED_RUSTBORO_CITY),
        "fortree": get_flag(flags, FLAG_VISITED_FORTREE_CITY),
        "lilycove": get_flag(flags, FLAG_VISITED_LILYCOVE_CITY),
        "mossdeep": get_flag(flags, FLAG_VISITED_MOSSDEEP_CITY),
        "sootopolis": get_flag(flags, FLAG_VISITED_SOOTOPOLIS_CITY),
        "evergrande": get_flag(flags, FLAG_VISITED_EVER_GRANDE_CITY),
    }

    state["defeated_gyms"] = {
        "rustboro": get_flag(flags, FLAG_DEFEATED_RUSTBORO_GYM),
        "dewford": get_flag(flags, FLAG_DEFEATED_DEWFORD_GYM),
        "mauville": get_flag(flags, FLAG_DEFEATED_MAUVILLE_GYM),
        "lavaridge": get_flag(flags, FLAG_DEFEATED_LAVARIDGE_GYM),
        "petalburg": get_flag(flags, FLAG_DEFEATED_PETALBURG_GYM),
        "fortree": get_flag(flags, FLAG_DEFEATED_FORTREE_GYM),
        "mossdeep": get_flag(flags, FLAG_DEFEATED_MOSSDEEP_GYM),
        "sootopolis": get_flag(flags, FLAG_DEFEATED_SOOTOPOLIS_GYM),
    }

    state["defeated_elite_4"] = [
        get_flag(flags, FLAG_DEFEATED_ELITE_4_SIDNEY),
        get_flag(flags, FLAG_DEFEATED_ELITE_4_PHOEBE),
        get_flag(flags, FLAG_DEFEATED_ELITE_4_GLACIA),
        get_flag(flags, FLAG_DEFEATED_ELITE_4_DRAKE),
    ]

    state["party"] = save_block_1["playerParty"]
    stored_mons = [
        boxed_mon
        for box in pokemon_storage["boxes"]
        for boxed_mon in box
        if boxed_mon["substructs"][0]["species"] != 0
    ]
    state["boxes"] = stored_mons

    pokedex = {}
    num_seen = 0
    num_owned = 0
    for i in range(1, NUM_SPECIES):
        name = species_names[i].lower()
        dex_number = gba.read_u16(_addresses["sSpeciesToNationalPokedexNum"] + (i - 1) * 2)
        dex_number -= 1
        index = dex_number // 8
        mask = 1 << dex_number % 8
        seen = save_block_2["pokedex"]["seen"][index] & mask > 0
        owned = save_block_2["pokedex"]["owned"][index] & mask > 0
        num_seen += 1 if seen else 0
        num_owned += 1 if owned else 0
        pokedex[name] = {"seen": seen, "caught": owned}

    state["num_seen_pokemon"] = num_seen
    state["num_caught_pokemon"] = num_owned
    state["pokedex"] = pokedex

    return state


class PokemonEmerald(GameWrapper):
    def __init__(
        self,
        badge_reward: float = 10.0,
        champion_reward: float = 100.0,
        visit_city_reward: float = 5.0,
        money_reward: float = 0.0,
        seen_pokemon_reward: float = 0.2,
        caught_pokemon_reward: float = 1.0,
    ):
        self.badge_reward = badge_reward
        self.champion_reward = champion_reward
        self.visit_city_reward = visit_city_reward
        self.money_reward = money_reward
        self.seen_pokemon_reward = seen_pokemon_reward
        self.caught_pokemon_reward = caught_pokemon_reward

        self._prev_reward = 0.0

    def reward(self, gba, observation):
        game_state = get_game_state(gba)

        reward = (
            game_state["num_badges"] * self.badge_reward
            + game_state["is_champion"] * self.champion_reward
            + sum(game_state["visited_cities"].values()) * self.visit_city_reward
            + game_state["money"] * self.money_reward
            + game_state["num_seen_pokemon"] * self.seen_pokemon_reward
            + game_state["num_caught_pokemon"] * self.caught_pokemon_reward
        )

        prev_reward = self._prev_reward
        self._prev_reward = reward
        return reward - prev_reward
    
    def game_over(self, gba, observation):
        return False
    
    def reset(self, gba):
        self._prev_reward = self.reward(gba, None)

    def game_state(self, gba):
        return get_game_state(gba)
    
    def info(self, gba, observation):
        return {
            "game_state": self.game_state(gba),
            "prev_reward": self._prev_reward,
        }
