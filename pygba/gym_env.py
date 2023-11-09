import sys
from typing import Any, Literal

import gymnasium as gym
import mgba.core
import mgba.image
import numpy as np

from .utils import KEY_MAP
from .pygba import PyGBA
from .game_wrappers.base import GameWrapper


try:
    import pygame
    from pygame import gfxdraw
except ImportError as e:
    pass

def _pil_image_to_pygame(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()

class PyGBAEnv(gym.Env):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 60,
    }
    
    def __init__(
        self,
        gba: PyGBA,
        game_wrapper: GameWrapper | None = None,
        obs_type: Literal["rgb", "grayscale"] = "rgb",
        frameskip: int | tuple[int, int] | tuple[int, int, int] = 0,
        repeat_action_probability: float = 0.0,
        render_mode: Literal["human", "rgb_array"] | None = None,
        reset_to_initial_state: bool = True,
        max_episode_steps: int | None = None,
        **kwargs,
    ):
        self.gba = gba
        if not isinstance(gba, PyGBA):
            raise TypeError(f"core must be a PyGBA object (got {type(gba)})")
        
        self.game_wrapper = game_wrapper
        if game_wrapper is not None and not isinstance(game_wrapper, GameWrapper):
            raise TypeError(f"game_wrapper must be a GameWrapper object (got {type(game_wrapper)})")
        if game_wrapper is None:
            gym.logger.warn(
                "You didn't pass a GameWrapper to the base GBA environment, "
                "which means that there is no reward calculation and no game over detection."
            )
        
        self.obs_type = obs_type
        self.frameskip = frameskip
        self.repeat_action_probability = repeat_action_probability
        self.render_mode = render_mode
        self.max_episode_steps = max_episode_steps

        self.arrow_keys = [None, "up", "down", "right", "left"]
        self.buttons = [None, "A", "B", "select", "start", "L", "R"]

        # cartesian product of arrows and buttons, i.e. can press 1 arrow and 1 button at the same time
        self.actions = [(a, b) for a in self.arrow_keys for b in self.buttons]
        
        self.action_space = gym.spaces.Discrete(len(self.actions))

        # Building the observation_space
        screen_size = self.gba.core.desired_video_dimensions()
        if obs_type == "rgb":
            screen_size += (3,)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=screen_size, dtype=np.uint8)

        self._framebuffer = mgba.image.Image(*self.gba.core.desired_video_dimensions())
        self.gba.core.set_video_buffer(self._framebuffer)  # need to reset after this

        self._screen = None
        self._clock = None
        self._step = 0
        if reset_to_initial_state:
            self._initial_state = self.gba.core.save_raw_state()
            pass
        else:
            self._initial_state = None
        self._kwargs = kwargs

        self.reset()

    def get_action_by_id(self, action_id: int) -> tuple[Any, Any]:
        if action_id < 0 or action_id > len(self.actions):
            raise ValueError(f"action_id {action_id} is invalid")
        return self.actions[action_id]

    def get_action_id(self, arrow: str, button: str) -> int:
        action = (arrow, button)
        if action not in self.actions:
            raise ValueError(f"Invalid action: Must be a tuple of (arrow, button)")
        return self.actions.index(action)

    def _get_observation(self):
        img = self._framebuffer.to_pil().convert("RGB")
        if self.obs_type == "grayscale":
            img = img.convert("L")
        return np.array(img).transpose(1, 0, 2)

    def step(self, action_id):
        info = {}

        actions = self.get_action_by_id(action_id)
        actions = [KEY_MAP[a] for a in actions if a is not None]
        if np.random.random() > self.repeat_action_probability:
            self.gba.core.set_keys(*actions)

        if isinstance(self.frameskip, tuple):
            frameskip = np.random.randint(*self.frameskip)
        else:
            frameskip = self.frameskip

        for _ in range(frameskip + 1):
            self.gba.core.run_frame()
        observation = self._get_observation()

        reward = 0
        done = False
        truncated = False
        if self.max_episode_steps is not None:
            truncated = self._step >= self.max_episode_steps
        if self.game_wrapper is not None:
            reward = self.game_wrapper.reward(self.gba, observation)
            done = done or self.game_wrapper.game_over(self.gba, observation)
            info.update(self.game_wrapper.info(self.gba, observation))

        self._step += 1
        # print(f"\r step={self._step} | {reward=} | {done=} | {truncated=}", end="", flush=True)

        return observation, reward, done, truncated, info
    
    def check_if_done(self):
        observation = self._get_observation()
        done = self.game_wrapper.game_over(self.gba, observation)

        return done

    def reset(self, seed=None):
        info = {}
        self._step = 0
        self.gba.core.reset()
        if self._initial_state is not None:
            self.gba.core.load_raw_state(self._initial_state)

            # not sure what the best solution is here:
            # 1. don't run_frame after resetting the state, will lead to the old frame still being rendered
            # 2. run_frame after resetting the state, offsetting the savestate by one frame
            self.gba.core.run_frame()
        
        observation = self._get_observation()
        
        if self.game_wrapper is not None:
            self.game_wrapper.reset(self.gba)
            info.update(self.game_wrapper.info(self.gba, observation))
        return observation, info

    def render(self):
        if self.render_mode is None:
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You can specify the render_mode at initialization."
            )
            return
        
        img = self._framebuffer.to_pil().convert("RGB")
        if self.obs_type == "grayscale":
            img = img.convert("L")
        
        if self.render_mode == "human":
            if "pygame" not in sys.modules:
                raise RuntimeError(
                    "pygame is not installed, run `pip install pygame`"
                ) from e

            if self._screen is None:
                pygame.init()
                pygame.display.init()
                self._screen = pygame.display.set_mode(
                    self.gba.core.desired_video_dimensions()
                )
            if self._clock is None:
                self._clock = pygame.time.Clock()

            surf = _pil_image_to_pygame(img)
            self._screen.fill((0, 0, 0))
            self._screen.blit(surf, (0, 0))

            effective_fps = self.metadata["render_fps"]
            if self.frameskip:
                if isinstance(self.frameskip, tuple):
                    # average FPS is close enough
                    effective_fps /= (self.frameskip[0] + self.frameskip[1]) / 2 + 1
                else:
                    effective_fps /= self.frameskip + 1

            pygame.event.pump()
            self._clock.tick(effective_fps)
            pygame.display.flip()
        else:  # self.render_mode == "rgb_array"
            return np.array(img)

    def close(self):
        if self._screen is not None:
            if "pygame" not in sys.modules:
                pygame.display.quit()
                pygame.quit()
