from random import randint
from traceback import print_exception

import flask

import nmct
from nmct import Palette

ledapp = flask.Flask(__name__)
ring = nmct.box.get_pixel_ring()


@ledapp.route('/', methods=['POST'])
def neopixel():
    effect = flask.request.form['effect']
    color = flask.request.form['color']
    red = flask.request.form['red']
    green = flask.request.form['green']
    blue = flask.request.form['blue']

    if effect is None:
        error = "Gelieve een effect mee te geven: /show_nmct_pixel?effect=loop&color=(255,0,0)"
        return flask.render_template("error.html", exc=None, message=error)

    from nmct import Color
    if color is None:
        color = Color(red, green, blue)     # *[randint(0, 255) for x in range(3)]
    else:
        color = Color(*[int(x) for x in color[1:-1].split(",")])

    try:
        ring.queue_effect(effect, color)
    except Exception as ex:
        print_exception(ex, ex, ex.__traceback__)
        return flask.render_template("error.html", exc=ex, message=ex.message)

    return flask.render_template("neopixel.html", effect=effect, color=color, palette=list(Palette))


if __name__ == '__main__':
    ledapp.run(host='0.0.0.0', port=3005, debug=True)
