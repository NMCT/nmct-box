from pathlib import Path

from .app import *



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3006, debug=True)