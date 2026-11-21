from pathlib import Path
import sys


SERVICE_PATH = Path(__file__).resolve().parents[2]
if str(SERVICE_PATH) not in sys.path:
    sys.path.insert(0, str(SERVICE_PATH))
