import os
import queue
from signal import signal
from snowboy import snowboydetect

import aiy.audio

from nmct.settings import RESOURCE_PATH


class HotWord:
    def __init__(self, model, name: str = None, sensitivity: float = 0.5):
        if name is None:
            import re
            name = re.search(r'[ \w-]+?(?=\.)', model).group(0)
        self.model = model
        self.name = name
        self.sensitivity = sensitivity


class SnowboyDetector:
    def __init__(self, resource):
        self._resource = resource
        self._gain = 1
        self._detector = None
        # self._detector_lock = threading.Lock()

        self._hotwords = []
        self.buffer = queue.Queue()

    @property
    def audio_gain(self):
        return self._gain

    @audio_gain.setter
    def audio_gain(self, value):
        self._gain = value
        if self._detector:
            self._detector.SetAudioGain(self._gain)

    def setup(self):
        model_str = ",".join([w.model for w in self._hotwords])
        sensitivity_str = ",".join([str(w.sensitivity) for w in self._hotwords])
        self._detector = snowboydetect.SnowboyDetect(
            resource_filename=self._resource.encode(), model_str=model_str.encode())
        self._detector.SetSensitivity(sensitivity_str.encode())
        self._detector.SetAudioGain(self._gain)

    def add_hotword(self, value):
        if isinstance(value, HotWord):
            self._hotwords.append(value)
        else:
            self._hotwords.append(HotWord(os.path.join(RESOURCE_PATH, 'snowboy', value),
                                          "::".join(value.split('.')[:-1])))
        self.setup()
        return self

    __iadd__ = add_hotword

    def with_hotword(self, *args, **kwargs):
        self.add_hotword(*args, **kwargs)
        return self

    def add_data(self, audio):
        self.buffer.put(audio)

    def wait_for_hotword(self):
        recorder = aiy.audio.get_recorder()
        recorder.add_processor(self)
        while True:
            audio = self.buffer.get()
            result = self._detector.RunDetection(audio)
            if result > 0:
                recorder.remove_processor(self)
                hotword = self._hotwords[result - 1]
                return hotword
