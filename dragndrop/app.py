import os
import traceback
import shutil
import tempfile
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import uuid

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

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, debug=True)
