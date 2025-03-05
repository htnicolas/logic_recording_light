# This program listens to an OSC address for MIDI data
# To be run on raspberry pi: turn on GPIO pins when recording starts, turn off when recording stops
# If running on macOS, it uses DummyLightController to simulate GPIO pin

import sys
import argparse
import time
from functools import partial

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from loguru import logger

from LightController import LightController
from DirigeraPlugController import DirigeraPlugController
from DirigeraLightController import DirigeraLightController, COLOR_TO_HEX
import midi_states as ms
if sys.platform == "linux":
    logger.info("Running on Linux, using GPIOLightController")
    from GPIOLightController import GPIOLightController
    CommonLightController = GPIOLightController
elif sys.platform == "darwin":
    logger.info("Running on macOS, using DummyLightController")
    from DummyLightController import DummyLightController
    CommonLightController = DummyLightController

GPIO_PIN = 16
DIRIGERA_LIGHT_NAME = "recording_light"

def process_midi_rec_light(
        midi_data:list,
        light_controller:LightController,
        rgb_light_controller:DirigeraLightController=None,
        plug_controller:DirigeraPlugController=None,
        ) -> None:
    """
    Process MIDI data received from OSC.
    Check the MIDI message corresponding to the record action in Logic.
    Trigger an action like turning on a light accordingly.
    Args:
        midi_data: List, MIDI message from OSC consisting of status,
                    data1, data2
        light_controller: LightController object to control a light.
                    Eg GPIOLightController or DummyLightController object
        rgb_light_controller: DirigeraLightController object to control a RGB light
        plug_controller: DirigeraPlugController object to control a plug
    """
    status, data1, data2 = midi_data

    midi_action = ms.get_midi_action(midi_data)
    match midi_action:
        case ms.MidiActions.RECORD_START:
            logger.info(f"{midi_data}\tRecording started")
            light_controller.turn_on()
            if rgb_light_controller:
                rgb_light_controller.turn_on(hex_color=COLOR_TO_HEX["red"])
        case ms.MidiActions.RECORD_STOP:
            logger.info(f"{midi_data}\tRecording stopped")
            light_controller.turn_off()
            if rgb_light_controller:
                rgb_light_controller.turn_on(hex_color=COLOR_TO_HEX["pink"])
        case ms.MidiActions.PLAY:
            logger.info(f"{midi_data}\tPlay")
            if rgb_light_controller:
                rgb_light_controller.turn_on(hex_color=COLOR_TO_HEX["light_blue"])
            if plug_controller:
                plug_controller.turn_on()
        case ms.MidiActions.STOP:
            logger.info(f"{midi_data}\tPause")
            if rgb_light_controller:
                rgb_light_controller.turn_on(hex_color=COLOR_TO_HEX["pink"])
            if plug_controller:
                plug_controller.turn_off()
        case ms.MidiActions.TRACK_LEFT:
            logger.info(f"{midi_data}\tTrack Left")
        case ms.MidiActions.TRACK_RIGHT:
            logger.info(f"{midi_data}\tTrack Right")
        case _:
            pass

def midi_handler(unused_addr, args, *midi_message):
    """
    Callback function to handle MIDI messages
    Args:
        unused_addr: Unused
        args: Additional arguments passsed via the dispatcher. Eg process_midi_rec_light
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

    light_controller = CommonLightController(GPIO_PIN)
    light_controller.health_check()
    try:
        rgb_light_controller = DirigeraLightController(DIRIGERA_LIGHT_NAME)
        rgb_light_controller.health_check()

        disco_plug_controller = DirigeraPlugController("disco")
        disco_plug_controller.health_check()
    except Exception as e:
        # When testing locally, Dirigera controllers may not be available
        logger.error(f"Error initializing Dirigera controllers: {e}")
        logger.error("Continuing without RGB light and plug control")
        rgb_light_controller = None
        disco_plug_controller = None

    dispatcher = Dispatcher()
    dispatcher.map(
            args.osc_channel,
            midi_handler,
            partial(
                process_midi_rec_light,
                light_controller=light_controller,
                rgb_light_controller=rgb_light_controller,
                plug_controller=disco_plug_controller,
                ),
            )

    server = osc_server.ThreadingOSCUDPServer(
            (args.ip, args.port),
            dispatcher,
            )
    logger.info(f"Listening on {server.server_address}")


    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        light_controller.turn_off()
        if rgb_light_controller:
            rgb_light_controller.turn_off()
        if disco_plug_controller:
            disco_plug_controller.turn_off()
        time.sleep(1)
        logger.info("Exiting...")
        exit(0)

