## the project name may change...


For now this is a hello world project that demonstrates how to view nifti images by leveraging papaya, flask and celery.  

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

    + simple client side "async await" with axios.

    + show tabular data using DataTables, with link to download csv.

## motivation & rant

As a person with a non cs background and being in a rather isolated field from web development - biomedical-image-processing (computer-vision, medical imaging, biology), I cringe alot when dealing with "web stuff"... especially looking at java script, arrhhghhh, somehow the syntax just gets to me, or perhaps just because the name contains the word java, or maybe it tries hard to be not verbose, but you still need to add a `;` to the end of line, all in all, for me, js seems a bit cryptic, and the cryptic gets more "crytpier" once you add on async logics, and the abundant little minimized js libraries with cool names... as I make up excuses and try very hard to avoid getting near javascript... at the same time, javascript is most likey supporting most websites and I am awed at the pace it evolves and how it kept on building upon or trumping other tech stacks, from static html, css, flash, then (now) ajax, angular, react.  These days, even tensorflow have a js version. Gotta give respect to the people building these tools, dealing with the ever changing tech stack, plus the attention to detail, patience required to build a functional, customized, responsive, sleek, and reliable web-based gui.

Fast forward to year 2020, despite hating and avoding building anything GUI related, and any language with the word java (yes, I hate java, and i know javascript is not java), hosting a web site to visualize data, monitor, trigger, maintain workflows is becoming trendier and possible an inevitable reality. Having this "zero-foot-print" web site for everything may be an over kill, but for me, naively in my mind, it seems to kind of out weight the alternative - the dreadful tasks of maintaining legacy applications that needs to be installed in different PCs - project managers, co-worker and client (think jnlp, java applications with no unit test cases, C++ qt applications built in windows with no source code ...).  Further with the libraries that is now available in Python and cool libraries for viewing 2d and 3d images like papaya, webgl in javascript, it really doesn't take much to cook up some basic web pages to monitor in-house workflows, visualize images and surfaces.  Yes, coding in javascript is still required, but most code can be dealt in python.  Last but not least, you have a bunch of online resources since javascript is such a popular language.

Thus, for me at least, there is really no more excuse to not learn the web-stack anymore... so here I am, creating this project - which basically is just me cobbling up python javascript libraries in containers - this is my way of learning the inner workings of "web sites", and hopefully will serve as the basis for future projects if need be.  The project functionality "depth-wise" will be kept to a minimal, and have a hello-world-style to it, meaning, many little examples, which then these examples can perhaps be used for profiling or if it works at scale, copy and pasted to bigger projects.  The examples which I'd like to cover for now are: uploading of images, download of images, view 3d images, trigger and monitor segmentation quantification workflows and perhaps later down the road, trigger and monitor training of nn models (slap in tensorboard), maybe also slap in Airflow in there to make it more fun.  Come to think of it, web stack used to be "LAMP" then "MEAN", for some "Django"... what I'm really getting to and want to learn in this project is a "minimal tech stack" for machine leaning, which covers data intake, analysis, visualization, flagging cases with good/bad data, analyais or results (ui, and data pseristance invovled), training of models, inference, and finally analytics/plotting and reporting.

end of rant.

## maybe TODOS for this project, if it doesn't die out like covid.

+ to have a "minimal tech stack" that can do "all things machine learning" via REST api: data import, model training, inference, export and visualization of quantified data.  This is likely an over kill / over engineered project.  That said, I'm sure there are many commercial sites that are already doing all this but with a very very polished frontend...and they will be charging you hundreds if not thousands per month for this service. 

+ After just a few minutes spent on google, below are the sites that are already doing what this project wants to be...

    + https://teachablemachine.withgoogle.com
    + https://cloud.google.com/solutions/build-and-use-ai
    + https://aws.amazon.com/machine-learning/ai-services/
    + https://azure.microsoft.com/en-us/services/machine-learning/
    + https://deepcognition.ai/features/deep-learning-studio/



+ all things ML stack
    + [x] docker
    + [x] rest api front - flask
    + [x] async trigger long running task - celery/rabbitmq/redis
    + [x] 2d, 3d visualization - Papaya
    + [x] authenticaion (see ./itsdangerous)
    + [x] enable drag and drop import & store & retrive data (see ./dragndrop)
    + [x] email. https://gist.github.com/pangyuteng/b1e5cd003bd2310cbf335791e9d08d1d
    + [x] scaling/async with nginx. (see ./nginx and 8398773c00204c041dec9dad837aebf4)
    + [o] celery task chaining (see ./workflow)
    + [ ] data access abtraction (see a808eb0c026474d999110039c9b03ae1)
    + [ ] mongodb
    + [ ] file storage
    + [o] batch data import export capability? via celery. (see ./dragndrop)
    + [ ] airflow for long running tasks vs celery?
    + [ ] batch export of quantified data. (see ./dragndrop and ./workflow and cffda14bba8b1a0526ec6992118b9fa4)
    + [o] case report generation (see 2af5d4ee692f05fab20e72630260e2be and https://stackoverflow.com/a/37807113/868736)
    + [ ] create aws friendly docker-compose file to claim project is "in the cloud".

+ client side async - get a list of dicom files quickly and render in papaya.
  
+ server side async - user triggers segmentation with mouse click location, once process is complete, client side gets updated.

+ add airflow and model traning monitoring...?

+ add example for image labeling / semantic segmentation data label html for submission to amazon mechanical turk? to create labeled dataset

+ add report generation.

+ unit test case

+ cicd

+ cicd for model training/testing/version control/updating model weights for inference.
