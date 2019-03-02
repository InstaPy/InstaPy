FROM python:3.7-slim-stretch
COPY ./requirements.txt /tmp
RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
      wget \
      gcc \
      g++ \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && apt-get purge -y --auto-remove \
      gcc \
      g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["./code/wait-for-selenium.sh", "http://selenium:4444/wd/hub", "--", "python", "code/docker_quickstart.py"]
