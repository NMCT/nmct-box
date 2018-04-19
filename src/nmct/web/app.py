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
tts = nmct.watson.get_synthesizer()


def default_values():
    return {
        'uploads': list_uploads(),
        'w1ids': nmct.box.list_onewire_ids(),
        'voices': tts.list_voices()
    }


def list_uploads():
    p = Path(app.config['UPLOAD_FOLDER'])
    return [(f.name, f.owner(), f.suffix[1:]) for f in p.iterdir() if f.is_file()]


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('./static', path)


@app.route('/styles/<path:path>')
def serve_styles(path):
    return send_from_directory('./static/styles', path)


@app.route('/media/<path:path>')
def serve_media(path):
    return send_from_directory('./static/media', path)


@app.route('/')
@app.route('/dashboard/', methods=['GET'])
def show_dashboard():
    try:
        defaults = default_values()
    except Exception as ex:
        return flask.render_template("error.html", exc=ex, message=ex.args)
    return flask.render_template("dashboard.html", showmethod='write_lcd', **defaults)


@app.route('/write_lcd', methods=['POST', 'GET'])
def write_lcd():
    display.clear()
    if flask.request.method == 'POST':
        text = flask.request.form.get('lcdMessage')
    else:
        text = flask.request.args.get('lcdMessage')
    if text is None:
        error = 'Gelieve een tekst mee te geven: http://xxx.xxx.xxx.xxx/write_lcd?lcdMessage=hallo'
        return flask.render_template("error.html", exc=None, message=error)
    text = text.rstrip("")
    display.write(text)
    return flask.render_template("dashboard.html", showmethod='write_lcd', lcdMessage=text, **default_values())


@app.route('/speak', methods=['POST', 'GET'])
def tts_speak():
    text = flask.request.form.get('tts_text')
    voice = flask.request.form.get('tts_voice')
    watson = nmct.watson.get_synthesizer(voice)
    watson.say(text)
    return flask.render_template("dashboard.html", tts_text=text, tts_voice=voice, **default_values())


@app.route('/sensors', methods=['GET'])
def sensors():
    w1ids = nmct.box.list_onewire_ids()
    # axe = request.form['show_method']
    sensor = flask.request.args.get('sensor')
    show_text = ""
    try:

        accelero = nmct.box.get_accelerometer()
        accelero.measure()

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
    return flask.render_template("dashboard.html", show_method='gravity', show_text=show_text, **default_values())


@app.route('/temperatuur', methods=['GET'])
def show_temperature():
    show_text = ""
    w1ids = nmct.box.list_onewire_ids()
    serial = flask.request.args.get('serial_number')
    if serial is None:
        error = 'Gelieve een serienummer mee te geven: http://xxx.xxx.xxx.xxx/temperauur?serial_number=28-xxxx'
        return flask.render_template("error.html", exc=None, message=error)
    try:
        temperatuur = nmct.box.get_thermometer(serial).measure()
        show_text = "De temperatuur is {0:3.2f} \N{DEGREE SIGN}C".format(temperatuur)
    except Exception as ex:
        return flask.render_template("error.html", exc=ex, message=ex.args)
    return flask.render_template("dashboard.html", show_method='show_temperature', show_text=show_text,
                                 **default_values())


def file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def allowed_file(filename):
    return '.' in filename and file_extension(filename) in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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
        if file:
            filename = secure_filename(file.filename)
            if not allowed_file(filename):
                return flask.render_template("error.html", exc=None, message="File type not allowed for upload")
            if file_extension(filename) in ['html', 'htm']:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'static', filename))

            success = True
    return flask.render_template("dashboard.html", show_method='upload', upload_success=success, **default_values())


@app.route('/uploads', methods=['GET'])
def show_uploads():
    return flask.render_template("uploads.html", files=list_uploads())


@app.route("/live_plot")
def live_plot():
    script = bokeh.embed.server_document(request.url.replace("live_plot", "plot/plot"), True)
    return flask.render_template('plot.html', bokeh_script=script)


#
# @app.errorhandler(500)
# def page_not_found(e):
#     return flask.render_template('error.html', exc=e, message=e.message)
#
#
# @app.errorhandler(404)
# def page_not_found(e):
#     return flask.render_template('error.html', exc=e, message=e.message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
