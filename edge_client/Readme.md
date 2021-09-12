# Hardward
- Raspberry PI 
- Wifi alfa

# OS
This image was built for Raspberry pi 3b with debian "buster" (32bit version)

# Run
```bash
docker run --net="host" --privileged -e REPORT_PERIOD="10s" -e INTERFACE_DEVICE_NAME="wlan1" -e FORCE_KILL_TIME="5s" -e S3_BUCKET_TARGET_AP="<YOUR_OWN_VALUE>" -e S3_BUCKET_TARGET_CLIENT="<YOUR_OWN_VALUE>"  -e AWS_ACCESS_KEY_ID="<YOUR_OWN_VALUE>" -e AWS_SECRET_ACCESS_KEY="<YOUR_OWN_VALUE>" <YOUR_IMAGE_NAME>
```
### Enable PI to have access to wifi interface
```bash
--net="host" --privileged 
```
### Environment variables
#### Mandatory Environment Variables
- **REPORT_PERIOD**: The report time window of airodump-ng. One log file will be generated for each REPORT_PERIOD. Example value: "30m"
- **INTERFACE_DEVICE_NAME**: the name of wifi device. Example value: "wlan1"
- **S3_BUCKET_TARGET_AP**: Where to store the log files of AP. Example value: "s3://wifidumper/raw/AP". No need to append "/" at the end.
- **S3_BUCKET_TARGET_CLIENT**: Where to store the log files of Client. Example value: "s3://wifidumper/raw/Client". No need to append "/" at the end.
- **AWS_ACCESS_KEY_ID**: Your AWS access key
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret

#### Optional Environment Variables
- **FORCE_KILL_TIME**: Time to force kill the airodump-ng progress after timeout. Default value "5s".