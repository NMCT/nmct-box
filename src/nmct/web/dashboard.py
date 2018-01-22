from random import randint
from traceback import print_exception

import flask
import nmct

app = flask.Flask(__name__)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
