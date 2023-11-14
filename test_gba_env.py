import json
import multiprocessing

import mgba
import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from pygba import PyGBA, PyGBAEnv, PokemonEmerald
from custom_wrapper import CustomEmeraldWrapper
from pygba.game_wrappers.pokemon_emerald import get_game_state

mgba.log.silence()


def load_pokemon_game(gba_file: str, save_file: str | None = None):
    gba = PyGBA.load(gba_file, save_file=save_file)
    if save_file is not None:
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



def _run_actions(actions, conn):
    gba_file = "roms/pokemon_emerald.gba"
    save_file = "saves/pokemon_emerald.new_game.sav"
    gba = load_pokemon_game(gba_file, save_file=save_file)
    env = PyGBAEnv(gba, frameskip=15, render_mode="human")
    for action in actions:
        obs, reward, done, truncated, info = env.step(env.get_action_id(*action))
        env.render()
        conn.send((obs, reward, done, truncated, info))


def test_parallel_saving():
    actions1 = [
        (None, "start"),
        (None, None),
        (None, None),
        (None, None),
        ("up", None),
        (None, None),
        ("up", None),
        (None, None),
        ("up", None),
        (None, "A"),
        (None, None),
        (None, "A"),
        (None, None),
        (None, "A"),
        (None, None),
        (None, "A"),
        (None, None),
        (None, "A"),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, "A"),
        (None, None),
        (None, "A"),
        ("right", None),
        ("right", None),
        ("left", None),
        ("left", None),
        (None, None),
    ]

    # actions2 = [("left" if i % 8 < 4 else "right", "B") for i in range(len(actions1))]
    actions2 = actions1.copy()

    # create pipes to communicate with the child processes  
    parent_conn1, child_conn1 = multiprocessing.Pipe()
    parent_conn2, child_conn2 = multiprocessing.Pipe()


    p1 = multiprocessing.Process(target=_run_actions, args=(actions1, child_conn1))
    p2 = multiprocessing.Process(target=_run_actions, args=(actions2, child_conn2))
    p1.start()
    p2.start()

    received1 = 0
    received2 = 0
    while True:
        if parent_conn1.poll():
            parent_conn1.recv()
            received1 += 1
        if parent_conn2.poll():
            parent_conn2.recv()
            received2 += 1
        if not p1.is_alive() and not p2.is_alive():
            break

    assert len(actions1) == received1
    assert len(actions2) == received2


def test_game_parsing_on_walking_through_door():
    gba_file = "roms/pokemon_emerald.gba"
    save_file = "saves/pokemon_emerald.pokedex.sav"
    # save_file = None
    gba = load_pokemon_game(gba_file, save_file=save_file)
    emerald_wrapper = PokemonEmerald()
    env = PyGBAEnv(gba, emerald_wrapper, frameskip=1, render_mode="human")
    actions = (
        [("up", None) if i % 2 == 0 else ("up", "A") for i in range(60)]
        + [("down", None) if i % 2 == 0 else ("down", "A") for i in range(60)]
        + [("right", None) if i % 2 == 0 else ("right", "A") for i in range(24)]
        + [("left", None) if i % 2 == 0 else ("left", "A") for i in range(24)]
    ) * 2
    # actions = [("right", None) if i % 2 == 0 else ("right", "A") for i in range(1000)]
    for action in actions:
        obs, reward, done, truncated, info = env.step(env.get_action_id(*action))
        env.render()
        if "game_state" in info:
            print(reward, info["game_state"]["location"], info["game_state"]["pos"])
        else:
            print(info)

def test_exp_and_event_reward():
    gba_file = "roms/pokemon_emerald.gba"
    gba = load_pokemon_game(gba_file, save_file="saves/pokemon_emerald.before_starter.sav")
    emerald_wrapper = CustomEmeraldWrapper()
    env = PyGBAEnv(gba, emerald_wrapper, frameskip=16, render_mode="human")

    actions = (
        [a for pair in zip([("up", "A") for _ in range(23)], [("up", None) for _ in range(23)]) for a in pair]
        + [a for pair in zip([("left", "A") for _ in range(10)], [("left", None) for _ in range(10)]) for a in pair]
        + [a for pair in zip([(None, "A") for _ in range(100)], [(None, None) for _ in range(100)]) for a in pair]
        + [a for pair in zip([("down", "A") for _ in range(20)], [("down", None) for _ in range(20)]) for a in pair]
        + [(None, "start"), (None, None), (None, None), (None, "A"), (None, None), (None, None), (None, None)]
    )

    for i, action in enumerate(actions):
        obs, reward, done, truncated, info = env.step(env.get_action_id(*action))
        # print(obs.shape, reward, done, info["game_state"]["location"])
        if (i + 1) % 12 == 0:
            print(json.dumps(info["rewards"], indent=2))
            env.render()
    print(json.dumps(info["rewards"], indent=2))
    env.render()
    print(info["game_state"]["party"])
    get_game_state(gba)

def main():
    # test_parallel_saving()

    # test_game_parsing_on_walking_through_door()

    test_exp_and_event_reward()

    gba_file = "roms/pokemon_emerald.gba"
    save_file = "saves/pokemon_emerald.pokedex.sav"
    # save_file = None
    gba = PyGBA.load(gba_file, save_file=save_file)
    env = PyGBAEnv(gba, frameskip=8, render_mode="human")
    env.reset()
    obs, reward, done, truncated, info = env.step(env.get_action_id(None, "A"))
    print(obs.shape, reward, done, truncated, info)

    gba = load_pokemon_game(gba_file, save_file=save_file)
    emerald_wrapper = PokemonEmerald()
    env = PyGBAEnv(gba, emerald_wrapper, frameskip=8, render_mode="human")
    state = emerald_wrapper.game_state(gba)
    del state["pokedex"]
    del state["boxes"]
    del state["script_flags"]
    del state["trainer_flags"]
    del state["system_flags"]
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
