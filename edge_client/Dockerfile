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

#docker run --net="host" --privileged -e REPORT_PERIOD="10s" -e INTERFACE_DEVICE_NAME="wlan1" -e FORCE_KILL_TIME="5s" -e S3_BUCKET_TARGET="<YOUR_OWN_VALUE>" -e AWS_ACCESS_KEY_ID="<YOUR_OWN_VALUE>" -e AWS_SECRET_ACCESS_KEY="<YOUR_OWN_VALUE>" <YOUR_IMAGE_NAME>

