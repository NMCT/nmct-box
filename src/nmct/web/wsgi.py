from nmct.web import app
from nmct.hardware import get_pixel_ring

if __name__ == "__main__":
    ring = get_pixel_ring()
    app.run()
