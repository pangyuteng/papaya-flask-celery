
```


https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html


docker build -t flask-jwt .

docker run -it -p 5555:5555 -w $PWD -v /mnt:/mnt flask-jwt bash

python app.py -d


curl -k --header "Content-Type: application/json" --request POST \
--data '{"username":"xxxx","password":"xxx"}' \
http://127.0.0.1:5555/login


export JWT_TOKEN=1234

curl -k --request GET -H Authorization:"Bearer $JWT_TOKEN" "http://127.0.0.1:5555/blah?param0=kaka"

browser friendly option via query_string:

curl -k --request GET "http://127.0.0.1:5555/blah?param0=kaka&jwt=$JWT_TOKEN"



```