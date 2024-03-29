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
def myworkflow0():
    
    random_list = [1,2,3]
    mylist = [myfind.s(x) for x in random_list] # distribue to workers
    reduced_results = chord(mylist)(mycollect.s()) # reduce to flat lit
    mymove_results = mymove.map(reduced_results.get()) # execute func per item
    mydone_results = chain(mymove_results,mydone.s()) # aggregate

    return ~mydone_results

@app.task()
def myworkflow1():
    
    mylist = myfind.map(mystart.delay().get())
    
    reduced_results = mycollect.s(~mylist) # reduce to flat lit
    
    mymove_results = mymove.map(~reduced_results) # execute func per item
    
    mydone_results = chain(mymove_results,mydone.s()) # aggregate
    
    results = mydone_results.delay().get()

    return results

@app.task
def dmap(it, callback):
    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    return group(callback.clone((arg,)) for arg in it)()

@app.task()
def myworkflow():
    
    wf = chain(
        mystart.s(),
        dmap.s(myfind.s()),
        _mycollect.s(),
        dmap.s(mymove.s()),
        mydone.s()
    )    

    return wf.delay().get()



# generate more lists based on input
@app.task()
def myfind(myinput):
    print('myfind',myinput)
    time.sleep(mysleep)

    mylist = random.sample(range(1, 100), myinput)
    return mylist

mysleep = 0

# generate a list
@app.task()
def mystart():
    time.sleep(mysleep)
    mylist = mylist = random.sample(range(1, 10), 3)
    print('mystart',mylist)
    return mylist

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

@app.task()
def _mycollect(myinput):
    mylist = []
    for x in myinput:
        mylist.extend(x.get())
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

