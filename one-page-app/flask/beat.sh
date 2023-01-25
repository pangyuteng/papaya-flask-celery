#!/bin/bash

celery -A utils.celery beat \
  --loglevel INFO \
  --pidfile /opt/celerybeat.pid
