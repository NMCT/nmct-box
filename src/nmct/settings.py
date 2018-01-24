import os
# Watson
SECRETS_PATH = os.path.join(os.environ.get("NMCT_HOME", os.environ.get("PWD")), ".secret")
DEFAULT_MODEL = "en-US_BroadbandModel"
DEFAULT_VOICE = "en-US_AllisonVoice"

# File upload
ALLOWED_EXTENSIONS = {'htm', 'html', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'css'}
UPLOAD_FOLDER = '/home/nmct/uploads'
MAX_UPLOAD_SIZE = 1 * 1024 * 1024

#
RESOURCE_PATH = os.path.join(os.environ.get("NMCT_HOME", os.environ.get("PWD")), "resources")  # FIXME?
