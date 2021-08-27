import os
import traceback
import shutil
import tempfile
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import uuid
import flask

app = Flask(__name__)

@app.route('/')
def index():
    # render upload page
    uid = uuid.uuid4().hex
    return render_template('upload.html',uid=uid)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    uid = request.args.get('uid')
    tempdir = os.path.join('/tmp',uid)
    os.makedirs(tempdir,exist_ok=True)
    if request.method == 'POST':
        csv_list = []
        myfile = request.files.getlist('file')
        for f in myfile:
            file_path = os.path.join(tempdir, f.filename)
            f.save(file_path)
    return "ok"

@app.route('/completed')
def completed():
    uid = request.args.get('uid')
    tempdir = os.path.join('/tmp',uid)
    df_list = []

    if os.path.exists(tempdir):
        for basename in os.listdir(tempdir):
            file_path = os.path.join(tempdir,basename)
            if not file_path.endswith('.csv'):
                continue
            df = pd.read_csv(file_path)
            df_list.append(df)

    try:
        shutil.rmtree(tempdir)
        delete_success = True
    except:
        traceback.print_exc()
        delete_success = False
        
    return render_template('completed.html',uid=uid,df_list=df_list,delete_success=delete_success)

@app.route('/ping')
def ping():
    return jsonify({'status':'pong'})

# testing for sagemaker post to accept different content type.
@app.route('/invocations', methods=['POST'])
def transformation():
    data = None
    result = {'content_type':flask.request.content_type}
    print(flask.request.content_type)
    if flask.request.content_type == 'application/json':
        data_dict = flask.request.get_json()
        return flask.Response(response=data_dict, status=200, mimetype='application/json')
    elif flask.request.content_type.startswith('multipart/form-data'):
        txtcontent = ''
        with tempfile.TemporaryDirectory() as tempdir:
            print(request.files.to_dict())
            myfile = request.files.getlist('files')
            for f in myfile:
                file_path = os.path.join(tempdir, f.filename)
                f.save(file_path)
                with open(file_path,'r') as f:
                    tmp = f.read()
                    txtcontent+=tmp
            return jsonify({'content':txtcontent})

    else:
        return flask.Response(response='This predictor only supports application/json or files via multipart/form-data', status=415, mimetype='text/plain')        

"""
curl localhost:5000/ping
curl -X POST --header "Content-Type: application/json" --data '{"username":"xyz","password":"xyz"}' localhost:5000/invocations

echo okdude >> myfile.txt
echo okbud >> myotherfile.txt
curl -F "files=@myfile.txt" localhost:5000/invocations
curl -F "files=@myfile.txt" -F "files=@myotherfile.txt" localhost:5000/invocations

helpful
https://gist.github.com/subfuzion/08c5d85437d5d4f00e58
https://stackoverflow.com/questions/12667797/using-curl-to-upload-post-data-with-files

"""

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, debug=True)
