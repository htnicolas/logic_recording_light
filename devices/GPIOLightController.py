# Will only work on raspberry pi
import time
import asyncio

from loguru import logger
import RPi.GPIO as GPIO

from devices.LightController import LightController


class GPIOLightController(LightController):
    def __init__(self, pin:int):
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        logger.info(f"Set pin #{self.pin} to OUT in [GPIO.BOARD] mode")

    def turn_on(self, hex_color:str|None=None):
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def health_check(self):
        self.turn_off()
        self.turn_on()
        time.sleep(1)
        self.turn_off()
        logger.info("GPIO light OK")

    async def async_turn_on(self, hex_color:str|None=None):
        await asyncio.to_thread(self.turn_on, hex_color)

    async def async_turn_off(self):
        await asyncio.to_thread(self.turn_off)

    async def async_health_check(self):
        await asyncio.to_thread(self.turn_off)
        await asyncio.sleep(1)
        await asyncio.to_thread(self.turn_on)
        await asyncio.sleep(1)
        await asyncio.to_thread(self.turn_off)
        logger.info("GPIO light OK")

if __name__ == "__main__":
    pin = 16
    gpio = GPIOLightController(pin)

    for i in range(3):
        print(f"Turning pin {pin} on")
        gpio.turn_on()
        time.sleep(1)
        print(f"Turning pin {pin} off")
        gpio.turn_off()
        time.sleep(1)
