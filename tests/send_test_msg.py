import time
from loguru import logger
from pythonosc import udp_client


IP_ADDRESS = "rpi.lan" # Change to the IP of the RPi connected to the recording light
PORT = 5005
LIGHTS_ON = [144, 25, 127]
LIGHTS_OFF = [144, 25, 0]

logger.info(f"Sending MIDI messages to {IP_ADDRESS}:{PORT}")

client = udp_client.SimpleUDPClient(IP_ADDRESS, PORT)
client.send_message("/midi", LIGHTS_ON)
logger.info(f"Sent MIDI message {LIGHTS_ON} over OSC channel /midi")
time.sleep(2)
client.send_message("/midi", LIGHTS_OFF)
logger.info(f"Sent MIDI message {LIGHTS_OFF} over OSC channel /midi")

