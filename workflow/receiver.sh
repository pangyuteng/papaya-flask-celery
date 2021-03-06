#!/bin/bash
celery -A myapp worker -Q receiver --loglevel=INFO --pool=gevent --concurrency=2 --hostname=%h