# This program is to be run on the machine running Logic Pro X.
# To setup recording light, go to Logic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light
import os
import argparse
import socket

from loguru import logger
import rtmidi
from pythonosc import udp_client

from OBSController import OBSController
import midi_states as ms


PORT = 5005
LOGIC_MIDI_PORT_NAME = "Logic Pro Virtual Out" # Default name of Logic Pro X's virtual MIDI port
KEYBOARD_MIDI_PORT_NAME = "Impact LX61+ MIDI2" # Change this to the name of your MIDI controller
MIDI_SOURCES = [LOGIC_MIDI_PORT_NAME, KEYBOARD_MIDI_PORT_NAME]


def send_midi_message_over_osc(message:tuple, data_dict:dict) -> None:
    """
    Callback function to send MIDI message over OSC
    Args:
        message: MIDI message from rtmidi. Tuple([status, data1, data2], timestamp)
        data_dict: Dict, data dictionary containing the OSC channel, OBS controller, and OSC client
    """
    osc_channel = data_dict["osc_channel"]
    obs_controller = data_dict["obs_controller"]
    osc_client = data_dict["osc_client"]

    midi_data = message[0] # Ignore timestamp

    # Make sure it is 3 bytes long
    if len(midi_data) != 3:
        logger.warning(f"Invalid MIDI message: {midi_data}")
        pass

    midi_action = ms.get_midi_action(midi_data)
    match midi_action:
        case ms.MidiActions.RECORD_START:
            # Record video with OBS
            if obs_controller:
                logger.info(f"{midi_data}\tStarting OBS recording")
                obs_controller.start_recording()
        case ms.MidiActions.RECORD_STOP:
            if obs_controller:
                logger.info(f"{midi_data}\tStopping OBS recording")
                obs_controller.stop_recording()
        case ms.MidiActions.ALL_NOTES_OFF:
            osc_client.send_message(osc_channel, midi_data)
            # Exit the program
            logger.info(f"{midi_data}\tAll notes off")
            if obs_controller:
                logger.info(f"{midi_data}\tStopping OBS recording")
                obs_controller.stop_recording()
            logger.warning("All notes off event received. Exiting...")
            os._exit(0)

    # Send MIDI message over OSC
    osc_client.send_message(osc_channel, midi_data)
    logger.info(f"Sent MIDI message {midi_data} over OSC channel {osc_channel}")
    return

def create_osc_client(rpi_hostname:str, port:int) -> udp_client.SimpleUDPClient:
    """
    Create an OSC client
    Args:
        rpi_hostname: Str, IP address of the RPi connected to the recording light
        port: Int, port number
    Returns:
        osc_client: SimpleUDPClient, OSC client
    """
    try:
        logger.info(f"Connecting to {rpi_hostname}:{port}")
        rpi_ip = socket.gethostbyname(rpi_hostname)

        logger.info(f"Resolved hostname {rpi_hostname} to IP address {rpi_ip}")
        osc_client = udp_client.SimpleUDPClient(rpi_ip, port)
        return osc_client

    except socket.gaierror as e:
        logger.exception(f"Could not connect to IP from hostname {rpi_hostname} on port {port}.")
        logger.error("Make sure the RPi is connected to the same network as the machine running Logic Pro X and double-check its hostname.")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--osc_channel",
            type=str,
            default="/midi",
            help="The OSC channel to listen on",
            )
    parser.add_argument(
            "--rpi_hostname",
            type=str,
            default="rpi.local",
            help="The hostname of the RPi connected to the recording light",
            )
    parser.add_argument(
            "--record_obs",
            action="store_true",
            help="Enable OBS recording control",
        )
    args = parser.parse_args()

    midi_in = rtmidi.MidiIn()
    available_ports = midi_in.get_ports()

    # Controller for OBS
    obs_controller = None
    if args.record_obs:
        try:
            logger.info("OBS recording control enabled")
            obs_controller = OBSController()
        except ConnectionRefusedError as e:
            logger.error("Is OBS running? And is the OBS websocket server enabled?")
            exit(1)

    # Controller for OSC
    osc_client = create_osc_client(
            rpi_hostname=args.rpi_hostname,
            port=PORT,
            )

    # Prepare data dictionary to pass to callback
    callback_data = {
        "osc_channel": args.osc_channel,
        "obs_controller": obs_controller,
        "osc_client": osc_client,
    }

    midi_ins = []
    found_midi_sources = {midi_source: False for midi_source in MIDI_SOURCES}

    # Loop through available MIDI ports and open the ones we want to listen to MIDI messages on
    if available_ports:
        logger.info(f"Available MIDI ports: {available_ports}")
        for idx, port in enumerate(available_ports):
            # We want to catch MIDI messages from Logic Pro X's virtual MIDI port
            # We also want to catch MIDI messages from a MIDI controller
            # Both sources are tied to the same callback function to send MIDI over OSC

            for midi_source in MIDI_SOURCES:
                if midi_source in port:
                    midi_in = rtmidi.MidiIn()
                    midi_in.open_port(idx)
                    midi_in.set_callback(send_midi_message_over_osc, callback_data)
                    logger.info(f"Opened MIDI port {available_ports[idx]}")
                    midi_ins.append(midi_in)
                    found_midi_sources[midi_source] = True

    else:
        logger.error("No MIDI ports available. Make sure that Logic Pro X is open, and that a recording light was setup:\nLogic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light")
        logger.info("Exiting...")
        exit(1)

    # Warn user if any of the MIDI sources were not found
    for midi_source, found in found_midi_sources.items():
        if not found:
            logger.warning(f"Could not find MIDI source '{midi_source}'. Make sure that the MIDI controller is connected and that Logic Pro X is open.")

    logger.info(f"OSC client set up with hostname {args.rpi_hostname} on port {PORT}")
    logger.info(f"Sending MIDI messages over OSC channel {args.osc_channel}")

    try:
        while True:
            # Keep the main thread alive to receive MIDI messages
            pass
    except KeyboardInterrupt:
        logger.info("Exiting...")
    finally:
        for midi_in in midi_ins:
            midi_in.close_port()
        exit(0)
