FROM ubuntu

RUN apt-get update
RUN apt-get install -y python wget unzip python-pip

RUN mkdir /InstaPy
WORKDIR /InstaPy
COPY . .

WORKDIR /InstaPy/assets
RUN wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip
RUN unzip -o chromedriver_linux64.zip

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - 
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update 
RUN apt-get install -y google-chrome-stable

WORKDIR /InstaPy
RUN pip install .
