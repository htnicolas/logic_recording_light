# Python class to connect to OBS websocket and remote start recording. Must be running on the same machine as OBS

import os
import time

from loguru import logger
import obsws_python as obs


class OBSController:
    """
    A simple class to control OBS via OBS Websockets.
    This assumes that a file named config.toml is present in the same directory as this file,
    which contains the OBS websocket connection information:

    [connection]
    host = "localhost"
    port = 4455
    password = "password"
    """
    def __init__(self):
        self.tic = None
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "config.toml")):
            logger.error(f"config.toml not found in the same directory as {__file__}")
            logger.error("config.toml should contain the OBS websocket connection information, eg:")
            logger.error("\n[connection]\nhost = \"localhost\"\nport = 4455\npassword = \"password\"")
            exit(1)

        try:
            self.cl = obs.ReqClient()
        except ConnectionRefusedError as e:
            logger.exception("Could not connect to OBS. Make sure OBS is running and the websocket server is enabled.")
            logger.exception("To enable the websocket server, open OBS -> Tools -> WebSockets Server Settings...")
            raise e
        resp = self.cl.get_version()
        logger.info(f"OBS Version: {resp.obs_version}")

    def start_recording(self) -> None:
        """
        Start recording in OBS
        """
        self.cl.start_record()
        self.tic = time.time()
        logger.info("Recording started")

    def stop_recording(self) -> None:
        """
        Stop recording in OBS
        """
        self.cl.stop_record()
        toc = time.time()
        logger.info(f"Recording stopped. Recording duration: {toc - self.tic:.2f} seconds")
        logger.info(f"Output saved to {self.cl.get_record_directory().record_directory}")

if __name__ == "__main__":
    obs_controller = OBSController()
    obs_controller.start_recording()
    time.sleep(5)
    obs_controller.stop_recording()
