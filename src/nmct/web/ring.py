from random import randint
from traceback import print_exception

import flask

import nmct
from nmct import Palette
from nmct.box import get_pixel_ring

app = flask.Flask(__name__)
ring = nmct.box.get_pixel_ring()


@app.route('/ring', methods=['GET'])
def neopixel():
    return flask.render_template("ring.html", palette=list(Palette))


@app.route('/ring/animation', methods=['POST'])
def show_animation():
    animation = flask.request.form['animation']
    color = flask.request.form['color']
    rgb = flask.request.form['rgb']
    red = flask.request.form['red']
    green = flask.request.form['green']
    blue = flask.request.form['blue']

    if animation is None:
        error = "Gelieve een animation mee te geven: /show_nmct_pixel?animation=loop&color=(255,0,0)"
        return flask.render_template("error.html", exc=None, message=error)

    from nmct import Color
    # if color is None:
    print(color)
    if rgb:
        color = Color.by_name(color)# Color(*[int(x) for x in color[1:-1].split(",")])
    else:
        color = Color(red, green, blue)  # *[randint(0, 255) for x in range(3)]
    try:
        ring.queue_animation(animation, color)
    except Exception as ex:
        print_exception(ex, ex, ex.__traceback__)
        return flask.render_template("error.html", exc=ex, message=ex.args)

    return flask.render_template("ring.html", animation=animation, color=color, palette=list(Palette))


if __name__ == '__main__':
    # ring = get_pixel_ring()
    app.run(debug=True)
