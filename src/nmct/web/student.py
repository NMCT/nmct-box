from pathlib import Path

import flask

app = flask.Flask(__name__, template_folder='/home/nmct/uploads')


@app.route('/student', methods=['POST', 'GET'])
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


if __name__ == '__main__':
    app.run(debug=True)
