from traceback import print_exception

import flask

import nmct

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


@app.route('/show_ring', methods=['POST'])
def show_ring():
    show_method = flask.request.form['show_method']
    # PixelThread.call_method(show_method)
    try:
        ring = nmct.hardware.get_pixel_ring()
        ring.queue_effect(show_method)
    except Exception as ex:
        # print("Exception")
        print_exception(ex, ex, ex.__traceback__)
    return flask.render_template("index.html", show_method=show_method)


@app.route('/get_axes')
def get_axes():
    # axe = request.form['show_method']
    try:
        print("axe")
        accelero = nmct.hardware.get_accelerometer()
        print(accelero.measure())
        # x = accelero.get_X_axe()
        # y = accelero.get_Y_axe()
        # z = accelero.get_Z_axe()
        # print(x)
        # print(y)
        # print(z)

    except Exception as ex:
        print("Exception")
        print(ex)
    return flask.render_template("index.html", show_method='axe')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)