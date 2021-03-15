FROM python:3.7-buster

RUN mkdir -p /opt/code
WORKDIR /opt/code
COPY requirements.txt /opt/code
RUN pip install -r /opt/code/requirements.txt

COPY . /opt/code

RUN pip install -r /opt/code/requirements.txt

