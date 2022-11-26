from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    jsonify,
    send_file,
    Response
)
import os
import sys
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    # render upload page
    uid = uuid.uuid4().hex
    return render_template('test.html',uid=uid)

@app.route('/upload', methods=['POST'])
def upload():
    print(request.files)
    f = request.files['file']
    f.save(f.filename)
    return Response("{'a':'b'}", status=201, mimetype='application/json')


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
