#!/bin/bash
celery -A app worker -Q receiver --loglevel=INFO --pool=gevent --concurrency=2 --hostname=%h