# This docker image is built for raspberry pi 3b with debian 11 "bullseye" (32bit version)
FROM python:3.9.7-bullseye

# Setup wifi tools
RUN apt-get update && apt-get install -y \
    aircrack-ng

# Setup AWS cli
RUN pip3 install awscli

# Setup app
COPY ./app ./app
WORKDIR ./app

CMD [ "bash", "app.sh" ]
