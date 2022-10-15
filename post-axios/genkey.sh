#!/bin/bash

export KEYSTORE=keystore
mkdir -p ${KEYSTORE}
if [[ -f ${KEYSTORE}/key.pem && -f ${KEYSTORE}/cert.pem ]]; then
    echo 'cert.pem and key.pem found.'
else
    echo 'generating certificate for https...'
    openssl req -x509 -newkey rsa:4096 -nodes \
        -out ${KEYSTORE}/cert.pem \
        -keyout ${KEYSTORE}/key.pem \
        -days 3650 \
        -subj "/C=US/ST=NA/L=NA/O=NA/CN=NA"
fi

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
