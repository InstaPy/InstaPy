FROM gliderlabs/alpine:latest

RUN apk add --update \
    git \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*

RUN mkdir /code 
RUN mkdir /config
RUN mkdir /srv

WORKDIR /code
COPY ./requirements.txt /config/
RUN pip install -r /config/requirements.txt

# Add wait-for
ADD https://raw.githubusercontent.com/Eficode/wait-for/master/wait-for /code
RUN chmod 755 /code/wait-for

COPY ./ /code/
