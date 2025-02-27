# A dummy class to test locally on macOs, since RPi module is only available on raspberry pi

import time

from loguru import logger

from LightController import LightController


class DummyLightController(LightController):
    def __init__(self, pin:int):
        logger.info(f"Dummy light init with pin={pin}")

    def turn_on(self, hex_color:str|None=None):
        logger.info("Dummy light: turning on")

    def turn_off(self):
        logger.info("Dummy light: turning off")

    def health_check(self):
        self.turn_off()
        self.turn_on()
        time.sleep(1)
        self.turn_off()
        logger.info(f"Dummy light ready")

if __name__ == "__main__":
    dummy = DummyLightController()

    for i in range(3):
        dummy.turn_on()
        time.sleep(1)
        dummy.turn_off()
        time.sleep(1)
