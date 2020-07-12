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

+ head over to localhost:5000 and click on the links for demos.

    + show Image and mask with Papaya.

    + show volume given a list of dicom images.



## motivation & rant

As a person with a non cs background and being in a rather isolated field from web development - biomedical-image-processing (computer-vision, medical imaging, biology), I cringe alot when dealing with "web stuff"... especially looking at java script, arrhhhhh, the syntax just gets to be, maybe because it resembles java, but then it also wants to not be not too verbose, so you make it less verbose, thus becoming a bit cryptic, and then you add on async,await...I make up excuses and tried avoiding it but at the same time, am also amazed at the pace it evolves and how it kept on building upon or trumping other tech stacks, from static html, css, flash, then ajax, angular, react.  These days, even tensoflow have a js version. Gotta give respect to the people building these tools, dealing with the ever changing tech stack, plus the attention to detail and patience required to build a functional, customized, usable, sleek, and reliable web-based gui.

Fast forward to year 2020, despite hating and avoding building anything GUI related, hosting a web site to visualize data, monitor,trigger, maintain workflows is becoming trendier and possible an inevitable reality. Having this "zero-foot-print" web site for everything may be an over kill, but for me, naively in my mind, it seems to kind of out weight the alternative - the dreadful tasks of maintaining legacy applications that needs to be installed in different PCs - project managers, co-worker and client (think jnlp, java applications with no unit test cases, C++ qt applications built in windows with no source code ...).  Further with the libraries that is now available in Python and cool libraries for viewing 2d and 3d images like papaya, webgl in javascript, it really doesn't take much to cook up some basic web pages to monitor in-house workflows, visualize images and surfaces.  Yes, coding in javascript is still required, but most code can be dealt in python  Last but not least, you have a bunch of online resources since javascript is such a popular language.

Thus, for me at least, there is really no more excuse to not learn the web-stack anymore... so here I am, creating this project - which basically cobbles up python javascript libraries in containers - that'll allow me to learn the inner workings of "web sites", and hopefully servce as basis for future projects.  The project functionality will be kept to a minimal, and have a hello-world-style to it, meaning, many little examples, which then these examples can be perhaps used for profiling or if it works at scale, copy and pasted to bigger projects.  The examples which I'd like to cover for now are: uploading of images, download of images, view medical images, trigger and monitor segmentation quantification workflows (hello world airflow), and perhaps later down the road, trigger and monitor training of nn models (slap a tensorboard for all i care), maybe slap in Airflow in there to make it more fun.  Come to think of it, web stack used to be "LAMP" then "MEAN", "Django"... what I'm really get to and learn in this project is a hopefully "minimal tech stack" for a machine leaning "mvp" coovering data intake, analysis, visualization, training of models and inference, and report generation.

## maybe TODOS for this project, if it doesn't die out like covid.

+ client side async - get a list of dicom files quickly and render in papaya.
  
+ server side async - user triggers segmentation with mouse click location, once process is complete, client side gets updated.

+ Add MongoDB & File Storage ( enable drag and drop import & store & retrive data)

+ Add authentication

+ Add airflow and model traning monitoring...?

+ Add report generation.