import logging
logger = logging.getLogger(__file__)
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
    # actual logic lives in app1.py
    raise ValueError()

@app.task()
def main_task():
    logger.info("app0.main_task started.")
    logger.info("app0.main_task triggering sub_task...")

    args, kwargs = [1,2],{'mybool': True}
    result = sub_task.apply_async(args, kwargs)

    while not result.ready():
        logger.info(f"result.ready() {result.ready()}")
        time.sleep(2)
    logger.info(f"result.ready() {result.ready()}")
    out = result.result
    logger.info(f"results: {type(out)},{out}")
    logger.info("app0.main_task done.")
    return out
