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

WORKDIR /InstaPy/assets
RUN wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip
RUN unzip -o chromedriver_linux64.zip

WORKDIR /InstaPy
RUN pip install .
