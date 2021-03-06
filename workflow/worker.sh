#!/bin/bash
celery -A myapp worker -Q default --loglevel=INFO --pool=gevent --concurrency=2 --hostname=%h