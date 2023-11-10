import json
import multiprocessing

import mgba
import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from pygba import PyGBA, PyGBAEnv, PokemonEmerald

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
    save_file = "roms/pokemon_emerald.sav"
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


def main():
    gba_file = "roms/pokemon_emerald.gba"
    save_file = "roms/pokemon_emerald.sav"
    gba = PyGBA.load(gba_file, save_file=save_file)
    env = PyGBAEnv(gba, frameskip=8, render_mode="human")
    env.reset()
    obs, reward, done, truncated, info = env.step(env.get_action_id(None, "A"))
    print(obs.shape, reward, done, info)

    gba = load_pokemon_game(gba_file, save_file=save_file)
    emerald_wrapper = PokemonEmerald()
    env = PyGBAEnv(gba, emerald_wrapper, frameskip=8, render_mode="human")
    state = emerald_wrapper.game_state(gba)
    del state["pokedex"]
    del state["boxes"]
    print(json.dumps(state, indent=2))

    test_parallel_saving()

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
        obs, reward, done, truncated, info = env.step(env.get_action_id(*action))
        print(obs.shape, reward, done, info["game_state"]["pos"])
        env.render()


if __name__ == "__main__":
    main()
