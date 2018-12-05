# How to Docker

## Requirements
In order to run InstaPy under this setup, is needed to have installed [docker](https://www.docker.com/get-started) and [docker-compose](https://docs.docker.com/compose/install/)

## Directory structure
Create a folder called **z_{user}** in repo root directory, where `{user}` is your instagram user. Since under this folder we will store sensible data, starting the name with **z_** avoids it to be published on GitHub.
The configuration is based on 3 files `start.py`, `docker-compose.yaml` and `data.yaml`.

### Docker compose
- Will wait for Selenium to be ready, then execute `start.py`
- Uses local files `logs`, `data.yaml` configuration file and `start.py` script.

*docker-compose.yaml*
```yaml
version: '3'
services:
  web:
    command: ["./wait-for-selenium.sh", "http://selenium:4444/wd/hub", "--", "python", "start.py"]
    environment:
      - PYTHONUNBUFFERED=0
    build:
      context: ../
      dockerfile: docker_conf/python/Dockerfile
    depends_on:
      - selenium
    volumes:
      - ./start.py:/code/start.py
      - ./data.yaml:/code/data.yaml
      - ./logs:/code/logs
  selenium:
    image: selenium/standalone-chrome
    shm_size: 128M
```

### Data file
What it stores in the example [Friends last post likes and interact with user based on hashtags](../quickstart_templates/Friends-last-post-likes-and-interact-with-user-based-on-hashtags.py):
- Our credentials
- A *protected* friend list which we want to keep after any acction from InstaPy
- A list of hashtags that we whant to interact with
- Control Flow

*data.yaml*
```yaml
username: string
password: string
friends_interaction: boolean
do_comments: boolean
do_follow: boolean
user_interact: boolean
do_unfollow: boolean
friendlist: [list]
hashtags: [list]
```
- username: Instagram Username
- password: Instagram Password
- friends_interaction: If `True` will like last two post from friendlist, if not, it won't even create _friends_ session
- do_comments: If `True` will enable comments in like_by_tags interaction
- do_follow: If `True` will enable follow users in like_by_tags interaction
- user_interact: If `True` will enable interact with user's posts in like_by_tags interaction
- do_unfollow: If `True` will enable unfollow execution

### How to run
Inside **z_{user}** directory:
- run in background:
`docker-compose down && docker-compose up -d --build`
- run with log in terminal:
`docker-compose down && docker-compose up -d --build && docker-compose logs -f`
