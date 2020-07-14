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
    session, flash, redirect, url_for, jsonify,
    send_file
)

import utils

import shutil
import tempfile
import weakref

class FileRemover(object):
    def __init__(self):
        self.weak_references = dict()  # weak_ref -> filepath to remove

    def cleanup_once_done(self, response, filepath):
        wr = weakref.ref(response, self._do_cleanup)
        self.weak_references[wr] = filepath

    def _do_cleanup(self, wr):
        filepath = self.weak_references[wr]
        print('Deleting %s' % filepath)
        shutil.rmtree(filepath, ignore_errors=True)


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

file_remover = FileRemover()
@app.route('/dicom_file')
def dicom_file(series_instance_uid):
    series_instance_uid = request.args.get('series_instance_uid')
    instance_number = request.args.get('instance_number')
    tempdir = tempfile.mkdtemp()
    filepath = make_the_data(dir_to_put_file_in=tempdir)
    resp = send_file(filepath)
    file_remover.cleanup_once_done(resp, tempdir)
    return resp    

@app.route('/show_surface')
def show_surface():
    img_file, surface_file= utils.get_bunny()
    print(surface_file,img_file)
    return render_template("show_surface.html",
        img_file=img_file,
        surface_file=surface_file
    )

@app.route('/show_nifti_image')
def show_nifti_image():
    series_instance_uid = request.args.get('series_instance_uid')
    base64string, img_file, mask_file = utils.get_random_nifti_image()
    print(img_file)
    return render_template("show_nifti_image.html",
        series_instance_uid=series_instance_uid,
        base64string=base64string, # just trying out this feature...
        isbase64string=False,
        img_file=img_file,
        mask_file=mask_file,
    )

@app.route('/show_dicom_image')
def show_dicom_image():
    series_instance_uid = request.args.get('series_instance_uid')
    image_list = utils.gen_random_dicom_file_list()
    return render_template("show_dicom_image.html",
        series_instance_uid=series_instance_uid,
        image_list=image_list,
    )

@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = utils.celery.AsyncResult(task_id)
    random_char = ' '+''.join(random.choice(string.ascii_lowercase) for i in range(10))
    response = {'ready': task.ready(),'task_id':task_id,'random_char':random_char}
    if task.ready():
        response["result"]=task.get()
        return jsonify(response)
    else:
        return jsonify(response)

@app.route('/long_running_task')
def long_running_task():
    start_time = time.time()
    task = utils.long_running_task.apply_async((start_time,))
    task_id = task.id
    return render_template("loading.html",task_id=task_id)

@app.route('/show_table')
def show_table():
    df = utils.get_table()
    return render_template("show_table.html",table=df.to_html(
        index=False,header="true",
        classes="display",table_id="example",border=0))
        # ^^^ override default kwags so DataTable css can take over look and feel.

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

    task = utils.celery.AsyncResult(task_id)
    print(series_instance_uid,task_id,task.ready())

    response = {'ready': task.ready(),'task_id':task_id}

    # for debugging
    if return_type == "html":

        if task.ready() is True:
            return render_template("show_results.html",results=response,)
        else: # for learning redirect html
            return render_template("loading.html",task_id=task_id)

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
