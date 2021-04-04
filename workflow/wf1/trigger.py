import time
from app import (
    chain, group, chord,
    mymapper, mymain
)

def mytrigger0():

    # works
    result = mymapper.apply_async()
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    
def mytrigger():

    # works
    result = mymain.apply_async()
    
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    print(result.ready())
    print(result.result,'here')
    print('done')

if __name__ == '__main__':
    mytrigger()