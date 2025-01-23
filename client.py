# This program is to be run on the machine running Logic Pro X.
# To setup recording light, go to Logic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light
import argparse

from loguru import logger
import rtmidi
from pythonosc import udp_client


IP_ADDRESS = "rpi.lan" # IP address of the RPi connected to the recording light
PORT = 5005
client = udp_client.SimpleUDPClient(IP_ADDRESS, PORT)

def send_midi_message_over_osc(message, data):
    """
    Callback function to send MIDI message over OSC
    Args:
        message: MIDI message from rtmidi. Tuple([status, data1, data2], timestamp)
        data: osc channel. Str, eg "/midi"
    """
    osc_channel = data
    midi_message = message[0] # Ignore timestamp
    client.send_message(osc_channel, midi_message)
    logger.info(f"Sent MIDI message {midi_message} over OSC channel {osc_channel}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--osc_channel",
            type=str,
            default="/midi",
            help="The OSC channel to listen on",
            )
    args = parser.parse_args()

    midi_in = rtmidi.MidiIn()
    available_ports = midi_in.get_ports()

    osc_channel = args.osc_channel

    if available_ports:
        midi_in.open_port(0)
        midi_in.set_callback(send_midi_message_over_osc, osc_channel)
        logger.info(f"Opened MIDI port {available_ports[0]}")
    else:
        logger.warning("No MIDI ports available. Make sure that Logic Pro X is open, and that a recording light was setup:\nLogic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light")
        logger.info("Exiting...")
        exit(1)

    logger.info(f"OSC client set up on {IP_ADDRESS}:{PORT}")
    logger.info(f"Sending MIDI messages over OSC channel {osc_channel}")

    try:
        while True:
            # Keep the main thread alive to receive MIDI messages
            pass
    except KeyboardInterrupt:
        logger.info("Exiting...")
    finally:
        midi_in.close_port()
        exit(0)
