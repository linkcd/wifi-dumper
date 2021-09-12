# This docker image is built for raspberry pi 3b with debian "buster" (32bit version)
FROM python:3.9.7-buster

# Setup wifi tools
RUN curl -s https://packagecloud.io/install/repositories/aircrack-ng/release/script.deb.sh | bash
RUN apt-get update && apt-get install -y \
    aircrack-ng 

# Setup AWS cli
RUN pip3 install awscli

# Setup app
COPY ./app ./app
WORKDIR ./app

CMD [ "bash", "app.sh" ]

