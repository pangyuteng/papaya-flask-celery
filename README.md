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

## motivation & rant

As a person with a non cs background and being in rather isolated field from web development - biomedical-image-processing (computer-vision, medical imaging, biology), I cringe alot when dealing with "web stuff"... especially looking at java script, arrhhhhh, the syntax, it seems like it wants to not be verbose, but now because you have aync, it seems imo, cryptic and still verbose... I tried avoiding it but at the same time, am also amazed at the pace it evolves and trumpped other tech stacks, from html,css,flash, then ajax, angular, not react and even tensoflow have a js version now. Gotta give repesect the pelple building these tools, dealing with the ever changing tech stack, plus the attention to detail and patience required to build a functional, customized, usable, sleek, and reliable web-based gui.  Fast forward to year 2020, despite hating and avoding building anything GUI related, hosting a web site to visualize data, monitor,trigger, maintain workflows is becoming an inevitable trend / need. Having this "zero-foot-print" web site for everything may be an over kill, but for me, naively in my mind, it seems to kind of weigh the alternative - the dreadful task of maintaining legacy applications (think jnlp, java applications no unit test cases, C++ qt applications built in windows with no source code ...) that needs to be installed in different PCs - project managers, co-worker and client.  Further with the libraries that is now available in Python and cool libraries for viewing 2d and 3d images like papaya, webgl in javascript, it really doesnt take much to cook up some basic web-pages to monitor in-house workflows, visualize images and surfaces.  yes coding in javascript is still required, but most code can be dealt in python and last but not least you have a bunch of online resources since javascript it such a popular language.  Thus, for me at least, there is really no more excuse to not learn the web-stack anymore... so here I am, creating this project - which is basicaling cobbling up python javascript libraries and dockerizing "it" which it will serve to be a 'hello-world' project that can be used as a basis for a bigger project - upload, download, view medical images and trigger and monitor segmentation quantification workflows, and perhaps later down the road monitor trigger train nn models, maybe slap in Airflow in there to make it more fun.

## maybe TODOS for this project, if it doesn't die out like covid.

+ client side async - get a list of dicom files quickly and render in papaya.
  
+ server side async - user triggers segmentation with mouse click location, once process is complete, client side gets updated.

+ Add MongoDB & File Storage ( enable drag and drop import & store & retrive data)

+ Add authentication

+ Add airflow and model traning monitoring...?

