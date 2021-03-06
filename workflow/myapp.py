'''
proposed workflow.

mystart---myfind---mymove---|
        |        |-mymove --|
        |                   |- mydone  
        |-myfind---mymove --|
                 |-mymove --|

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

@app.task()
def mystart(fetch_list):
    print('mystart',fetch_list)
    time.sleep(5)
    return fetch_list

@app.task()
def myfind(myfind_param):
    print('myfind_param',myfind_param)
    time.sleep(1)
    if myfind_param == 1:
        return [1,2,3]
    elif myfind_param == 2:
        return [4,5,6]
    else:
        return [6,8,9]

@app.task()
def myunwrap(listoflist):
    print('myunwrap',listoflist)
    # flatten items from output list of all myfinds
    flat_list = [item for sublist in listoflist for item in sublist]
    return flat_list

@app.task()
def mymove(mymove_param):
    print('mymove',mymove_param)
    time.sleep(1)
    return mymove_param*2

@app.task()
def mydone(param_list):
    print('mydone',param_list)
    time.sleep(1)
    return param_list
