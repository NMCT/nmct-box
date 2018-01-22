import os

RESOURCE_PATH = os.path.join(os.environ.get("NMCT_HOME", os.environ.get("PWD")), "resources")  # FIXME
SECRETS_PATH = os.path.join(os.environ.get("NMCT_HOME", os.environ.get("PWD")), ".secrets")
DEFAULT_MODEL = "en-US_BroadbandModel"
DEFAULT_VOICE = "en-US_AllisonVoice"

