import RPi.GPIO as GPIO
import time

pin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(pin, GPIO.OUT)

for i in range(5):
    print(f"Turning on pin {pin}")
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(1)
    print(f"Turning off pin {pin}")
    GPIO.output(pin, GPIO.LOW)
    time.sleep(1)
