# A simple class to control a light using a GPIO pin
import time

from loguru import logger
import RPi.GPIO as GPIO


class LightController:
    def __init__(self, pin:int):
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        logger.info(f"Set pin #{self.pin} to OUT in [GPIO.BOARD] mode")

    def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def health_check(self):
        self.turn_off()
        self.turn_on()
        time.sleep(1)
        self.turn_off()
        logger.info(f"Ready")

if __name__ == "__main__":
    pin = 16
    gpio = LightController(pin)

    for i in range(3):
        print(f"Turning pin {pin} on")
        gpio.turn_on()
        time.sleep(1)
        print(f"Turning pin {pin} off")
        gpio.turn_off()
        time.sleep(1)
