
##### celery workflow demo

```
workflow 1.

mystart---myfind---mymove---|
        |        |-mymove --|
        |                   |----- mydone  
        |-myfind---mymove --|
            |    |-mymove --|
            |----------------
    merge output of my find, then move to mymove

user executes `bin/fetch.py` which triggers `mystart`
worker `receiver.sh` consumes `mystart`, `mydone`
worker `worker.sh` consumes `myfind` and `mymove`

```

```
tmux new
docker-compose up
tmux new
docker exec -it wf1_receiver_1 bash
