#!/bin/bash

celery -A utils.celery worker \
    --loglevel=INFO --pool=prefork --max-tasks-per-child=1 \
    --concurrency=1 --prefetch-multiplier=1 --hostname=%h \
    --pidfile /opt/celeryworker.pid

