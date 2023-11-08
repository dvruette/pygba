from .gym_env import PyGBAEnv
from .pygba import PyGBA
from .game_wrappers import GameWrapper, PokemonEmerald

from gymnasium.envs.registration import register

__all__ = [
    "PyGBAEnv",
    "PyGBA",
    "GameWrapper",
    "PokemonEmerald",
]

register(id="PyGBA-v0", entry_point="gym_env:PyGBAEnv")
