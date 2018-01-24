from pathlib import Path

import flask
from flask import send_from_directory

app = flask.Flask(__name__, template_folder='/home/nmct/uploads')


@app.route('/student', methods=['GET'])
def show_student():
    # http://169.254.10.11/student?number=3
    # number = flask.request.args.get('number')
    template = flask.request.args.get('template')
    # if number is None:
    #     error = 'Gelieve een studentnummer mee te geven : http://xxx.xxx.xxx.xxx/student?number=x'
    #     return flask.render_template("error.html", exc=None, message=error)

    # template = "student{0}.html".format(number)
    # print(template)
    return flask.render_template(template)


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('./static', path)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3005, debug=True)
