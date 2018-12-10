FROM python:3.6
RUN apt update && apt install python3-dbus -y

RUN mkdir /code
RUN mkdir /config
WORKDIR /code
COPY ./requirements.txt /config/
RUN pip install -r /config/requirements.txt
COPY ./ /code/
