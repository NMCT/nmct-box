from random import randint
from traceback import print_exception

import flask
from flask import send_from_directory

import nmct
from nmct import Palette
from nmct.box import get_pixel_ring

app = flask.Flask(__name__)
ring = nmct.box.get_pixel_ring()
animations = sorted([(func.__name__, func.__name__.replace('_', ' ').capitalize()) for func in ring.list_animations()])
palette = list(Palette)


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('./static', path)


@app.route('/styles/<path:path>')
def serve_styles(path):
    return send_from_directory('./static/styles', path)


@app.route('/media/<path:path>')
def serve_media(path):
    return send_from_directory('./static/media', path)


@app.route('/ring', methods=['GET'])
def neopixel():
    return flask.render_template("ring.html", palette=list(Palette), animations=animations)


@app.route('/ring/animation', methods=['POST', 'GET'])
def show_animation():
    if flask.request.method == 'GET':
        params = flask.request.args
    elif flask.request.method == 'POST':
        params = flask.request.form
    else:
        message = "Unsupported method: {}".format(flask.request.method)
        return flask.render_template("error.html", exc=None, message=message)
    animation = params.get('animation')
    color = params.get('color')
    rgb = bool(params.get('rgbvalues'))
    red = int(params.get('red', 0))
    green = int(params.get('green', 0))
    blue = int(params.get('blue', 0))

    if animation is None:
        error = "Gelieve een animation mee te geven: /show_nmct_pixel?animation=loop&color=(255,0,0)"
        return flask.render_template("error.html", exc=None, message=error)

    from nmct import Color
    # if color is None:
    print("Input: {}, rgb: {}".format(color, rgb))
    if rgb:
        print("True")
        color = Color(red, green, blue)  # *[randint(0, 255) for x in range(3)]
    else:
        print("False")
        color = Color.by_name(color)  # Color(*[int(x) for x in color[1:-1].split(",")])
    print("Output: {}, rgb: {}".format(color, rgb))
    try:
        ring.queue_animation(animation, color)
    except Exception as ex:
        print_exception(ex, ex, ex.__traceback__)
        return flask.render_template("error.html", exc=ex, message=ex.args[0])

    return flask.render_template("ring.html", animation=animation, color=color, palette=palette,
                                 animations=animations, rgbvalues=rgb)


if __name__ == '__main__':
    # ring = get_pixel_ring()
    app.run(host="0.0.0.0", port=3002, debug=True)
