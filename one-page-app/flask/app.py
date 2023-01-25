import argparse
import sys
import os
import ast
import datetime
import time
import json
import traceback
import yaml
import subprocess
import logging
import requests
import tempfile
import pathlib
import pandas as pd
import redis
import flask
from flask import (
    Flask, flash, render_template, request, redirect, url_for,
    send_file, jsonify,
)

from utils import (
    get_queue_status,
    get_job_status,
    myjob,
)
from celery import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(THIS_DIR,'config.yml')
with open(config_path, 'r') as f:
    mycfg = yaml.safe_load(f.read())

app = Flask(__name__,
    static_url_path='', 
    static_folder='static',
    template_folder='templates',
)

@app.route('/ping')
def ping():
    logger.debug("ping")
    return jsonify({'message':'pong'})

@app.route('/')
def home():

    queue_status = get_queue_status()
    job_status = get_job_status()

    return render_template('home.html',
        queue_status=queue_status,job_status=job_status)

@app.route('/task-id')
def get_task_id():
    if request.method == "GET":
        return jsonify({"task_id":uuid()})

@app.route('/submit', methods=['POST'])
def submit():
    info_dict = request.get_json()
    task_id=uuid()
    info_dict['task_id']=task_id

    workdir=f'/shared/{task_id}'
    os.makedirs(workdir,exist_ok=True)

    queue_file = os.path.join(workdir,'.queued')
    pathlib.Path(queue_file).touch()

    app.logger.debug(info_dict)
    myjob.apply_async(args=[info_dict],task_id=task_id)
    return jsonify({'message':task_id})

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=5000)
    parser.add_argument('-d','--debug',type=str,default='False')

    parser.add_argument('-l','--loglevel', type=str, default='DEBUG', 
        choices=['DEBUG','INFO','WARNING','ERROR'])
    parser.add_argument('-f','--logdir', type=str, default=None)
    args = parser.parse_args()
    port = args.port
    debug = ast.literal_eval(args.debug)
    loglevel = args.loglevel
    logdir = args.logdir

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.getLevelName(loglevel))
    stream_ch = logging.StreamHandler()
    stream_ch.setLevel(getattr(logging, loglevel))
    stream_ch.setFormatter(formatter)
    logger.addHandler(stream_ch)
    if logdir:
        os.makedirs(logdir,exist_ok=True)
        filename = os.path.join(logdir,'myflask.log')
        file_ch = logging.FileHandler(filename)
        file_ch.setLevel(getattr(logging, loglevel))
        file_ch.setFormatter(formatter)
        logger.addHandler(file_ch)
    app.run(host="0.0.0.0", port=port, debug=debug)
