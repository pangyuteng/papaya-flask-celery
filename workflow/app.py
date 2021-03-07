'''
proposed workflow.

mystart---myfind---mymove---|
        |        |-mymove --|
        |                   |- mydone  
        |-myfind---mymove --|
                 |-mymove --|

               merge output of my find, then move to mymove

mystart (reads csv and sends message to queue - `initiate`)
myfind (runs `findscu` connects to hospital pacs and download multiple query dcm files)
mymove (takes in single query dcm file and runs `movescu` to fetch dcm to Orthanc, 
         downloads and process zip from localhost Orthanc and delete from Orthanc)
mydone (email, and cleanup if necessary)

user executes `bin/fetch.py` which triggers `mystart`
worker `receiver.sh` consumes `mystart`, `mydone`
worker `worker.sh` consumes `myfind` and `mymove`

TODO: rate limit / throttling to maintain availability
assuming 2 receivers and 10 workers
each recevier shall only occupy 5 workers, to maintain availability
if receiver is increased, dynically reduce worker to maintain availability until utilizing 1 worker.
'''

'''
TODO: misc
#task = celery.AsyncResult(task_id)
#response = {'ready': task.ready(),'task_id':task_id}


'''
import os
import time
from copy import deepcopy
from celery import Celery, group, subtask, chain, chord, uuid
from celery.result import AsyncResult


celery_config = {
    "broker_url": os.environ["AMQP_URI"],
    "result_backend": os.environ["REDIS_URI"],
    "task_serializer": "pickle", # for passing binary objects
    "result_serializer": "pickle",
    "accept_content": ["pickle"],
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

#@app.task(bind=True)
#def mystart(self,fetch_list):
mynum = 1

@app.task
def noop(ignored):
    print('noop',ignored)
    return ignored

@app.task()
def mystart(fetch_list):
    print('mystart',fetch_list)
    time.sleep(mynum)
    return fetch_list

@app.task()
def myfindmap(items):
    return myfind.map(items)

@app.task()
def myfind(myfind_param):
    print('myfind_param',myfind_param)
    time.sleep(mynum)
    if myfind_param == 1:
        v = 1
    elif myfind_param == 2:
        v = 5
    else:
        v = 10
    mylist = list(range(v))
    return mymove.map(mylist)()

@app.task()
def mymovemap(items):
    return mymove.map(items)

@app.task()
def mymove(mymove_param):
    print('mymove',mymove_param)
    time.sleep(mynum)
    return mymove_param*2


@app.task()
def myunwrap(listoflist):
    print('myunwrap',listoflist)
    # flatten items from output list of all myfinds
    #flat_list = [item for _,sublist in listoflist.collect() for item in sublist]
    return (mymove.map(x) for x in listoflist)

@app.task()
def mydone(mydone_param):
    print('mydone',mydone_param)
    time.sleep(mynum)
    return len(mydone_param)
