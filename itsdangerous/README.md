## passwordless authentication with itsdangerous

### demo

+ spin up flask
```
openssl req -x509 -newkey rsa:4096 -nodes -out keystore/cert.pem -keyout keystore/key.pem -days 365
docker-compose build
docker-compose up
```
+ head to `localhost:5000`

### dev

+ development mode
```
docker-compose build
docker run -it -p 5000:5000 -v $PWD:/workdir -w /workdir -v $PWD/keystore:/keystore itsdangerous bash
python app.py
```



### ref
```
https://github.com/kevinjqiu/flask-passwordless
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
```
