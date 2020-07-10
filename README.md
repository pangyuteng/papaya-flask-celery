# papaya-flask-celery


A hello world sample that demonstrate how to show nifti images by leveraging papaya, flask and celery.

The dead simpler alternative when we are considering to scale the app is to cut off dependency on Celery, and slap a load balancer in front of Flask, that probably make much more sense.... That said, I'm sticking with celery+rabbitmq+redis, just because they have cuter names than "load balancer".

Papaya - https://github.com/rii-mango/Papaya

Flask - https://github.com/pallets/flask

Celery - https://github.com/celery/celery

Docker - https://www.docker.com

## build with docker, then start Flask and underlying services.

```
docker-compose build
docker-compose up
```

## check out the images with the Papaya viewer that you are now hosting!

+ head over to localhost:5000 and click on one of the mocked links.