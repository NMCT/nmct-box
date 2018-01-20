import os
from pathlib import Path
from snowboy import snowboydetect

from nmct.apis.snowboy import HotWord, SnowboyDetector

RESOURCE_FILE = os.path.join(os.path.dirname(snowboydetect.__file__), 'resources', 'common.res')

_detector = None


def builtin_hotwords():
    p = Path(os.path.join(os.path.dirname(snowboydetect.__file__), 'resources'))
    return [HotWord(f.absolute().as_posix(), f.stem) for f in p.glob('*.umdl')]


def get_detector():
    global _detector
    if _detector is None:
        _detector = SnowboyDetector(RESOURCE_FILE)
    return _detector
