import time
from app import create_order
    
def mytrigger():

    # works
    result = create_order.apply_async()
    
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    print(result.ready())
    print(result.result,'here')
    print('done')

if __name__ == '__main__':
    mytrigger()