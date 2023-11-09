import json
import mgba

import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from pygba import PyGBA, PyGBAEnv, PokemonEmerald

mgba.log.silence()


def load_pokemon_game(gba_file: str, autoload_save: bool = True):
    gba = PyGBA.load(gba_file, autoload_save=autoload_save)
    if autoload_save:
        # skip loading screen
        for _ in range(16):
            gba.press_a(30)
        gba.wait(60)
    else:
        # skip loading screen and character creation
        gba.wait(600)
        for _ in range(120):
            gba.press_a(30)
        gba.wait(720)
    return gba



def main():
    gba_file = "roms/pokemon_emerald.gba"
    gba = load_pokemon_game(gba_file, autoload_save=True)
    emerald_wrapper = PokemonEmerald()
    env = PyGBAEnv(gba, emerald_wrapper, frameskip=8, render_mode="human")

    state = emerald_wrapper.game_state(gba)
    del state["pokedex"]
    del state["boxes"]
    print(json.dumps(state, indent=2))

    actions = [
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("up", None),
        ("up", None),
        ("up", None),
        ("up", None),
        ("up", None),
        ("up", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
        ("right", None),
    ]

    for action in actions:
        obs, reward, done, info = env.step(env.get_action_id(*action))
        print(obs.shape, reward, done, info["game_state"]["pos"])
        env.render()


if __name__ == "__main__":
    main()
