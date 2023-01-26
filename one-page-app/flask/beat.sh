#!/bin/bash

# weird maybe need to wait for rabbit to load
sleep 20

cd /opt/app

celery -A utils.celery beat \
  --loglevel INFO \
  --pidfile /opt/celerybeat.pid

