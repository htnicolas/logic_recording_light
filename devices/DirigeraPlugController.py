import os
import time

import dirigera
from dirigera.devices.device import StartupEnum
from loguru import logger

from devices.LightController import LightController


class DirigeraPlugController(LightController):
    def __init__(self, plug_name: str):
        """
        Args:
            plug_name: Name of the plug to control, e.g. "disco_ball".
                       Refer to the name set in the Ikea Smart Home app.
        """
        # Get env var DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS
        dirigera_token = os.getenv("DIRIGERA_TOKEN")
        dirigera_ip_address = os.getenv("DIRIGERA_IP_ADDRESS")
        if not dirigera_token or not dirigera_ip_address:
            logger.error("Please set the environment variables DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS")
            raise ValueError("Please set the environment variables DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS")

        self.dirigera_hub = dirigera.Hub(
            token=dirigera_token,
            ip_address=dirigera_ip_address,
        )
        logger.info(f"Connected to Dirigera Hub at {dirigera_ip_address}")

        self.plug = None

        try:
            plugs = self.dirigera_hub.get_outlets()
        except requests.exceptions.ConnectionError as e:
            # Dirigera Hub IP is likely wrong
            logger.exception(e)
            logger.error(f"Could not connect to Dirigera Hub at {dirigera_ip_address}. Please check the connection.")
            raise e
            exit(1)

        for plug in plugs:
            if plug.attributes.custom_name == plug_name:
                self.plug = plug
                break

        if not self.plug:
            logger.error(f"No Dirigera-enabled plug with name '{plug_name}' found")
            logger.error(f"Available plugs: {[l.attributes.custom_name for l in plugs]}")
            raise ValueError(f"No Dirigera-enabled plug with name '{plug_name}' found")

        self.plug_name = plug_name
        self.plug.set_startup_behaviour(behaviour=StartupEnum.START_OFF)

    def turn_on(self) -> None:
        """
        Turn on the plug.
        """
        logger.info(f"Turning on plug {self.plug_name}")
        if not self.plug.attributes.is_on:
            self.plug.set_on(outlet_on=True)

    def turn_off(self) -> None:
        """
        Turn off the plug.
        """
        logger.info(f"Turning off plug {self.plug_name}")
        if self.plug.attributes.is_on:
            self.plug.set_on(outlet_on=False)

    def health_check(self) -> None:
        self.turn_on()
        time.sleep(0.2)
        self.turn_off()
        logger.info(f"Plug {self.plug_name} OK")

if __name__ == "__main__":
    plug_controller = DirigeraPlugController("disco")
    plug_controller.health_check()

    try:
        sleep = 1
        for i in range(3):
            plug_controller.turn_on()
            time.sleep(sleep)
            plug_controller.turn_off()
            time.sleep(sleep)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        plug_controller.turn_off()
        time.sleep(1)
        logger.info("Exiting...")
        exit(0)
