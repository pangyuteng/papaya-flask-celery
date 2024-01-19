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
def sub_task(var0,var1,mybool=False):
    logger.info("app1.sub_task started.")
    logger.info(f"{var0} {var1} {mybool}")
    logger.info("sleeping for 10 seconds.")
    time.sleep(10)
    var2 = var0 + var1
    logger.info("app1.sub_task done.")
    return var2