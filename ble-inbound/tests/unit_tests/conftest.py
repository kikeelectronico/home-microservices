import sys
import types
from pathlib import Path


SERVICE_DIR = Path(__file__).resolve().parents[2]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

# BLE peripherals are mocked by the tests; provide a small import shim when
# bluepy is unavailable (for example, in environments without BLE support).
try:
    from bluepy import btle  # noqa: F401
except ModuleNotFoundError:
    btle_stub = types.ModuleType("bluepy.btle")

    class DefaultDelegate:
        def __init__(self):
            pass

    class BTLEDisconnectError(Exception):
        pass

    btle_stub.DefaultDelegate = DefaultDelegate
    btle_stub.BTLEDisconnectError = BTLEDisconnectError
    btle_stub.ADDR_TYPE_RANDOM = "random"
    btle_stub.UUID = lambda value: value
    btle_stub.Peripheral = None
    btle_stub.Scanner = None
    bluepy_stub = types.ModuleType("bluepy")
    bluepy_stub.btle = btle_stub
    sys.modules["bluepy"] = bluepy_stub
    sys.modules["bluepy.btle"] = btle_stub
