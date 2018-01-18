import flask
from traceback import print_exception

import nmct

from src.nmct import Color

app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/dashboard')
def show_dashboard():
    return flask.render_template("index.html")


@app.route('/write_lcd', methods=['POST'])
def write_lcd():
    text = flask.request.form['lcdMessage']
    text = text.rstrip("")
    # sda en scl pin meegeven
    display = nmct.hardware.get_display()
    display.write(text)
    return flask.render_template("index.html", lcdMessage=text)


@app.route('/show_ring', methods=['GET'])
def show_ring():
    # show_method = flask.request.form['show_method']
    show_method = flask.request.args.get('show_method')
    if show_method is None:
        return "Gelieve een show_method mee te geven: /show_nmct_pixel?show_method=loop&color=(255,0,0)"

    color = flask.request.args.get('color')

    if color is None:
        color = Color(255, 0, 0)
    else:
        color = tuple([int(x) for x in color[1:-1].split(",")])
    # PixelThread.call_method(show_method)
    try:
        ring = nmct.hardware.get_pixel_ring()
        ring.queue_effect(show_method, color)
    except Exception as ex:
        # print("Exception")
        print_exception(ex, ex, ex.__traceback__)
    return flask.render_template("index.html", show_method=show_method)


@app.route('/get_axes', methods=['POST'])
def get_axes():
    # axe = request.form['show_method']
    sensor = flask.request.form['sensor']
    show_text = ""
    try:

        accelero = nmct.hardware.get_accelerometer()

        if sensor == "gravity":
            # x = accelero.get_X_axe()
            # y = accelero.get_Y_axe()
            # z = accelero.get_Z_axe()
            show_text = accelero.measure()

        if sensor == "tilt":
            tilt = accelero.tilt()
            print(tilt.roll)
            print(tilt.pitch)
            show_text = "roll: {0:5.2f}°  pitch : {1:5.2f}°".format(tilt.roll, tilt.pitch)

        print(accelero.tilt())

    except Exception as ex:
        print("Exception")
        print(ex)
    return flask.render_template("index.html", show_method='gravity', show_text=show_text)


@app.route('/student', methods=['POST', 'GET'])
def show_student():
    # http://169.254.10.11/student?number=3
    number = flask.request.args.get('number')
    if number is None:
        return 'Gelieve een studentnummer mee te geven : http://xxx.xxx.xxx.xxx/student?number=x'
    template = "student{0}.html".format(number)

    print(template)
    return flask.render_template(template)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1080, debug=True)
