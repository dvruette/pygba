import numpy as np
from pygba import GameWrapper, PyGBA
from pygba.game_wrappers.pokemon_emerald import (
    get_game_state,
    read_species_info,
    read_experience_tables,
    count_flags,
    count_changed_flags,
    get_gained_exp,
)

class CustomEmeraldWrapper(GameWrapper):
    def __init__(
        self,
        badge_reward: float = 10.0,
        pokedex_reward: float = 10,
        pokenav_reward: float = 10,
        champion_reward: float = 100.0,
        visit_city_reward: float = 5.0,
        money_gained_reward: float = 0.0,
        # setting this below half of money_gained_reward leaves an exploit
        # where the agent can just buy and sell stuff at the pokemart..
        # but setting it too high will make it scared of battling
        money_lost_reward: float = 0.0,
        seen_pokemon_reward: float = 0.2,
        caught_pokemon_reward: float = 1.0,
        trainer_beat_reward: float = 1.0,
        event_reward: float = 1.0,
        exp_reward_shape: float = 0.3,
        exp_reward_scale: float = 0.75,
        exploration_reward: float = 0.01,
        exploration_dist_thresh: float = 6.0,  # GBA screen is 7x5 tiles
        max_hnsw_count: int = 100000,
    ):
        self.badge_reward = badge_reward
        self.pokedex_reward = pokedex_reward
        self.pokenav_reward = pokenav_reward
        self.champion_reward = champion_reward
        self.visit_city_reward = visit_city_reward
        self.money_gained_reward = money_gained_reward
        self.money_lost_reward = money_lost_reward
        self.seen_pokemon_reward = seen_pokemon_reward
        self.caught_pokemon_reward = caught_pokemon_reward
        self.trainer_beat_reward = trainer_beat_reward
        self.event_reward = event_reward
        self.exp_reward_shape = exp_reward_shape
        self.exp_reward_scale = exp_reward_scale

        self.exploration_reward = exploration_reward
        self.exploration_dist_thresh = exploration_dist_thresh
        self.max_hnsw_count = max_hnsw_count

        self._total_script_flags = 0
        self._prev_reward = 0.0
        self._game_state = {}
        self._prev_game_state = {}
        self._reward_info = {}
        self._location_store = {}

    def get_exploration_reward(self, state):
        return 0.0

    def reward(self, gba: PyGBA, observation):
        self._game_state.update(get_game_state(gba))
        state = self._game_state

        # Game state can get funky during loading screens, so we just wait until
        # we get a valid observation.
        if observation is not None and observation.sum() < 1:
            return 0.0

        trainer_flags = state.get("trainer_flags", None)
        num_trainer_flags = count_flags(trainer_flags)

        new_script_flags = state.get("script_flags", None)
        prev_script_flags = self._prev_game_state.get("script_flags", None)
        changed_script_flags = count_changed_flags(prev_script_flags, new_script_flags)
        self._total_script_flags += changed_script_flags

        species_info = read_species_info(gba)
        experience_tables = read_experience_tables(gba)
        all_mons = list(map(lambda x: x["box"], state.get("party", []))) + state.get("boxes", [])
        total_gained_exp = sum(get_gained_exp(mon, species_info, experience_tables) for mon in all_mons)

        # don't give any reward for visiting the first town, as the player spawns there
        visited_cities = max(0, sum(state.get("visited_cities", {}).values()) - 1)
        # player starts with $3000 cash
        earned_money = (state.get("money", 3000) - 3000)
        # in case the the game state glitches and gives the player a lot of money, we ignore values over 100k
        if earned_money > 0 and earned_money < 100_000:
            money_rew = earned_money * self.money_gained_reward
        elif earned_money < 0:
            money_rew = earned_money * self.money_lost_reward
        else:
            money_rew = 0.0

        self._reward_info = {
            "visit_city_rew": visited_cities * self.visit_city_reward,
            "seen_poke_rew": state.get("num_seen_pokemon", 0) * self.seen_pokemon_reward,
            "caught_poke_rew": state.get("num_caught_pokemon", 0) * self.caught_pokemon_reward,
            "explore_rew": self.get_exploration_reward(state),
            "money_rew": money_rew,
            "pokedex_rew": (1.0 if state.get("has_pokedex", False) else 0.0) * self.pokedex_reward,
            "pokenav_rew": (1.0 if state.get("has_pokenav", False) else 0.0) * self.pokenav_reward,
            "badge_rew": state.get("num_badges", 0) * self.badge_reward,
            "champ_rew": state.get("is_champion", 0) * self.champion_reward,
            "trainer_rew": num_trainer_flags * self.trainer_beat_reward,
            "event_rew": self._total_script_flags * self.event_reward,
            "exp_rew": self.exp_reward_scale * total_gained_exp ** self.exp_reward_shape,
        }
        reward = sum(self._reward_info.values())
        self._reward_info["total_reward"] = reward

        prev_reward = self._prev_reward
        self._prev_reward = reward
        self._prev_game_state = state.copy()
        return reward - prev_reward
    
    def reset(self, gba: PyGBA):
        self._game_state = {}
        self._location_store = {}
        self._total_script_flags = 0
        self._prev_reward = 0.0
        self._prev_reward = self.reward(gba, None)
        self._prev_game_state = {}
    
    def info(self, gba: PyGBA, observation):
        if self._game_state is None:
            self._game_state = get_game_state(gba)

        return {
            "game_state": self._game_state,
            "prev_reward": self._prev_reward,
            "rewards": self._reward_info,
        }
