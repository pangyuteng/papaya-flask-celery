from gevent import monkey
monkey.patch_all() # we need to patch very early

import os
import sys
import json
import time
import random
import string

from flask import (
    Flask, request, render_template, 
    session, flash, redirect, url_for, jsonify
)

import utils

app = Flask(__name__,
    static_url_path='', 
    static_folder='static',
    template_folder='templates',
)

app.config["SECRET_KEY"] = "the random string"

def gen_random(num):
    mylist = []
    for _ in range(10):
        mylist.append(' '+''.join(random.choice(string.ascii_letters) for i in range(32)))
    return mylist

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',mylist=gen_random(10))

@app.route('/image/<series_instance_uid>')
def image(series_instance_uid):
    # TODO: provide api to get nifti object - base64 encoded string
    raise NotImplementedError()

@app.route('/show_nifti_image')
def show_nifti_image():
    series_instance_uid = request.args.get('series_instance_uid')
    base64string = utils.get_random_nifti_image_as_base64string()
    return render_template("show_nifti_image.html",
            series_instance_uid=series_instance_uid,
            base64string=base64string,
    )


@app.route('/show_dicom_image')
def show_dicom_image():
    series_instance_uid = request.args.get('series_instance_uid')
    image_list = utils.gen_random_dicom_file_list()
    return render_template("show_dicom_image.html",
            series_instance_uid=series_instance_uid,
            image_list=image_list,
    )

@app.route('/taskstatus/<task_id>')
def taskstatus(task_id):
    task = celery.AsyncResult(task_id)
    response = {'ready': task.ready(),'task_id':task_id}
    if task.ready():
        response["result"]=task.get()
        return jsonify(response)
    else:
        return jsonify(response)

@app.route('/segment')
def segment():
    raise NotImplementedError()
    series_instance_uid = request.args.get('series_instance_uid')
    model_id = request.args.get('model_id')
    foo = request.args.get('foo',None)
    task_id = request.args.get('task_id',None)
    return_type = request.args.get('return_type',"html")

    if task_id is None:
        task = utils.segment(series_instance_uid,model_id,foo=foo)
        print(series_instance_uid,task_id,task.ready())
        return redirect(url_for('segment',
            series_instance_uid = series_instance_uid,
            model_id = model_id,
            foo = foo,
            task_id = task.id,
        ))

    task = celery.AsyncResult(task_id)
    print(series_instance_uid,task_id,task.ready())

    response = {'ready': task.ready(),'task_id':task_id}

    # for debugging
    if return_type == "html":

        if task.ready() is True:
            return render_template("show_results.html", 
                series_instance_uid=series_instance_uid,
                task_id=task_id,
            )
        else: # for learning redirect html
            time.sleep(1) # TODO: sleep should be at client side
            status = ' '+''.join(random.choice(string.ascii_lowercase) for i in range(10))
            return render_template("loading.html",
                series_instance_uid=series_instance_uid,
                task_id=task_id,
                status=status,
            )

    else:
        if task.ready() is True:
            try:
                response["result"]=task.get()
            except:
                return jsonify(response)
            return jsonify(response)
        else:
            return jsonify(response)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port",type=int,default=5000)
    args = parser.parse_args()
    app.run(debug=True,host="0.0.0.0",port=args.port)
