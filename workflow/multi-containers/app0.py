import os
import time
import random
from celery import Celery, uuid
from celery.result import AsyncResult

import celeryconfig0
app = Celery()
app.config_from_object(celeryconfig0)

@app.task()
def sub_task():
    # actual logic lives in 
    pass

@app.task()
def main_task():
    result = sub_task.apply_async()
    
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    out = result.result
    print(out,'!!!!!!!!!!!!!!11')
    return out
