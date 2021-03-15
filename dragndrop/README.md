## drag and drop with Dropzone (javascript) and Flask (python)

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
python app.py
```

+ move new css and js files to `static` folder.
```
https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js
https://github.com/dropzone/dropzone/releases/download/v5.8.1/dist.zip
```


### ref
+ https://www.dropzonejs.com/
+ https://stackoverflow.com/a/42264730/868736
+ https://github.com/greyli/flask-dropzone/blob/master/examples/complete-redirect/app.py