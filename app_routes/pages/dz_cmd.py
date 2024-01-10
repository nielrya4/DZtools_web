from flask import render_template, request
from applications import cmd


def register(app):
    @app.route('/cmd/', methods=['GET', 'POST'])
    def dz_cmd():
        output = request.form.get('output', "")
        if request.method == 'POST':
            command = request.form['command']
            command = command.strip()
            result = cmd.process_cmd(command)
            if result.startswith("text "):
                output = output + f"$ {command}\n" + result[5:] + " \n"
            elif result.startswith("page "):
                return result[5:]
        return render_template('dz_cmd/dz_cmd.html', output=output)
