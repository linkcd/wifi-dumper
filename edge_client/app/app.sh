#!/bin/bash

# Check env variables
if [[ -z "$INTERFACE_DEVICE_NAME" ]]; then
    echo "Environment variable INTERFACE_DEVICE_NAME is missing, exiting..." 1>&2
    exit 1
fi

if [[ -z "$REPORT_PERIOD" ]]; then
    echo "Environment variable REPORT_PERIOD is missing, exiting..." 1>&2
    exit 1
fi

if [[ -z "$S3_BUCKET_TARGET" ]]; then
    echo "Environment variable S3_BUCKET_TARGET is missing, exiting..." 1>&2
    exit 1
fi

if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    echo "Environment variable AWS_ACCESS_KEY_ID is missing, exiting..." 1>&2
    exit 1
fi

if [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "Environment variable AWS_SECRET_ACCESS_KEY is missing, exiting..." 1>&2
    exit 1
fi

# Set default value
time_to_kill="${FORCE_KILL_TIME:-5s}"

# Do it
while true
do
	#start dumping
	timestamp=$(date +"%Y-%m-%dT%H-%M-%S")
	timeout -k $time_to_kill $REPORT_PERIOD airodump-ng $INTERFACE_DEVICE_NAME -b abg -w $timestamp --output-format csv 
    if [ $? -eq 1 ] 
    then 
        echo "Error when calling airodump-ng, exiting..." >&2
        exit 1
    fi

    fileName="$timestamp-01.csv"
	echo "uploading $fileName to $S3_BUCKET_TARGET"

    aws s3 cp $fileName $S3_BUCKET_TARGET/$fileName 
    if [ $? -eq 0 ] 
    then 
        echo "Uploaded successfully!" 
    else 
        echo "Could not upload to s3, exiting..." >&2
        exit 1
    fi
done 

