#!/bin/bash
#celery -A app worker -Q default --loglevel=INFO --pool=gevent --concurrency=10 --hostname=%h
tail -f /dev/null