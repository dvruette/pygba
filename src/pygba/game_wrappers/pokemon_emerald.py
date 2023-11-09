from .base import GameWrapper
from .utils.emerald_utils import *


def get_flag(flags, flag_id):
    if flag_id // 8 >= len(flags) or flag_id < 0:
        return False
    return bool((flags[flag_id // 8] >> (flag_id % 8)) & 1)

def get_game_state(gba):
    save_block_1 = read_save_block_1(gba)
    save_block_2 = read_save_block_2(gba)
    pokemon_storage = read_pokemon_storage(gba)
    species_names = read_species_names(gba)

    state = {}
    if save_block_1 is not None:
        flags = save_block_1["flags"]

        if save_block_2 is not None:
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

    if pokemon_storage is not None:
        stored_mons = [
            boxed_mon
            for box in pokemon_storage["boxes"]
            for boxed_mon in box
            if boxed_mon is not None and boxed_mon["substructs"][0]["species"] != 0
        ]
        state["boxes"] = stored_mons

    if save_block_2 is not None and species_names is not None:
        pokedex = {}
        num_seen = 0
        num_owned = 0
        for i in range(1, NUM_SPECIES):
            name = species_names[i].lower()
            dex_number = gba.read_u16(ADRESSES["sSpeciesToNationalPokedexNum"] + (i - 1) * 2)
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
        self._game_state = {}

    def game_state(self, gba):
        return get_game_state(gba)

    def reward(self, gba, observation):
        if self._game_state is None:
            self._game_state = get_game_state(gba)
        else:
            self._game_state.update(get_game_state(gba))
        state = self._game_state

        reward = (
            state.get("num_badges", 0) * self.badge_reward
            + state.get("is_champion", 0) * self.champion_reward
            + sum(state.get("visited_cities", {}).values()) * self.visit_city_reward
            + state.get("money", 0) * self.money_reward
            + state.get("num_seen_pokemon", 0) * self.seen_pokemon_reward
            + state.get("num_caught_pokemon", 0) * self.caught_pokemon_reward
        )

        prev_reward = self._prev_reward
        self._prev_reward = reward
        self._prev_game_state = state.copy()
        return reward - prev_reward
    
    def game_over(self, gba, observation):
        return False
    
    def reset(self, gba):
        self._prev_reward = self.reward(gba, None)
        self._game_state = None
    
    def info(self, gba, observation):
        if self._game_state is None:
            self._game_state = self.game_state(gba)

        return {
            "game_state": self._game_state,
            "prev_reward": self._prev_reward,
        }
