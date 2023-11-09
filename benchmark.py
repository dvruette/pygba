import argparse
import functools
import random
import time

import mgba
import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from pygba import PyGBA, PyGBAEnv, PokemonEmerald

mgba.log.silence()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gba-file", type=str, default="roms/pokemon_emerald.gba")
    parser.add_argument("--frameskip", type=int, default=0)
    parser.add_argument("--iterations", type=int, default=1000)
    return parser.parse_args()

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

def benchmark_function(func, iterations=1000, warmup=10):
    print(f"Warming up for {warmup} iterations...")
    for _ in range(warmup):
        func()
    
    print(f"Benchmarking for {iterations} iterations...")
    start_time = time.time()
    for _ in range(iterations):
        func()
    end_time = time.time()
    
    it_per_sec = iterations / (end_time - start_time)
    return it_per_sec

def create_env(args, use_wrapper=True):
    gba = load_pokemon_game(args.gba_file, autoload_save=True)
    if use_wrapper:
        emerald_wrapper = PokemonEmerald()
        return PyGBAEnv(gba, emerald_wrapper, frameskip=args.frameskip)
    else:
        return PyGBAEnv(gba, frameskip=args.frameskip)

def random_env_step(env):
    action = random.randrange(env.action_space.n)
    env.step(action)


def main(args):
    env = create_env(args, use_wrapper=False)

    env.reset()
    steps_per_sec = benchmark_function(env.gba.core.run_frame, args.iterations)
    print(f"mGBA FPS: {steps_per_sec}")
    print("---")

    env.reset()
    steps_per_sec = benchmark_function(functools.partial(random_env_step, env), args.iterations)
    print(f"Env. it/s: {steps_per_sec}")
    print("---")

    env = create_env(args, use_wrapper=True)
    steps_per_sec = benchmark_function(functools.partial(random_env_step, env), args.iterations)
    print(f"Wrapped Env. it/s: {steps_per_sec}")
    print("---")

if __name__ == "__main__":
    args = parse_args()
    main(args)    
