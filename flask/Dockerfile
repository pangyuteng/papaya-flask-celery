# TODO: ADD VERSIONS TO basefile and requirements.txt
FROM python

# Copy the package requirements
COPY requirements.txt /opt

WORKDIR /opt
# Install the package requirements
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . /opt

# prevent container from exiting - useful for development.
CMD tail -f /dev/null