FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:videolan/master-daily && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y sudo gcc musl-dev libffi-dev cargo python3 pip python3-dev bash net-tools git vlc nano ffmpeg && \
    adduser --disabled-password web && \
    pip install pipenv && \
    mkdir -p /opt/www/html && \
    chown -R web:web /opt/www

USER web

COPY Pipfile /opt/www/html

WORKDIR /opt/www/html

RUN pipenv install
