import time
from app import main_task
    
def mytrigger():

    # works
    result = main_task.apply_async()
    
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    print(result.ready())
    print(result.result,'here')
    print('done')

if __name__ == '__main__':
    mytrigger()