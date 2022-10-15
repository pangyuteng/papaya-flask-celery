
import argparse
import sys,os

from flask_cors import CORS
from flask import (
    Flask, request, render_template, Response,
    session, flash, redirect, url_for, jsonify,
    send_file
)

app = Flask(__name__)
app.config['TESTING'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = "the random string"
CORS(app)

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/ping')
def ping():
    response = jsonify({"foo":"pong"})
    return response

@app.route('/myfunc', methods=['GET', 'POST'])
def myfunc():
    app.logger.info(f'{request.json}!!!!!')
    uid = int(request.json.get('uid'))
    value = request.json.get('accepted',None)
    if request.method == 'GET':
        return jsonify({"foo":f"get {uid} {value}"})
    if request.method == 'POST':
        return jsonify({"foo":f"post {uid} {value}"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-host',type=str,default='0.0.0.0')
    parser.add_argument('-port',type=int,default='5555')
    parser.add_argument('-d','--debug',action='store_true')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port,debug=args.debug)

'''

curl -k  \
    --header "Content-Type: application/json" \
    --request POST  \
    --data '{"myfunc,"accepted":true,"uid":123}' \
    https://xxx/myfunc

curl -k  \
    --header "Content-Type: application/json" \
    --request GET  \
    --data '{"uid":123,"accepted":true}' \
    https://xxx/myfunc
    
'''