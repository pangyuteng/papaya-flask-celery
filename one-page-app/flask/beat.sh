#!/bin/bash

cd /opt/app

celery -A utils.celery beat \
  --loglevel INFO \
  --pidfile /opt/celerybeat.pid

