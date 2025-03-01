# Script to emulate a MIDI controller by sending MIDI messages to the OSC server

import time
import socket
import argparse

from loguru import logger
from pythonosc import udp_client


RECORD_START = [144, 25, 127]
RECORD_STOP = [144, 25, 0]
PLAY = [16, 106, 127]
STOP = [16, 105, 127]
MIDI_MESSAGES = [RECORD_START, RECORD_STOP, PLAY, STOP]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--hostname",
            default="rpi.local",
            help="The hostname of the instance running server.py connected to the recording light. Use 'localhost' if testing locally",
            )
    parser.add_argument(
            "--port",
            type=int,
            default=5005,
            help="The port to send OSC messages to",
            )
    args = parser.parse_args()

    rpi_hostname = args.hostname # Hostname of the instance running server.py
    port = args.port

    logger.info(f"Sending MIDI messages to {rpi_hostname}:{port}")

    try:
        rpi_ip = socket.gethostbyname(rpi_hostname)
        client = udp_client.SimpleUDPClient(rpi_ip, port)
    except socket.gaierror as e:
        logger.error(f"Could not resolve hostname {rpi_hostname} to an IP address")
        logger.error("If you are testing locally, use 'localhost' as the hostname")
        raise e

    for message in MIDI_MESSAGES:
        client.send_message("/midi", message)
        logger.info(f"Sent MIDI message {message} over OSC channel /midi")
        time.sleep(2)
