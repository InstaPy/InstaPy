FROM ubuntu:16.04
MAINTAINER Grossmann Tim <contact.timgrossmann@gmail.com>

# Environment setup
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install \
        apt-utils \
        locales \
        unzip \
        python3-pip \
        python3-dev \
        build-essential \
        libgconf2-4 \
        libnss3-1d \
        libxss1 \
        libssl-dev \
        libffi-dev \
        xvfb \
        wget \
        libcurl3 \
        gconf-service \
        libasound2 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libfontconfig1 \
        libgdk-pixbuf2.0-0 \
        libgtk2.0-0 \
        libpango1.0-0 \
        libxcomposite1 \
        libxtst6 \
        fonts-liberation \
        libappindicator1 \
        xdg-utils \
        git \
    && pip3 install --upgrade pip \
    && locale-gen en_US.UTF-8 \
    && dpkg-reconfigure locales \
    && pip3 install --upgrade pip \
    && apt-get -f install

# Installing latest chrome
RUN cd ~ \
    && wget "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get install -y -f \
    && rm google-chrome-stable_current_amd64.deb
    
# Setting the language enc
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Adding InstaPy
RUN git clone -b docker_settings https://github.com/timgrossmann/InstaPy.git \
    && wget "http://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64 \
    && mv chromedriver InstaPy/assets/chromedriver \
    && chmod +x InstaPy/assets/chromedriver \
    && chmod 755 InstaPy/assets/chromedriver \
    && cd InstaPy \
    && pip install .

# Copying the your quickstart file into the container and setting directory
COPY quickstart.py ./InstaPy
WORKDIR /InstaPy 
    
CMD ["python3.5", "quickstart.py"]