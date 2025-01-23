import time

from loguru import logger
import RPi.GPIO as GPIO


class RpiGPIO:
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

if __name__ == "__main__":
    pin = 11
    gpio = RpiGPIO(pin)

    for i in range(5):
        print(f"Turning pin {pin} on")
        gpio.turn_on()
        time.sleep(1)
        print(f"Turning pin {pin} off")
        gpio.turn_off()
        time.sleep(1)
