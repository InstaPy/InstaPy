FROM ubuntu:16.04
MAINTAINER ARCHER Stéphane <stephane.archer@epita.fr>

RUN apt-get update \
    && apt-get install -y \
        chromium-browser \
        python \
        python-pip \
        unzip \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /InstaPy
WORKDIR /InstaPy
COPY . .

RUN wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip \
    && unzip -o -d /InstaPy/assets chromedriver_linux64.zip \
    && rm chromedriver_linux64.zip

RUN pip install .
