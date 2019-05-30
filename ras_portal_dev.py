import json
import os
import subprocess
import logging
import requests

from collections import OrderedDict

from flask import Flask, flash, render_template, request, session
from dicts.tz_dic import tz_dic

_logger = logging.getLogger(__name__)

app = Flask(__name__)

WORK_DIR = '/home/hveficent/Eficent/RASv2/ras/'


def get_ip():
    _logger.debug("Getting IP")
    command = "hostname -I | awk '{ print $1}' "

    ip_address = (
        subprocess.check_output(command, shell=True)
        .decode("utf-8")
        .strip("\n")
    )

    return ip_address

@app.route("/")
def form():
    _logger.debug("inside form")
    tz_sorted = OrderedDict(sorted(tz_dic.items()))
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        return render_template(
            "form.html", IP=str(get_ip()), port=3000, tz_dic=tz_sorted
        )


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        results = request.form
        result_dic = results.to_dict(flat=False)
        if result_dic['mode'] == 'iot':
            result = json.loads(requests.post(
                result_dic['odoo_link'][0],
                data={
                    'template': 'eficent.ras',
                },
            ).content.decode('utf-8'))
            result_dic.append({
                'user_name': [result['inputs']['rfid_read']['serial']],
                'user_password': [result['inputs']['rfid_read']['passphrase']],
            })
        with open(os.path.abspath(
                os.path.join(WORK_DIR, 'dicts/data.json')), 'w+') as outfile:
            json.dump(result_dic, outfile)
        return render_template("result.html", result=results)


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form.get('Reset credentials') == 'Reset credentials':
        return render_template('change.html')
    elif request.form.get('Log in') == 'Log in':
        json_file = open(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/credentials.json')))
        json_data = json.load(json_file)
        json_file.close()
        if request.form['password'] == json_data['new password'][0] and \
                request.form['username'] == json_data['username'][0]:
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return form()
    else:
        return form()


@app.route('/change', methods=['POST', 'GET'])
def change_credentials():
    if request.method == 'POST':
        results = request.form
        dic = results.to_dict(flat=False)
        json_file = open(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/credentials.json')))
        json_data = json.load(json_file)
        json_file.close()
        if str(dic['old password'][0]) == json_data['new password'][0] and str(
                dic['username'][0]) == json_data['username'][0]:
            with open(os.path.abspath(
                    os.path.join(WORK_DIR, 'dicts/credentials.json')),
                    'w+') as outfile:
                json.dump(dic, outfile)
        else:
            flash('wrong password!')

        return form()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host=str(get_ip()), port=3000, debug=False)