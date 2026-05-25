import os
import time
import random
from copy import deepcopy
from celery import Celery, group, subtask, chain, chord, uuid
from celery.result import AsyncResult
import celery

import celeryconfig
app = Celery()
app.config_from_object(celeryconfig)

import random

@app.task()
def create_order():
    order_id = random.randint(0,6)
    print(f"create_order order_id {order_id}")
    process_order.delay(order_id)

@app.task()
def task_apple(order_id):
    print(f"task_apple {order_id}")
    return "apple"

@app.task()
def task_banana(order_id):
    print(f"task_banana {order_id}")
    return "banana"

@app.task()
def task_orange(order_id):
    print(f"task_orange {order_id}")
    return "orange"

@app.task()
def order_done_notification(product_name):
    print(f"order_notification {product_name}")

@app.task()
def process_order(order_id):
    print(f"process_order {order_id}")
    if order_id in [1,2]:
        jobs = group(
            chain(task_apple.s(order_id),order_done_notification.s()),
            chain(task_banana.s(order_id),order_done_notification.s()),
        )
        jobs.apply_async()
    elif order_id in [3,4]:
        jobs = chain(task_banana.s(order_id),order_done_notification.s())
        jobs.apply_async()
    elif order_id in [5]:
        pass
    else:
        raise NotImplementedError()

