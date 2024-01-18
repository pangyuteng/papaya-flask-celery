import os
import time
import random
from celery import Celery, uuid
from celery.result import AsyncResult

import celeryconfig1
app = Celery()
app.config_from_object(celeryconfig1)

@app.task()
def sub_task():
    time.sleep(5)
    return 1,2