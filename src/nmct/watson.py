import aiy.audio

from .apis.watson import WatsonConversation, _WatsonSynthesizer, _WatsonRecognizer, WatsonTranslator
from .settings import DEFAULT_MODEL, DEFAULT_VOICE

_recognizers = {}
_conversation = {}
_synthesizers = {}


def get_recognizer(model=DEFAULT_MODEL):
    global _recognizers
    _recognizers.setdefault(model, _WatsonRecognizer(model))
    return _recognizers[model]


def get_conversation(workspace_id):
    global _conversation
    _conversation.setdefault(workspace_id, WatsonConversation(workspace_id))
    return _conversation[workspace_id]


def get_synthesizer(voice=DEFAULT_VOICE):
    global _synthesizers
    _synthesizers.setdefault(voice, _WatsonSynthesizer(voice))
    return _synthesizers[voice]


def get_translator(source='en', target='es'):
    return WatsonTranslator(source, target)


def list_voices():
    return get_synthesizer(DEFAULT_VOICE).list_voices()


def list_translators():
    return get_translator().list_models()


def say(text, voice=DEFAULT_VOICE):
    synthesizer = get_synthesizer(voice)
    audio = synthesizer.synthesize(text)
    aiy.audio.get_player().play_bytes(audio, 16000)


def translate(text, source, target):
    translator = get_translator(source, target)
    return translator.translate(text)
