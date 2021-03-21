## passwordless authentication with itsdangerous

### demo

+ spin up flask
```
bash up.sh
```

+ head to `localhost:5000`

+ login with time-sensitive token.
```
curl -k -X POST -F 'email=asdf@ok.com' https://localhost:5000/login
```

+ authenticae with token as a user
```
curl -k https://localhost:5000/authenticate?token=asdf%40ok.com.YFebvQ.VZXx-lr5rZeAq0AAdhPD5vfD-9w
```

+ use `itsarobot` token as authentication
```
curl -k -u itsarobot.YFehGA.ZqwLF5sTpN6pupficH_W0nA8GGU:dummy https://localhost:5000/api/resource
```

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
