import os
import json
import time
import random
import string
import tempfile

import numpy as np
import SimpleITK as sitk

from celery import Celery
from celery.result import AsyncResult
from flask import (
    Flask, request, render_template, 
    session, flash, redirect, url_for, jsonify
)

app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = os.environ["AMQP_URI"]
app.config["CELERY_RESULT_BACKEND"] = os.environ["REDIS_URI"]
app.config["SECRET_KEY"] = "the random string"

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

@celery.task(bind=True)
def _get_image(self,uid):
    #time.sleep(10)
    #return f"THIS IS THE RESULT {uid}"

    with tempfile.TemporaryDirectory() as tempdir:
        spacing = (0.6,0.6,1.8)
        origin = (0,0,1)
        direction = (0,1,0,1,0,0,0,0,1)
        use_compression = False
        fpath = os.path.join(tempdir,'img.nii')
        arr = (np.random.rand(256,256,10)*255).astype(np.uint8)
        img = sitk.GetImageFromArray(arr)
        img.SetSpacing(spacing)
        img.SetOrigin(origin)
        img.SetDirection(direction)
        writer = sitk.ImageFileWriter()    
        writer.SetFileName(fpath)
        writer.SetUseCompression(use_compression)
        writer.Execute(img)

        with open(fpath,'rb') as f:
            return f.read()

@app.route('/', methods=['GET'])
def index():
    mylist = []
    for _ in range(10):
        mystatus = ' '+''.join(random.choice(string.ascii_lowercase) for i in range(10))
        mylist.append(mystatus)
    return render_template('index.html',mylist=mylist)

@app.route('/taskstatus/<task_id>')
def taskstatus(task_id):
    task = celery.AsyncResult(task_id)
    response = {'ready': task.ready(),'task_id':task_id}
    if task.ready():
        response["result"]=task.get()
        return jsonify(response)
    else:
        return jsonify(response)

@app.route('/image/<series_instance_uid>')
def image(series_instance_uid):
    print('series_instance_uid',series_instance_uid)
    task = _get_image.apply_async(args=[series_instance_uid])
    myinfo = json.dumps({"task_id":task.id,"series_instance_uid":series_instance_uid})
    session['myinfo'] = myinfo
    return redirect(url_for('show_image',myinfo=myinfo))

@app.route('/get_image/<series_instance_uid>')
def get_image(series_instance_uid):
    print('series_instance_uid',series_instance_uid)
    task = _get_image.apply_async(args=[series_instance_uid])
    myinfo = json.dumps({"task_id":task.id,"series_instance_uid":series_instance_uid})
    session['myinfo'] = myinfo
    return redirect(url_for('show_image',myinfo=myinfo))

@app.route('/show_image')
def show_image():
    myinfo = session['myinfo']       # counterpart for session
    myinfo = json.loads(myinfo)
    print(myinfo)
    series_instance_uid = myinfo["series_instance_uid"]
    task_id = myinfo["task_id"]
    task = celery.AsyncResult(task_id)
    print(series_instance_uid,task_id,task.ready())
    if task.ready() is True:
        return render_template("show_image.html", series_instance_uid=series_instance_uid,task_id=task_id,mydata=task.get())
    else:
        time.sleep(1)
        status = ' '+''.join(random.choice(string.ascii_lowercase) for i in range(10))
        return render_template("loading.html", series_instance_uid=series_instance_uid,task_id=task_id,status=status)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port",type=int,default=5000)
    args = parser.parse_args()
    app.run(debug=True,host="0.0.0.0",port=args.port)

"""
https://stackoverflow.com/questions/26954122/how-can-i-pass-arguments-into-redirecturl-for-of-flask/26957478
https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments
"""