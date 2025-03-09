import sys
import os

import pytest

sys.path.append("..")
from devices.DirigeraLightController import DirigeraLightController


class TestDirigeraLightController:
    def test_dirigera_light_controller_no_env_var(self):
        # Unset the environment variables
        if "DIRIGERA_TOKEN" in os.environ:
            del os.environ["DIRIGERA_TOKEN"]
        if "DIRIGERA_IP_ADDRESS" in os.environ:
            del os.environ["DIRIGERA_IP_ADDRESS"]
        with pytest.raises(ValueError, match="Please set the environment variables DIRIGERA_TOKEN and DIRIGERA_IP_ADDRESS"):
            light_controller = DirigeraLightController("recording_light")

    def test_dirigera_light_controller_unknown_light_name(self):
        with pytest.raises(ValueError):
            light_controller = DirigeraLightController("non_existent_light")
