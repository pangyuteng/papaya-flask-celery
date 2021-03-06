
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
        group(myfind.map(mystart(mylist))),
        myunwrap.s(noop.s()),
        group(mymove.map(noop.s())),
        mydone.s()
    )
    ~ workflow
    print('done')
if __name__ == '__main__':
    main()