import os
from pathlib import Path

import aiy.audio

from . import settings
from .watson import *

_audio_path = Path(os.path.join(os.path.dirname(settings.RESOURCE_PATH), 'audio'))


def play_sound(name):
    aiy.audio.get_player().play_wav(
        _audio_path.absolute().joinpath(os.path.join('{}.wav'.format(name))).absolute().as_posix())


def get_sounds():
    return [f.stem for f in _audio_path.glob('*.wav')]
