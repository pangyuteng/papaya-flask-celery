
FROM python:3.12-bookworm

#RUN apt-get update -y; apt-get install -y libgl1-mesa-dev xvfb

# Copy the package requirements
COPY requirements.txt /opt

WORKDIR /opt
# Install the package requirements
RUN pip install -U pip
RUN pip install -r requirements.txt

RUN mkdir -p /opt/app
COPY . /opt/app

WORKDIR /opt/app

# prevent container from exiting - useful for development.
#CMD tail -f /dev/null