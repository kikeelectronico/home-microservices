"""Helpers for importing the flat-layout service during pytest collection."""

import os
import sys


def add_service_to_path():
    service_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if service_dir not in sys.path:
        sys.path.insert(0, service_dir)
