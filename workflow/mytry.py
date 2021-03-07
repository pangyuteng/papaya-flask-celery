
#
# madeup complex workflow
# https://www.ovh.com/blog/doing-big-automation-with-celery/
# https://stackoverflow.com/a/29689441/868736
#
# real world complex workflow!
# https://www.azavea.com/blog/2016/10/20/how-to-build-asynchronous-workflows-geospatial-application/
#
# "Celery does not natively support conditional or dynamic task chains. "
# "We got around this by creating a list of tasks depending on input, and "
# "converting it to a Celery chain at the very end."
#

import time
from app import (
    chain, group, chord, dmap,
    mystart, mydone, noop,
    myfind, myunwrap, mymove, 
    myfindmap, mymovemap,
)

def main():
    print('am here')
    mylist = (1,2,3,4)*10
    print('ok')

    workflow = chain(
        mystart.s(), 
        dmap.s(myfind.s()),
        mydone.s(),
    )
    result = workflow.apply_async(args=(mylist,))
    while not result.ready():
        print(result.ready())
        time.sleep(1)
    print(result.ready())
    print(result.result,'here')
    print('done')

if __name__ == '__main__':
    main()