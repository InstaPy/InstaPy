FROM python:3.6
RUN mkdir /code
WORKDIR /code
#ADD . /code/

# install openssh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install openssh-server
RUN mkdir -p /var/run/sshd
RUN echo 'root:root' |chpasswd

# make it possible to connect to ssh console with root password
RUN mkdir -p /var/run/sshd && sed -i "s/UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config \
  && sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
  && touch /root/.Xauthority \
  && true

ADD ./config/web/requirements.txt /code/
RUN pip install -r requirements.txt
CMD ["/usr/sbin/sshd", "-D"]