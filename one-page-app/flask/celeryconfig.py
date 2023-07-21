import os
from celery.schedules import crontab
from kombu import Queue

broker_url = os.environ["AMQP_URI"]
result_backend = os.environ["REDIS_URI"]

# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html

beat_schedule = {
    'monitor': {
        'task': 'utils.mymonitor',
        'schedule': crontab("*/1 * * * * *"),
        'args': [],
    },
}

timezone = "UTC"
task_default_queue = 'default'
task_routes= {
    'utils.myjob': {'queue': 'default'},
    'utils.mymonitor': {'queue': 'default'},
}

task_queue_max_priority = 10
task_default_priority = 5
task_queues = (
    Queue('default', routing_key='default-routing-key', queue_arguments={'x-max-priority': 10}),
)

task_serializer='pickle'
result_serializer='pickle'
accept_content=['pickle','application/json']
# set an abnormally high value for timeout to prevent job being retried over and over again
broker_transport_options = {'visibility_timeout': 86400}
result_backend_transport_options = {'visibility_timeout': 86400}
worker_prefetch_multiplier = 1
task_acks_late = True
broker_heartbeat = 0



