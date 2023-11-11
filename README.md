# PyGBA

A Python wrapper around the Game Boy Advance emulator mGBA with built-in support for gymnasium environments.


## Usage

PyGBA is designed to be used by bots/AI agents. It provides an easy-to-use interface to interact with the emulator as well as a [`gymnasium`](https://github.com/Farama-Foundation/Gymnasium) environment for reinforcement learning.

While any GBA ROM can be run out-of-the box, if you want to do reward-based reinforcement learning, you might want to use a game-specific wrapper that provides a reward function. Currently, only a wrapper for [Pokemon Emerald](https://vimm.net/vault/5625) is provided, but more will be added in the future.

A gym environment can be created as follows:
```python
from pygba import PyGBA, PyGBAEnv, PokemonEmerald

rom_path = "path/to/pokemon_emerald.gba"
gba = PyGBA.load(rom_path, autoload_save=True)  # if autoload_save is True, a save file will be loaded if one exists next to the ROM

game_wrapper = PokemonEmerald()  # optionally customize the reward function by passing additional arguments
env = PyGBAEnv(gba, game_wrapper)
```


## Installation

Install PyGBA with pip using:
```bash
pip install pygba
```

You'll also need to install [mGBA](https://mgba.io/) with Python bindings. By default, mGBA is installed without Python bindings, so until the situation is improved, you'll need to build mGBA from source.


### Installing mGBA

MGBA PACKAGE IS CURRENTLY BROKEN (help wanted)

For Python >= 3.10 on Linux and macOS, you can use the pre-built wheels from here:
```bash
pip install mgba
```

For Windows and older Python versions, you'll need to build mGBA from source. See the the next section for instructions.

### Building mGBA from source

Official installation instructions can be found [here](https://github.com/mgba-emu/mgba/#compiling), but here's a quick summary.
The important detail is that Python bindings have to be enabled by passing `-DBUILD_PYTHON=ON` to CMake.

First, clone the mGBA repository:
```bash
git clone https://github.com/mgba-emu/mgba.git
cd mgba
```

- **Unix**:
    On Unix-based systems, run the following commands:
    ```bash
    mkdir build
    cd build
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DBUILD_PYTHON=ON ..
    make
    sudo make install
    ```

- **macOS**:
    On macOS, additional dependencies are required:
    ```bash
    brew install cmake ffmpeg libzip qt5 sdl2 libedit lua pkg-config
    mkdir build
    cd build
    cmake -DCMAKE_PREFIX_PATH=`brew --prefix qt5` -DBUILD_PYTHON=ON ..
    make
    sudo make install
    ```
    Note: If both `qt` and `qt5` are installed you might run into issues. If that's the case, try uninstalling `qt`.

- **Windows**:
    Please follow the official instructions [here](https://github.com/mgba-emu/mgba/#windows-developer-building).

After compiling mGBA, the Python bindings should be built at `build/python/lib.{platform}-{architecture}-cpython-{version}/mgba`.
To use it in your Python code, you'll need to add it to your `PYTHONPATH` environment variable.

You can check if the bindings were built and installed correctly by running `python -c "import mgba"` (should output nothing).
