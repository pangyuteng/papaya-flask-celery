
### alternative health checks

```
celery -b amqp://rabbitmq:5672 inspect ping -d celery@$$HOSTNAME

redis-cli --pass 12345 ping

```