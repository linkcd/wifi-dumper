# This docker image is built for raspberry pi 3b with debian 10 "buster" (32bit version)
FROM python:3.9.7-buster

# Setup wifi tools
RUN apt-get update && apt-get install -y \
    aircrack-ng

# Setup AWS cli
RUN pip3 install awscli

# Setup app
COPY ./app ./app
WORKDIR ./app

CMD [ "bash", "app.sh" ]
