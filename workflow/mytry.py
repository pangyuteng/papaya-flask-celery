
#
# VERY GOOD - usage of "noop"
# https://www.ovh.com/blog/doing-big-automation-with-celery/
# https://stackoverflow.com/a/29689441/868736
#
import time
from app import (
    chain, group, chord,
    mystart, mydone, noop,
    myfind, myunwrap, mymove, 
)

def main():
    print('am here')
    mylist = [1,2,3]
    print('ok')

    workflow = chain(
        group(myfind.map(mystart.s())),
        myunwrap.s(noop.s()),
        group(mymove.map(noop.s())),
        mydone.s(noop.s())
    )
    workflow.delay((mylist,))

    print('done')

if __name__ == '__main__':
    for x in range(100):
        main()