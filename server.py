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

from AsyncWorker import AsyncWorker
from devices.LightController import LightController
from devices.DirigeraPlugController import DirigeraPlugController
from devices.DirigeraLightController import DirigeraLightController, COLOR_TO_HEX
import midi_states as ms
if sys.platform == "linux":
    logger.info("Running on Linux, using GPIOLightController")
    from devices.GPIOLightController import GPIOLightController
    CommonLightController = GPIOLightController
elif sys.platform == "darwin":
    logger.info("Running on macOS, using DummyLightController")
    from devices.DummyLightController import DummyLightController
    CommonLightController = DummyLightController

GPIO_PIN = 16
DIRIGERA_LIGHT_NAME = "recording_light"

def process_midi_rec_light(
        midi_data:list,
        light_controller:LightController,
        async_worker:AsyncWorker,
        rgb_light_controller:DirigeraLightController=None,
        sunset_lights_plug:DirigeraPlugController=None,
        spotlight_plug:DirigeraPlugController=None,
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
        async_worker: AsyncWorker object to run async tasks
        rgb_light_controller: DirigeraLightController object to control a RGB light
        sunset_lights_plug: DirigeraPlugController object to control a plug
        spotlight_plug: DirigeraPlugController object to control a plug
    """
    status, data1, data2 = midi_data

    midi_action = ms.get_midi_action(midi_data)
    match midi_action:

        case ms.MidiActions.RESET_ALL:
            logger.info(f"{midi_data}\tInit server state")
            async_worker.run_task(
                    light_controller.async_health_check()
                    )
            if rgb_light_controller:
                async_worker.run_task(
                        rgb_light_controller.async_turn_on(hex_color=COLOR_TO_HEX["orange"])
                        )
            if spotlight_plug:
                async_worker.run_task(spotlight_plug.async_turn_off())
            if sunset_lights_plug:
                async_worker.run_task(sunset_lights_plug.async_turn_on())

        case ms.MidiActions.RECORD_START:
            logger.info(f"{midi_data}\tRecording started")
            async_worker.run_task(
                    light_controller.async_turn_on()
                    )
            if rgb_light_controller:
                async_worker.run_task(
                        rgb_light_controller.async_turn_on(hex_color=COLOR_TO_HEX["red"])
                        )
            if sunset_lights_plug:
                async_worker.run_task(sunset_lights_plug.async_turn_on())

        case ms.MidiActions.RECORD_STOP:
            logger.info(f"{midi_data}\tRecording stopped")
            async_worker.run_task(light_controller.async_turn_off())
            if rgb_light_controller:
                async_worker.run_task(
                        rgb_light_controller.async_turn_on(hex_color=COLOR_TO_HEX["pink"])
                        )

        case ms.MidiActions.PLAY:
            logger.info(f"{midi_data}\tPlay")
            if rgb_light_controller:
                async_worker.run_task(
                        rgb_light_controller.async_turn_on(hex_color=COLOR_TO_HEX["dark_green"])
                        )
            if spotlight_plug:
                async_worker.run_task(spotlight_plug.async_turn_on())
            if sunset_lights_plug:
                async_worker.run_task(sunset_lights_plug.async_turn_off())

        case ms.MidiActions.STOP:
            logger.info(f"{midi_data}\tPause")
            if rgb_light_controller:
                async_worker.run_task(
                        rgb_light_controller.async_turn_on(hex_color=COLOR_TO_HEX["pink"])
                        )
            if spotlight_plug:
                async_worker.run_task(spotlight_plug.async_turn_off())
            if sunset_lights_plug:
                async_worker.run_task(sunset_lights_plug.async_turn_on())

        case ms.MidiActions.TRACK_LEFT:
            logger.info(f"{midi_data}\tTrack Left")

        case ms.MidiActions.TRACK_RIGHT:
            logger.info(f"{midi_data}\tTrack Right")

        case ms.MidiActions.ALL_NOTES_OFF:
            # User quit Logic Pro X: turn everything off, server is still running
            logger.info(f"{midi_data}\tTurn all off")
            async_worker.run_task(light_controller.async_turn_off())
            if rgb_light_controller:
                async_worker.run_task(
                        rgb_light_controller.async_turn_off()
                        )
            if sunset_lights_plug:
                async_worker.run_task(sunset_lights_plug.async_turn_off())
            if spotlight_plug:
                spotlight_plug.turn_off()
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

    async_worker = AsyncWorker()
    light_controller = CommonLightController(GPIO_PIN)
    async_worker.run_task(light_controller.async_health_check())
    try:
        rgb_light_controller = DirigeraLightController(DIRIGERA_LIGHT_NAME)
        async_worker.run_task(
                rgb_light_controller.async_health_check()
                )

        # Sunset lights
        sunset_lights_plug_controller = DirigeraPlugController("Sunset Lights", start_on=True)
        async_worker.run_task(
                sunset_lights_plug_controller.async_health_check()
                )

        # Spotlight + disco ball
        spotlight_plug_controller = DirigeraPlugController("Spotlight Plug")
        async_worker.run_task(
                spotlight_plug_controller.async_health_check()
                )
    except Exception as e:
        # When testing locally, Dirigera controllers may not be available
        logger.warning(f"Error initializing Dirigera controllers: {e}")
        logger.warning("Processing without Dirigera device control")
        rgb_light_controller = None
        sunset_lights_plug_controller = None
        spotlight_plug_controller = None

    dispatcher = Dispatcher()
    dispatcher.map(
            args.osc_channel,
            midi_handler,
            partial(
                process_midi_rec_light,
                async_worker=async_worker,
                light_controller=light_controller,
                rgb_light_controller=rgb_light_controller,
                sunset_lights_plug=sunset_lights_plug_controller,
                spotlight_plug=spotlight_plug_controller,
                ),
            )

    server = osc_server.ThreadingOSCUDPServer(
            (args.ip, args.port),
            dispatcher,
            )
    logger.info(f"Listening on {server.server_address}")
    logger.info("Ready")


    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        async_worker.run_task(light_controller.async_turn_off())
        if rgb_light_controller:
            async_worker.run_task(rgb_light_controller.async_turn_off())
        if sunset_lights_plug_controller:
            async_worker.run_task(sunset_lights_plug_controller.async_turn_off())
        if spotlight_plug_controller:
            async_worker.run_task(spotlight_plug_controller.async_turn_off())
        time.sleep(1)
        logger.info("Exiting...")
        exit(0)

