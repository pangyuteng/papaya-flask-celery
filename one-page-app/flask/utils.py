import logging
logger = logging.getLogger(__file__)
import sys
import os
import datetime
import time
import json
import shutil
import traceback
import csv
import yaml
import subprocess
import requests
import tempfile
import pandas as pd
import pathlib

from celery import Celery, group, subtask, chain, uuid
import kombu
import redis



THIS_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(THIS_DIR,'config.yml')
with open(config_path, 'r') as f:
    mycfg = yaml.safe_load(f.read())

import celeryconfig
celery = Celery()
celery.config_from_object(celeryconfig)

AMQP_URI = os.environ["AMQP_URI"]
print(AMQP_URI)
kombu_inst = kombu.Connection(AMQP_URI)
kombu_inst.connect()

CACHE_URI = os.environ["CACHE_URI"]
cache_inst = redis.Redis.from_url(CACHE_URI)
#cache_inst.set(task_id,mydict)
#cache_inst.delete(task_id)
#fetched = cache_inst.get(task_id)

def get_queue_status():
    # since `celery.control.inspect().active()` only gets you active tasks
    # and not those in the queue, we opted for rabbitmq data via kombu
    client = kombu_inst.get_manager()
    queues = client.get_queues('')
    queue_len=[x for x in queues if 'default' in x['name']][0]['messages_ready']
    unack_len=[x for x in queues if 'default' in x['name']][0]['messages_unacknowledged']
    return {'queue_len':queue_len,'unack_len':unack_len}

def get_task_status(task_id):
    res = celery.AsyncResult(task_id)
    return res.ready()

@celery.task(bind=True)
def myjob(self,mydict):
    task_id = self.request.id
    workdir=f'/shared/{task_id}'
    os.makedirs(workdir,exist_ok=True)
    hostname = os.environ.get('HOSTNAME')
    mymessage={'task_id':task_id,'hostname':hostname}
    mydict['hostname']=hostname
    queue_file = os.path.join(workdir,'.queued')
    lock_file = os.path.join(workdir,'.lock') # processing
    done_file = os.path.join(workdir,'.done')
    error_file = os.path.join(workdir,'.error')
    done_emailed_file = os.path.join(workdir,'.done.emailed')
    error_emailed_file = os.path.join(workdir,'.error.emailed')
    with open(lock_file,'w') as f:
        f.write(json.dumps(mydict))
    os.remove(queue_file)
    stdout_file = os.path.join(workdir,'std.out')
    stderr_file = os.path.join(workdir,'std.err')
    try:
        # TODO: create sh file, subprocess write stdout stderr to files.
        time.sleep(3)
        if mydict['extra_sauce']=="YES":
            raise ValueError("extra_sauce!")
        
        mymessage['done']=True
        with open(done_file,'w') as f:
            f.write(json.dumps(mymessage))
        for x in [queue_file,lock_file,error_file,done_emailed_file,error_emailed_file]:
            if os.path.exists(x):
                os.remove(x)
    except:
        mymessage['error']=traceback.format_exc()
        with open(error_file,'w') as f:
            f.write(json.dumps(mymessage))
        for x in [queue_file,lock_file,done_file,done_emailed_file,error_emailed_file]:
            if os.path.exists(x):
                os.remove(x)

    return True


import smtplib
from email.message import EmailMessage
SMTP_SERVER = os.environ.get("SMTP_SERVER")
def email(from_email,to_email,title,message):
    return
    message = EmailMessage()
    message.set_content('Message test content')
    message['Subject'] = title
    message['From'] = from_email
    message['To'] = to_email
    smtp_server = smtplib.SMTP(SMTP_SERVER)
    smtp_server.send_message(message)
    smtp_server.quit()


def get_job_status():
    mylist = []
    for task_id in os.listdir("/shared"):

        if task_id == 'monitor':
            continue

        workdir = os.path.join("/shared",task_id)
        queue_file = os.path.join(workdir,'.queued')
        lock_file = os.path.join(workdir,'.lock')
        done_file = os.path.join(workdir,'.done')
        error_file = os.path.join(workdir,'.error')
        done_emailed_file = os.path.join(workdir,'.done.emailed')
        error_emailed_file = os.path.join(workdir,'.error.emailed')

        if os.path.exists(error_emailed_file):
            status = 'errored_out_email_sent'
        elif os.path.exists(done_emailed_file):
            status = 'done_email_sent'
        elif os.path.exists(error_file):
            status = 'errored_out'
        elif os.path.exists(done_file):
            status = 'done'
        elif os.path.exists(lock_file):
            status = 'processing'
        elif os.path.exists(queue_file):
            status = 'queue'
        else:
            status = 'undetermined'

        myitem = dict(
            task_id=task_id,
            status=status,
            workdir=workdir,
        )
        mylist.append(myitem)

    return mylist

@celery.task()
def mymonitor():

    monitordir = "/shared/monitor"
    os.makedirs(monitordir,exist_ok=True)
    lock_file = os.path.join(monitordir,".lock")

    if os.path.exists(lock_file):
        return

    pathlib.Path(lock_file).touch()

    for task_id in os.listdir("/shared"):

        if task_id == 'monitor':
            continue

        workdir = os.path.join("/shared",task_id)
        done_file = os.path.join(workdir,'.done')
        error_file = os.path.join(workdir,'.error')
        done_emailed_file = os.path.join(workdir,'.done.emailed')
        error_emailed_file = os.path.join(workdir,'.error.emailed')
        from_email,to_email,title,message = None,None,None,None

        if os.path.exists(done_file):
            email(from_email,to_email,title,message)
            pathlib.Path(done_emailed_file).touch()
            os.remove(done_file)

        if os.path.exists(error_file):
            email(from_email,to_email,title,message)
            pathlib.Path(error_emailed_file).touch()
            os.remove(error_file)
