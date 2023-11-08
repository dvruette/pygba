from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from pygba.pygba import PyGBA

class GameWrapper(ABC):
    @abstractmethod
    def reward(self, gba: PyGBA, observation: np.ndarray) -> float:
        raise NotImplementedError

    def game_over(self, gba: PyGBA, observation: np.ndarray) -> bool:
        return False
    
    def reset(self, gba: PyGBA) -> None:
        pass
    
    def info(self, gba: PyGBA, observation: np.ndarray) -> dict[str, Any]:
        return {}
