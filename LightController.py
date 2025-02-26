# A simple class to control a light using a GPIO pin
from abc import ABC, abstractmethod


class LightController(ABC):
    @abstractmethod
    def turn_on(self, hex_color:str|None=None):
        pass

    @abstractmethod
    def turn_off(self):
        pass


