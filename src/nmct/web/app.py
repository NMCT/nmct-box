from traceback import print_exception

import flask
from pathlib import Path

import nmct
import os
from flask import request, flash, redirect
from werkzeug.utils import secure_filename

from nmct.box import get_pixel_ring
from nmct.settings import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, MAX_UPLOAD_SIZE

app = flask.Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

display = nmct.box.get_display()


@app.route('/')
def show_dashboard():
    w1ids = nmct.box.list_onewire_ids()
    return flask.render_template("dashboard.html", w1ids=w1ids)


@app.route('/write_lcd', methods=['POST'])
def write_lcd():
    text = flask.request.form['lcdMessage']
    text = text.rstrip("")
    display.write(text)
    w1ids = nmct.box.list_onewire_ids()

    return flask.render_template("dashboard.html", lcdMessage=text, w1ids=w1ids)


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
        print_exception(ex, ex, ex.__traceback__)
    return flask.render_template("dashboard.html", show_method='gravity', show_text=show_text, w1ids=w1ids)


@app.route('/temperatuur', methods=['GET'])
def show_temperature():
    show_text = ""
    w1ids = nmct.box.list_onewire_ids()
    serial = flask.request.args.get('serial_number')
    if serial is None:
        return 'Gelieve een serieel nummer mee te geven : http://xxx.xxx.xxx.xxx/temperauur?serial_number=28-xxxx'
    try:
        temperatuur = nmct.box.get_thermometer(serial).measure()
        show_text = "De temperatuur is {0:3.2f} \N{DEGREE SIGN}C".format(temperatuur)
    except Exception as ex:
        print_exception(ex, ex, ex.__traceback__)

    return flask.render_template("dashboard.html", show_method='show_temperature', show_text=show_text, w1ids=w1ids)


@app.route('/student', methods=['POST', 'GET'])
def show_student():
    # http://169.254.10.11/student?number=3
    number = flask.request.args.get('number')
    if number is None:
        return 'Gelieve een studentnummer mee te geven : http://xxx.xxx.xxx.xxx/student?number=x'
    template = "student{0}.html".format(number)

    print(template)
    return flask.render_template(template)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    w1ids = nmct.box.list_onewire_ids()
    success=False
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
    return flask.render_template("dashboard.html", show_method='upload', w1ids=w1ids, upload_success=success)


@app.route('/uploads', methods=['GET'])
def show_uploads():
    p = Path(UPLOAD_FOLDER)
    return flask.render_template("uploads.html", files=[(f.name, f.owner(), f.suffix) for f in p.iterdir()])


if __name__ == '__main__':
    app.run(debug=True)