import logging
logger = logging.getLogger(__file__)
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
    logger.info("app1.sub_task running!!")
    time.sleep(5)
    return 1,2