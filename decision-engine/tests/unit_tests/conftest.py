from pathlib import Path
import sys


SERVICE_DIR = Path(__file__).resolve().parents[2]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))
