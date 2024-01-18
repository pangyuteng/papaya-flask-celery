

docker compose restart worker1 worker0


docker compose up -d

docker exec -it multi-containers-worker0-1 bash

python3 trigger.py