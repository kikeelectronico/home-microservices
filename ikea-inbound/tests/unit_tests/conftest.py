from pathlib import Path
import sys


SERVICE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVICE_DIR))
