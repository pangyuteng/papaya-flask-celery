## drag and drop with javascript and python flask

### demo

+ spin up flask
```
docker-compose build
docker-compose up
```
+ head to `localhost:5000`, and drag in multiple `.csv` files.

### dev

+ development mode
```
docker-compose build
docker run -it -p 5000:5000 -v $PWD:/opt/code dragndrop_dropzone bash
python app
```
### ref
+ https://github.com/dropzone/dropzone/releases/download/v5.8.1/dist.zip
+ https://stackoverflow.com/a/42264730/868736
+ https://github.com/greyli/flask-dropzone/blob/master/examples/complete-redirect/app.py