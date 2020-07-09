import os
import time
import random
import string
import datetime
import pytz
from celery import Celery
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

"""
@celery.task(bind=True)
def celery_get_image(self,uid):
    return get_image(uid)

def get_image(uid):
    return True

@app.route('/get_image/<series_instance_uid>', methods=['GET'])
def get_image():
    return render_template('index.html')
"""

@celery.task(bind=True)
def _get_image(self,uid):
    time.sleep(10)
    return f"THIS IS THE RESULT {uid}"

@app.route('/', methods=['GET'])
def index():
    mylist = []
    for _ in range(10):
        mystatus = ' '+''.join(random.choice(string.ascii_lowercase) for i in range(10))
        mylist.append(mystatus)
    return render_template('index.html',mylist=mylist)

@app.route('/get_image/<series_instance_uid>', methods=['GET'])
def get_image(series_instance_uid):
    series_instance_uid = request.args.get('series_instance_uid')
    task = _get_image.apply_async(args=[series_instance_uid])
    session['task_id'] = task.id
    session['series_instance_uid'] = series_instance_uid
    return redirect(url_for('loading'))

@app.route('/show_image')
def loading():
    task_id = session.get('task_id',None)
    series_instance_uid = session.get('series_instance_uid',None)
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