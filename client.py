# This program is to be run on the machine running Logic Pro X.
# To setup recording light, go to Logic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light
import argparse
import socket

from loguru import logger
import rtmidi
from pythonosc import udp_client

from OBSController import OBSController


PORT = 5005
LOGIC_MIDI_PORT_NAME = "Logic Pro Virtual Out"


def send_midi_message_over_osc(message:tuple, data_dict:dict):
    """
    Callback function to send MIDI message over OSC
    Args:
        message: MIDI message from rtmidi. Tuple([status, data1, data2], timestamp)
        data_dict: Dict, data dictionary containing the OSC channel, OBS controller, and OSC client
    """
    osc_channel = data_dict["osc_channel"]
    obs_controller = data_dict["obs_controller"]
    osc_client = data_dict["osc_client"]

    midi_message = message[0] # Ignore timestamp
    osc_client.send_message(osc_channel, midi_message)
    logger.info(f"Sent MIDI message {midi_message} over OSC channel {osc_channel}")

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
            logger.error("Is OBS running and the websocket server enabled?")
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

    if available_ports:
        for idx, port in enumerate(available_ports):
            logger.info(f"({idx}).\t{port}")
            if LOGIC_MIDI_PORT_NAME in port:
                midi_in.open_port(idx)
                midi_in.set_callback(send_midi_message_over_osc, callback_data)
                logger.info(f"Opened MIDI port {available_ports[idx]}")
    else:
        logger.warning("No MIDI ports available. Make sure that Logic Pro X is open, and that a recording light was setup:\nLogic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light")
        logger.info("Exiting...")
        exit(1)

    logger.info(f"OSC client set up with hostname {args.rpi_hostname} on port {PORT}")
    logger.info(f"Sending MIDI messages over OSC channel {args.osc_channel}")

    try:
        while True:
            # Keep the main thread alive to receive MIDI messages
            pass
    except KeyboardInterrupt:
        logger.info("Exiting...")
    finally:
        midi_in.close_port()
        exit(0)
