import time
from loguru import logger
from pythonosc import udp_client


IP_ADDRESS = "rpi.lan"
PORT = 5005
LIGHTS_ON = [144, 25, 127]
LIGHTS_OFF = [144, 25, 0]

# IP_ADDRESS = "192.168.40.28"
client = udp_client.SimpleUDPClient(IP_ADDRESS, PORT)
client.send_message("/midi", LIGHTS_ON)
logger.info(f"Sent MIDI message {LIGHTS_ON} over OSC channel /midi")
time.sleep(2)
client.send_message("/midi", LIGHTS_OFF)
logger.info(f"Sent MIDI message {LIGHTS_OFF} over OSC channel /midi")

