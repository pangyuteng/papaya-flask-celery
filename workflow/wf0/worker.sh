#!/bin/bash
celery -A app worker -Q default --loglevel=INFO --pool=gevent --concurrency=2 --hostname=%h