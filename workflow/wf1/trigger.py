import time
from app import (
    chain, group, chord,
    mymapper, #works
    myworkflow0, #works
    myworkflow1, #works
    myworkflow, #works
)

def mytrigger0():

    # works
    result = mymapper.apply_async()
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    
def mytrigger():

    # works
    result = myworkflow.apply_async()
    
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    print(result.ready())
    print(result.result,'here')
    print('done')

if __name__ == '__main__':
    mytrigger()