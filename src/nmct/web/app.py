from traceback import print_exception

import bokeh
import flask
from pathlib import Path

from bokeh.embed import autoload_server

import nmct
import os
from flask import request, flash, redirect, send_from_directory
from werkzeug.utils import secure_filename

from nmct.box import get_pixel_ring
from nmct.settings import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, MAX_UPLOAD_SIZE

app = flask.Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

display = nmct.box.get_display()


def list_uploads():
    p = Path(app.config['UPLOAD_FOLDER'])
    return [(f.name, f.owner(), f.suffix[1:]) for f in p.iterdir()]


@app.route('/')
def show_dashboard():
    w1ids = nmct.box.list_onewire_ids()
    return flask.render_template("dashboard.html", w1ids=w1ids, files=list_uploads())


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('./static', path)


@app.route('/styles/<path:path>')
def serve_styles(path):
    return send_from_directory('./static/styles', path)


@app.route('/media/<path:path>')
def serve_media(path):
    return send_from_directory('./static/media', path)


@app.route('/write_lcd', methods=['POST'])
def write_lcd():
    text = flask.request.form['lcdMessage']
    text = text.rstrip("")
    display.write(text)
    w1ids = nmct.box.list_onewire_ids()

    return flask.render_template("dashboard.html", lcdMessage=text, w1ids=w1ids, files=list_uploads())


@app.route('/sensors', methods=['GET'])
def sensors():
    w1ids = nmct.box.list_onewire_ids()
    # axe = request.form['show_method']
    sensor = flask.request.args.get('sensor')
    show_text = ""
    try:

        accelero = nmct.box.get_accelerometer()

        if sensor == "gravity":
            show_text = accelero.measure()

        if sensor == "tilt":
            tilt = accelero.tilt()
            # print(tilt.roll)
            # print(tilt.pitch)
            show_text = "roll: {0:5.2f}\N{DEGREE SIGN} pitch : {1:5.2f}\N{DEGREE SIGN}".format(tilt.roll, tilt.pitch)

        if sensor == "temperature":
            temp = nmct.box.measure_temperature()
            show_text = "Temperature: {}\N{DEGREE SIGN}".format(temp)

        # print(accelero.tilt())

    except Exception as ex:
        return flask.render_template("error.html", exc=ex, message=ex.args)
    return flask.render_template("dashboard.html", show_method='gravity', show_text=show_text, w1ids=w1ids, files=list_uploads())


@app.route('/temperatuur', methods=['GET'])
def show_temperature():
    show_text = ""
    w1ids = nmct.box.list_onewire_ids()
    serial = flask.request.args.get('serial_number')
    if serial is None:
        error = 'Gelieve een serieel nummer mee te geven : http://xxx.xxx.xxx.xxx/temperauur?serial_number=28-xxxx'
        return flask.render_template("error.html", exc=None, message=error)
    try:
        temperatuur = nmct.box.get_thermometer(serial).measure()
        show_text = "De temperatuur is {0:3.2f} \N{DEGREE SIGN}C".format(temperatuur)
    except Exception as ex:
        return flask.render_template("error.html", exc=ex, message=ex.args)
    return flask.render_template("dashboard.html", show_method='show_temperature', show_text=show_text, w1ids=w1ids, files=list_uploads())


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    w1ids = nmct.box.list_onewire_ids()
    success = False
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
    return flask.render_template("dashboard.html", show_method='upload', w1ids=w1ids, upload_success=success, files=list_uploads())


@app.route('/uploads', methods=['GET'])
def show_uploads():
    return flask.render_template("uploads.html", files=list_uploads())


@app.route("/fplot")
def hello():
    script = bokeh.embed.autoload_server(model=None, app_path="/fplot",
                                         url=request.url.replace("/fplot", "plot/plot"))
    return flask.render_template('plot.html', bokS=script)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
