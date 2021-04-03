import os
import time
import random
from copy import deepcopy
from celery import Celery, group, subtask, chain, chord, uuid
from celery.result import AsyncResult

celery_config = {
    "broker_url": os.environ["AMQP_URI"],
    "result_backend": os.environ["REDIS_URI"],
    "task_serializer": "pickle", # for passing binary objects
    "result_serializer": "pickle",
    "accept_content": ["pickle"],
    "worker_prefetch_multiplier": 1,
}

app = Celery(broker=celery_config["broker_url"])
app.conf.update(celery_config)
app.conf.task_default_queue = 'default'
app.conf.task_routes = {
    'mystart': {'queue': 'receiver'},
    'mydone': {'queue': 'receiver'},
}


"""
Takes an iterator of argument tuples and queues them up for celery to run with the function.
https://stackoverflow.com/a/13569873/868736
https://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
https://stackoverflow.com/questions/59013002/how-to-recursively-chain-a-celery-task-that-returns-a-list-into-a-group
"""
@app.task
def dmap(it, callback):
    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    return group(callback.clone((arg,)) for arg in it)()

mysleep = 0

# generate a list
@app.task()
def mystart():
    time.sleep(mysleep)
    random_list = [1,2,3]
    print('mystart',random_list)
    return random_list

# generate more lists based on input
@app.task()
def myfind(myinput):
    print('myfind',myinput)
    time.sleep(mysleep)
    mylist = random.sample(range(1, 100), myinput)
    return mylist

@app.task()
def mycollect(myinput):
    mylist = []
    for x in myinput:
        mylist.extend(x)
    time.sleep(mysleep)
    return mylist

# manipulate with input and return output
@app.task()
def mymove(myinput):
    print('mymove',myinput)
    time.sleep(mysleep)
    return myinput*2

@app.task()
def mydone(myinput):
    print('mydone',myinput)
    time.sleep(mysleep)
    return len(myinput)

############### misc junk

@app.task()
def myfindmap(items):
    return myfind.map(items)


@app.task()
def mymovemap(items):
    return mymove.map(items)


@app.task()
def myunwrap(listoflist):
    print('myunwrap',listoflist)
    # flatten items from output list of all myfinds
    #flat_list = [item for _,sublist in listoflist.collect() for item in sublist]
    return (mymove.map(x) for x in listoflist)


@app.task
def noop(ignored):
    print('noop',ignored)
    return ignored
