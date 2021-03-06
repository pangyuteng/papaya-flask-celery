# https://www.ovh.com/blog/doing-big-automation-with-celery/

from app import (
    chain, group, chord,
    mystart, mydone,
    myfind, myunwrap, mymove, 
)

def main():
    print('am here')
    mylist = range(3)
    print('ok')
    workflow = chord(
        mymove.s(y) for y in chain( 
            group([myfind.s(x) for x in mystart.s(mylist)]),
            myunwrap.s()
        ))(mydone.s())
    print('running')
    print(workflow.get())

if __name__ == '__main__':
    main()