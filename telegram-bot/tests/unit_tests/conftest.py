import sys
import types
from pathlib import Path


SERVICE_DIR = Path(__file__).resolve().parents[2]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

# The tests mock pytube's network-facing classes; keep the suite runnable when
# runtime requirements have not been installed in the test environment.
try:
    import pytube  # noqa: F401
except ModuleNotFoundError:
    pytube_stub = types.ModuleType("pytube")
    pytube_stub.YouTube = object
    pytube_stub.Playlist = object
    sys.modules["pytube"] = pytube_stub
