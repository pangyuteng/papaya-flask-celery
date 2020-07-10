import os
import json
import time
import random
import string
import tempfile
import base64

import numpy as np
import SimpleITK as sitk

from celery import Celery
from celery.result import AsyncResult
from flask import (
    Flask, request, render_template, 
    session, flash, redirect, url_for, jsonify
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "the random string"

celery_config = {
    "broker_url": os.environ["AMQP_URI"],
    "result_backend": os.environ["REDIS_URI"],
    "task_serializer": "pickle", # for passing binary objects
    "result_serializer": "pickle",
    "accept_content": ["pickle"],
}

celery = Celery(app.name, broker=celery_config["broker_url"])
celery.conf.update(celery_config)

@celery.task(bind=True)
def _get_image(self,uid):
    with tempfile.TemporaryDirectory() as tempdir:
        use_compression = False
        fpath = os.path.join(tempdir,'img.nii')
        
        # passing binary object is a bad idea since it'll blow up redis
        # check refs 19231389, 14118526 for alternatives/inspirations

        spacing = (0.6,0.6,1.8)
        origin = (0,0,1)
        direction = (0,1,0,1,0,0,0,0,1)
        arr = (np.random.rand(128,128,50)*255).astype(np.uint8)
        img = sitk.GetImageFromArray(arr)
        img.SetSpacing(spacing)
        img.SetOrigin(origin)
        img.SetDirection(direction)
        writer = sitk.ImageFileWriter()    
        writer.SetFileName(fpath)
        writer.SetUseCompression(use_compression)
        writer.Execute(img)

        with open(fpath,'rb') as f:
            binary_file_data = f.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_message = base64_encoded_data.decode('utf-8')
            return {"ext":".nii","base64string":base64_message}

@app.route('/', methods=['GET'])
def index():
    mylist = []
    for _ in range(10):
        mystatus = ' '+''.join(random.choice(string.digits+'.') for i in range(64))
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
    series_instance_uid = myinfo["series_instance_uid"]
    task_id = myinfo["task_id"]
    task = celery.AsyncResult(task_id)
    print(series_instance_uid,task_id,task.ready())
    if task.ready() is True:
        return render_template("show_image.html", 
            series_instance_uid=series_instance_uid,
            task_id=task_id,
            ext=task.get()["ext"],
            base64string=task.get()["base64string"],)
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
ref. 
flask+celery:
https://stackoverflow.com/questions/26954122/how-can-i-pass-arguments-into-redirecturl-for-of-flask/26957478
https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments
https://stackoverflow.com/questions/41956480/how-to-pass-large-chunk-of-data-to-celery/46072582#46072582
https://stackoverflow.com/questions/31866796/making-an-asynchronous-task-in-flask
passing binary object via celery:
https://stackoverflow.com/questions/14118526/how-to-serialize-binary-files-to-use-with-a-celery-task
https://stackoverflow.com/questions/19231389/celery-task-in-flask-for-uploading-and-resizing-images-and-storing-it-to-amazon
# papaya + display images:
https://github.com/vsoch/nifti-drop
https://github.com/rii-mango/Papaya/issues/32
https://github.com/rii-mango/Papaya/pull/79
# convert byte obect to base 64 encoded string
https://github.com/rii-mango/Papaya/wiki/Configuration#images
https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/
"""