import os
from kombu import Queue

RABBIT_URI = os.environ["AMQP_URI"]
REDIS_URI = os.environ["REDIS_URI"]

broker_url = RABBIT_URI
result_backend = REDIS_URI
task_serializer = "pickle"
result_serializer = "pickle"
accept_content = ["pickle"]
# # 1day=60*60*24*7 seconds==604800 seconds
broker_transport_options = {'visibility_timeout': 604800}
worker_prefetch_multiplier = 1
task_acks_late = True
broker_heartbeat = 0
#timezone = 'US/Pacific'
enable_utc = True
task_default_queue = 'default'
task_queue_max_priority = 10
task_default_priority = 5

task_routes= {
    'app.main_task': {'queue': 'default'},
    'app.subtask': {'queue': 'subtask'},
}

task_queues = (
    Queue('default', routing_key='default-routing-key', queue_arguments={'x-max-priority': 10}),
    Queue('subtask', routing_key='subtask-routing-key', queue_arguments={'x-max-priority': 10}),
)



