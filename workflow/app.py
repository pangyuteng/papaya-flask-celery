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

#@app.task(bind=True)
#def mystart(self,fetch_list):
mynum = 1

@app.task
def noop(*args, **kwargs):
    # Task accepts any arguments and does nothing
    print(args, kwargs)
    return True

@app.task()
def mystart(fetch_list):
    print('mystart',fetch_list)
    time.sleep(mynum)
    return fetch_list

@app.task()
def myfind(*args, **kwargs):
    print(args)
    myfind_param = args[0]
    print('myfind_param',myfind_param)
    time.sleep(mynum)
    if myfind_param == 1:
        v = 1
    elif myfind_param == 2:
        v = 5
    else:
        v = 10
    return list(range(v))

@app.task()
def myunwrap(*args, **kwargs):
    print(args)
    listoflist = args[0]
    print('myunwrap',listoflist)
    # flatten items from output list of all myfinds
    flat_list = [item for sublist in listoflist for item in sublist]
    return flat_list

@app.task()
def mymove(*args, **kwargs):
    print(args)
    mymove_param = args[0]
    print('mymove',mymove_param)
    time.sleep(mynum)
    return mymove_param*2

@app.task()
def mydone(*args, **kwargs):
    print(args)
    mydone_param = args[0]
    print('mydone',mydone_param)
    time.sleep(mynum)
    return len(mydone_param)
