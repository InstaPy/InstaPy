FROM python:3.6
RUN apt-get update && apt-get install -y chromedriver
COPY ./requirements.txt /
RUN pip install -r /requirements.txt
