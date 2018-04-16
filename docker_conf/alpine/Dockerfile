FROM gliderlabs/alpine:3.3

RUN apk add --update \
    git \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*

RUN mkdir /code && mkdir /config

WORKDIR /code
COPY ./requirements.txt /config/
ONBUILD RUN virtualenv /env && /env/bin/pip install -r /code/requirements.txt

COPY ./ /code/%
