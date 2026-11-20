from pathlib import Path
import sys
import types


SERVICE_DIR = Path(__file__).resolve().parents[2]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

# Tests mock Chromecast discovery and devices, so the package is not needed to
# exercise the service when runtime dependencies are absent from the test env.
try:
    import pychromecast  # noqa: F401
except ModuleNotFoundError:
    pychromecast_stub = types.ModuleType("pychromecast")
    pychromecast_stub.get_listed_chromecasts = lambda **_kwargs: ([], None)
    sys.modules["pychromecast"] = pychromecast_stub
