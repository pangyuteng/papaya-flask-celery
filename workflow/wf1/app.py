import os
import time
import random
from copy import deepcopy
from celery import Celery, group, subtask, chain, chord, uuid
from celery.result import AsyncResult
import celery

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


#https://stackoverflow.com/questions/12822005/celery-group-task-for-use-in-a-map-reduce-workflow/12897526

@app.task()
def mymapper():
    #split your problem in embarrassingly parallel maps 
    maps = [mymap.s(), mymap.s(), mymap.s(), mymap.s(), mymap.s(), mymap.s(), mymap.s(), mymap.s()]
    #and put them in a chord that executes them in parallel and after they finish calls 'reduce'
    mapreduce = chord(maps)(myreduce.s())
    return "{0} mapper ran on {1}".format(celery.current_task.request.id, celery.current_task.request.hostname)

@app.task()
def mymap():
    #do something useful here
    import time
    time.sleep(10.0)
    return "{0} map ran on {1}".format(celery.current_task.request.id, celery.current_task.request.hostname)

@app.task()
def myreduce(results):
    #put the maps together and do something with the results
    return "{0} reduce ran on {1}".format(celery.current_task.request.id, celery.current_task.request.hostname)


@app.task()
def mymain():
    
    random_list = [1,2,3]
    mylist = [myfind.s(x) for x in random_list]
    reduced_results = chord(mylist)(mycollect.s())
    more_results = mymove.map(reduced_results.get())
    mydone_results = chord(more_results)(mydone.s())
    return mydone_results

# generate more lists based on input
@app.task()
def myfind(myinput):
    print('myfind',myinput)
    time.sleep(mysleep)

    mylist = random.sample(range(1, 100), myinput)
    return mylist


"""
Takes an iterator of argument tuples and queues them up for celery to run with the function.
https://stackoverflow.com/a/13569873/868736
https://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
https://stackoverflow.com/questions/59013002/how-to-recursively-chain-a-celery-task-that-returns-a-list-into-a-group
"""
@app.task()
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
