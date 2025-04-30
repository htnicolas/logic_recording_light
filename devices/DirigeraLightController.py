import os
import time
import requests
import asyncio

import dirigera
from loguru import logger

from devices.LightController import LightController


COLOR_TO_HEX = {
    "red": "#ff3729",
    "green": "#47ff88",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "light_blue": "#1fb0ff",
    "magenta": "#FF00FF",
    "orange": "#FFA500",
    "pink": "#ff758f",
    "purple": "#e300e3",
    "white": "#FFFFFF",
    }

class DirigeraLightController(LightController):
    def __init__(self, light_name: str):
        """
        Args:
            light_name: Name of the light to control, e.g. "recording_light".
                        Refer to the name set in the Ikea Smart Home app.
        """
        # Get env var DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS
        dirigera_token = os.getenv("DIRIGERA_TOKEN")
        dirigera_ip_address = os.getenv("DIRIGERA_IP_ADDRESS")
        if not dirigera_token or not dirigera_ip_address:
            logger.error("Please set the environment variables DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS")
            raise ValueError("Please set the environment variables DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS")

        logger.info(f"Connecting to Dirigera Hub at {dirigera_ip_address}...")
        self.dirigera_hub = dirigera.Hub(
            token=dirigera_token,
            ip_address=dirigera_ip_address,
        )

        self.light = None

        try:
            lights = self.dirigera_hub.get_lights()
        except requests.exceptions.ConnectionError as e:
            # Dirigera Hub IP is likely wrong
            logger.exception(e)
            logger.warning(f"Could not connect to Dirigera Hub at {dirigera_ip_address}. Please check the connection.")
            raise e

        for light in lights:
            if light.attributes.custom_name == light_name:
                self.light = light
                break

        if not self.light:
            logger.error(f"No Dirigera-enabled light with name '{light_name}' found")
            logger.error(f"Available lights: {[l.attributes.custom_name for l in lights]}")
            raise ValueError(f"No Dirigera-enabled light with name '{light_name}' found")

        self.light_name = light_name

    def turn_on(self, hex_color: str | None = None) -> None:
        """
        Turn on the light with the specified hex color.
        Note: need to turn the light on first before setting the color or it won't do anything.
        Args:
            hex_color: Str, hex color code
        """
        if not self.light.attributes.is_on:
            self.light.set_light(lamp_on=True)
        if hex_color:
            hue, saturation, value = hex_to_hsv(hex_color)
            self.light.set_light_color(hue=hue, saturation=saturation / 100)
            self.light.set_light_level(light_level=value)

    def turn_off(self) -> None:
        self.light.set_light(lamp_on=False)

    async def async_turn_on(self, hex_color: str | None = None) -> None:
        """
        Turn on the light asynchronously with the specified hex color.
        Note: need to turn the light on first before setting the color or it won't do anything.
        Args:
            hex_color: Str, hex color code
        """
        await asyncio.to_thread(self.turn_on, hex_color)

    async def async_turn_off(self) -> None:
        """
        Turn off the light asynchronously.
        """
        await asyncio.to_thread(self.turn_off)

    def health_check(self) -> None:
        logger.info(f"Performing health check for Dirigera light {self.light_name}...")
        self.turn_on(hex_color=COLOR_TO_HEX["green"])
        time.sleep(0.5)
        self.turn_on(hex_color=COLOR_TO_HEX["pink"])
        time.sleep(0.5)
        self.turn_on(hex_color=COLOR_TO_HEX["green"])
        logger.info(f"Health check: Dirigera light {self.light_name} OK.")

    async def async_health_check(self) -> None:
        logger.info(f"Performing health check for Dirigera light {self.light_name}...")
        await self.async_turn_on(hex_color=COLOR_TO_HEX["green"])
        await asyncio.sleep(0.5)
        await self.async_turn_on(hex_color=COLOR_TO_HEX["pink"])
        await asyncio.sleep(0.5)
        await self.async_turn_on(hex_color=COLOR_TO_HEX["green"])
        logger.info(f"Health check: Dirigera light {self.light_name} OK.")


# Timing comparison functions
def time_sync_operations(lights: list[DirigeraLightController]) -> float:
    """
    Time synchronous operations on a list of smart lights.
    Returns elapsed time in seconds.
    """
    start_time = time.time()

    for light in lights:
        light.health_check()

    end_time = time.time()
    return end_time - start_time


async def time_async_operations(lights: list[DirigeraLightController]) -> float:
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


async def run_timing_comparison(lights: list[DirigeraLightController]) -> None:
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

def hex_to_hsv(hex_color: str) -> tuple[float, float, float]:
    """
    Convert hex color to HSV
    Args:
        hex_color: Str, hex color code
    Returns:
        hsv: Tuple, HSV values
    """
    assert hex_color.startswith("#")

    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    if delta == 0:
        hue = 0
    elif cmax == r:
        hue = ((g - b) / delta) % 6
    elif cmax == g:
        hue = ((b - r) / delta) + 2
    else:
        hue = ((r - g) / delta) + 4
    hue = round(hue * 60)
    if cmax == 0:
        saturation = 0
    else:
        saturation = round(delta / cmax * 100)
    value = round(cmax * 100)
    return hue, saturation, value

if __name__ == "__main__":
    light_controller = DirigeraLightController("recording_light")
    asyncio.run(run_timing_comparison([light_controller]))
    exit(0)

    light_controller.turn_off()
    light_controller.health_check()
    for color, hex_color in COLOR_TO_HEX.items():
        logger.info(f"Turning on light with color {color}")
        light_controller.turn_on(hex_color=hex_color)
        time.sleep(2)
    light_controller.turn_off()
