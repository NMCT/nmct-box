import asyncio
import json
import logging
from urllib.parse import urlparse

import aiy.audio
from autobahn.asyncio import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.websocket.util import create_url
from watson_developer_cloud import AuthorizationV1, ConversationV1, TextToSpeechV1, LanguageTranslatorV2, SpeechToTextV1

log = logging.getLogger("Watson")


class AuthenticationError(Exception):
    pass


class ServiceCredential(object):
    def __init__(self, name, secrets="../../.secret/credentials.json"):  # TODO: path
        try:
            with open(secrets) as f:
                self.data = json.load(f)["watson"][name]
                self.authorization = AuthorizationV1(**self.data)
                self.url = self.data["url"]
        except IOError:
            raise AuthenticationError("Failed to open secrets file")
        except KeyError:
            raise AuthenticationError("No credentials found for {}".format(name))

    def get_token(self):
        return self.authorization.get_token(self.url)

    def get_header(self):
        return {"X-Watson-Authorization-Token": self.get_token()}


class WatsonSpeechToTextClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        super().__init__()
        self.options = {
            "content_type": "audio/l16;rate=16000;channels=1",  # TODO: dynamic audio format
            "interim_results": True,
            "inactivity_timeout": None,
            "word_confidence": None,
            "timestamps": None,
            "max_alternatives": None,
            "word_alternatives_threshold": None,
            "profanity_filter": False,
            "smart_formatting": None,
            "keywords": None,
            "keywords_threshold": None,
            "speaker_labels": None
        }

    async def onConnect(self, response):
        log.debug("WebSocket connected: {}".format(response))

    async def onOpen(self):
        log.debug("WebSocket opened")

        self.sendMessage(
            json.dumps(
                {k: v for k, v in self.options.items() if v is not None}
            ).encode('utf-8')
        )

        while True:
            audio = await self.factory.audio_queue.get()
            self.sendMessage(audio, isBinary=True)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            res = json.loads(payload.decode('utf8'))
            log.debug("Result received: {}".format(res))
            if "results" in res:
                transcript = res["results"][0]["alternatives"][0]["transcript"]
                if res["results"][0]["final"]:
                    aiy.audio.get_recorder().remove_processor(self.factory)
                    self.sendMessage(json.dumps({'action': 'stop'}).encode('utf-8'))
                    self.sendClose(1000)
                    if callable(self.factory.final_cb):
                        self.factory.final_cb(transcript)
                    self.factory.transcript.set_result(transcript)
                else:
                    if callable(self.factory.partial_cb):
                        self.factory.partial_cb(transcript)

    def onClose(self, wasClean, code, reason):
        if reason:
            log.debug("WebSocket closed ({}): {} - {}".format(wasClean, code, reason))


class WatsonClientFactory(WebSocketClientFactory):
    def __init__(self, service, version, method, params=None, *args, **kwargs):
        auth = ServiceCredential(service)

        headers = kwargs.pop("headers", {})
        headers.update(auth.get_header())
        kwargs["headers"] = headers

        urlparts = urlparse(auth.url)
        self.host = urlparts.netloc
        path = "/".join([urlparts.path, version, method])
        url = create_url(hostname=urlparts.netloc, isSecure=True, path=path, params=params)
        kwargs["url"] = url
        super().__init__(*args, **kwargs)


class WatsonSpeechToTextClientFactory(WatsonClientFactory):
    def __init__(self, model, partial_cb=None, final_cb=None, *args, **kwargs):
        super().__init__("speech-to-text", "v1", "recognize", {'model': model}, *args, **kwargs)
        self.audio_queue = asyncio.Queue()
        self.protocol = WatsonSpeechToTextClientProtocol
        self.transcript = asyncio.Future()
        self.partial_cb = partial_cb
        self.final_cb = final_cb

    def add_data(self, data):
        asyncio.run_coroutine_threadsafe(self.audio_queue.put(data), self.loop)


