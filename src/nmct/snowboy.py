import os

from nmct.settings import RESOURCE_PATH
from nmct.apis.snowboy import SnowboyDetector

RESOURCE_FILE = os.path.join(RESOURCE_PATH, "snowboy", "common.res")

_detector = None


def get_detector():
    global _detector
    if _detector is None:
        _detector = SnowboyDetector(RESOURCE_FILE)
    return _detector
