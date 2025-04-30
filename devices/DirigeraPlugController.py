import os
import time
import asyncio
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

    # Async methods
    async def async_turn_on(self) -> None:
        """
        Turn on the plug asynchronously.
        """
        await asyncio.to_thread(self.turn_on)

    async def async_turn_off(self) -> None:
        """
        Turn off the plug asynchronously.
        """
        await asyncio.to_thread(self.turn_off)

    async def async_health_check(self) -> None:
        await self.async_turn_on()
        await asyncio.sleep(0.2)  # Non-blocking sleep
        await self.async_turn_off()
        logger.info(f"Plug {self.plug_name} OK")

# Timing comparison functions
def time_sync_operations(lights: list[DirigeraPlugController]) -> float:
    """
    Time synchronous operations on a list of smart lights.
    Returns elapsed time in seconds.
    """
    start_time = time.time()

    for light in lights:
        light.health_check()

    end_time = time.time()
    return end_time - start_time


async def time_async_operations(lights: list[DirigeraPlugController]) -> float:
    """
    Time asynchronous operations on a list of smart lights.
    Returns elapsed time in seconds.
    """
    start_time = time.time()

    # Create a list of coroutines to execute
    tasks = [light.async_health_check() for light in lights]

    # Run all health checks concurrently
    await asyncio.gather(*tasks)

    end_time = time.time()
    return end_time - start_time


async def run_timing_comparison(lights: list[DirigeraPlugController]) -> None:
    """
    Run and report timing comparison between sync and async operations.
    """
    # Time synchronous operations
    sync_time = time_sync_operations(lights)
    logger.info(f"Synchronous operation time: {sync_time:.2f} seconds")

    # Time asynchronous operations
    async_time = await time_async_operations(lights)
    logger.info(f"Asynchronous operation time: {async_time:.2f} seconds")

    improvement = (sync_time - async_time) / sync_time * 100
    logger.info(f"Improvement: {improvement:.2f}%")
    return


if __name__ == "__main__":
    plug_controller = DirigeraPlugController("disco")
    spotlight_plug_controller = DirigeraPlugController("Spotlight Plug")

    lights = [plug_controller, spotlight_plug_controller]

    asyncio.run(run_timing_comparison(lights))
    plug_controller.health_check()
    exit(0)

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