class _WatsonRecognizer(object):
    def __init__(self, model="en-US_BroadbandModel"):
        self.model = model
        self.client = SpeechToTextV1(**ServiceCredential('speech-to-text').data)
        self.recognition_result = None

    def recognize(self, partial_cb=None, final_cb=None):
        log.debug("Recognition start")
        loop = asyncio.get_event_loop()
        factory = WatsonSpeechToTextClientFactory(model=self.model, partial_cb=partial_cb, final_cb=final_cb, loop=loop)
        aiy.audio.get_recorder().add_processor(factory)
        coro = loop.create_connection(factory, factory.host, 443, ssl=True)
        loop.run_until_complete(coro)
        loop.run_until_complete(factory.transcript)
        return factory.transcript.result()

    def list_models(self):
        return self.client.models()
        # return [(v["name"], v["description"]) for v in self.client.list_models()["models"]]


class WatsonConversation(object):
    def __init__(self, workspace_id):
        print('init\n\n')

        self.workspace_id = workspace_id
        auth = ServiceCredential("conversation")
        self.client = ConversationV1(version="2017-05-26", **auth.data)
        self.context = {}
        self._finished = False

    def message(self, text):
        response = self.client.message(self.workspace_id, {'text': text}, context=self.context)
        # if "output" in response:
        #     if "text" in response["output"]:
        #         self.on_answer.fire(response["output"]["text"][0])
        #     if "action" in response["output"]:
        #         self.on_action(response["output"]["action"])
        # if "intents" in response:
        #     for intent in response["intents"]:
        #         self.on_intent(intent["intent"], intent["confidence"])
        if "context" in response:
            self.context = response["context"]
        return [i["intent"] for i in response.get("intents")], response.get("entities"), response.get("output")

    def finish(self):
        self.context = {}
        self._finished = True

    @property
    def finished(self):
        return self._finished  # TODO!


class WatsonTextToSpeechClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        super().__init__()
        self._audio = b""

    async def onConnect(self, response):
        log.debug("WebSocket connected: {}".format(response))

    async def onOpen(self):
        log.debug("WebSocket opened")

        self.sendMessage(
            json.dumps(
                {'text': self.factory.text, 'accept': 'audio/l16;rate=16000 '}
            ).encode('utf-8')
        )

    def onMessage(self, payload, isBinary):
        if isBinary:
            log.debug("Result received: {} bytes".format(len(payload)))
            if self.factory.audio.done():
                return
            if len(payload) > 0:
                self._audio += payload
            else:
                self.factory.audio.set_result(self._audio)

        else:
            log.debug("Result received: {} ".format(payload))

    def onClose(self, wasClean, code, reason):
        log.debug("TTS WebSocket closed ({}): {} - {}".format(wasClean, code, reason))


class WatsonTextToSpeechClientFactory(WatsonClientFactory):
    def __init__(self, voice, text, *args, **kwargs):
        super().__init__("text-to-speech", "v1", "synthesize", {'voice': voice}, *args, **kwargs)
        self.protocol = WatsonTextToSpeechClientProtocol
        self.text = text
        self.audio = asyncio.Future()


class _WatsonSynthesizer:
    def __init__(self, voice):
        self.voice = voice
        self.client = TextToSpeechV1(**ServiceCredential('text-to-speech').data)

    def synthesize(self, text):
        log.debug("Synthesis start")
        loop = asyncio.get_event_loop()
        factory = WatsonTextToSpeechClientFactory(voice=self.voice, text=text, loop=loop)
        coro = loop.create_connection(factory, factory.host, 443, ssl=True)
        loop.run_until_complete(coro)
        loop.run_until_complete(factory.audio)
        return factory.audio.result()

    def list_voices(self):
        return [v["name"] for v in self.client.voices()["voices"]]

    def get_voice(self, name):
        return [v for v in self.client.voices()["voices"] if v["name"] == name][0]

    def say(self, text):
        audio = self.synthesize(text)
        aiy.audio.get_player().play_bytes(audio, 16000)


class WatsonTranslator:
    def __init__(self, source='en', target='es'):
        self.client = LanguageTranslatorV2(**ServiceCredential('translator').data)
        self.source = source
        self.target = target
        self.model = None

    def list_models(self):
        # return self.client.list_models()["models"]
        return [(v["model_id"], v["source"], v["target"]) for v in self.client.list_models()["models"]]

    def translate(self, text):
        return self.client.translate(text, self.model, self.source, self.target)["translations"][0]

    def set_model(self, model):
        self.model, self.source, self.target = [m for m in self.list_models() if m[0] == model][0]
