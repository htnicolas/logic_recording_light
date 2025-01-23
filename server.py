# This program listens to an OSC address for MIDI data
# To be run on raspberry pi: turn on GPIO pins when recording starts, turn off when recording stops

import argparse

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from loguru import logger


def process_midi(midi_data):
    """
    Process MIDI data received from OSC
    Check the MIDI message type and perform actions accordingly.
    Args:
        midi_data: List, MIDI message from OSC
    """
    status, data1, data2 = midi_data
    if data1 == 25:
        if data2 == 127:
            logger.info(f"{midi_data}\tRecording started")
        elif data2 == 0:
            logger.info(f"{midi_data}\tRecording stopped")

def midi_handler(unused_addr, args, *midi_message):
    """
    Callback function to handle MIDI messages
    Args:
        unused_addr: Unused
        args: Additional arguments passsed via the dispatcher. Eg process_midi
        midi_message: MIDI message from OSC, unpacked tuple
    """
    process_func = args[0] # Callable to process MIDI data
    midi_data = list(midi_message) # Convert unpacked tuple to list
    process_func(midi_data)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--ip",
            default="0.0.0.0", # Listen on all available interfaces
            help="The ip to listen on",
            )
    parser.add_argument(
            "--port",
            type=int,
            default=5005,
            help="The port to listen on",
            )
    parser.add_argument(
            "--osc_channel",
            type=str,
            default="/midi",
            help="The OSC channel to listen on",
            )
    args = parser.parse_args()
    dispatcher = Dispatcher()
    dispatcher.map(
            args.osc_channel,
            midi_handler,
            process_midi,
            )

    server = osc_server.ThreadingOSCUDPServer(
            (args.ip, args.port),
            dispatcher,
            )
    logger.info(f"Listening on {server.server_address}")
    server.serve_forever()

