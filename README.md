# papaya-flask-celery

A hello world project that demonstrates how to view nifti images by leveraging papaya, flask and celery.  

+ Papaya is used for viewing images

+ Flask is used for REST API and serving static pages

+ Celery is used for long running tasks on the server end (for image processing people, that means... segmentation, quantification!)

Papaya - https://github.com/rii-mango/Papaya

Flask - https://github.com/pallets/flask

Gunicorn - https://gunicorn.org

Celery - https://github.com/celery/celery

Docker - https://www.docker.com


## build with docker, then start Flask and underlying services.

```
docker-compose build
docker-compose up
```

## check out the images with the Papaya viewer that you are now hosting!

+ head over to localhost:5000 and click on one of the mocked links.

+ Example 1. Show Image.

## maybe TODOS for this project, if it doesn't die out like covid.

+ client side async - get a list of dicom files quickly and render in papaya.
  
+ server side async - user triggers segmentation with mouse click location, once process is complete, client side gets updated.

+ Add MongoDB & File Storage ( enable drag and drop import & store & retrive data)

+ Add authentication


