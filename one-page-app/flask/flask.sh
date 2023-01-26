#!/bin/bash

cd /opt/app

# or you can scale via nginx,docker...
if [ ${ENVIRONMENT} == "production" ]; then
    gunicorn -k eventlet --workers 2 --timeout 120 --bind 0.0.0.0:5000 wsgi:app
elif [ ${ENVIRONMENT} == "development" ]; then
    python app.py --port 5000 --debug True
else
    echo "ENVIRONMENT can not be determined!" 1>&2
    exit 1
fi
