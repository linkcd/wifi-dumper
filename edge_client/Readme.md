## Hardward
- Raspberry PI 
- Wifi alfa awus036ach

## OS
This image was built for Raspberry pi 3b with debian "buster" (32bit version)
-----

## Install driver
ref: https://forums.raspberrypi.com/viewtopic.php?f=28&t=192985&p=1522188&hilit=awus036ach#p1522188
```bash
# to download
sudo wget http://downloads.fars-robotics.net/wifi-drivers/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi

# to install
sudo install-wifi
```

## Install tools
### 1. [Aircrack-ng](https://www.aircrack-ng.org/)
#### Install [pre-compiled aircrack-ng](https://www.aircrack-ng.org/doku.php?id=install_aircrack#installing_pre-compiled_binaries)
- Enable packages https://packagecloud.io/aircrack-ng/release/install
- Install package 
```bash
apt-get install aircrack-ng 
```

## Ensure wifi adapter are enabled correctly
### 1. Get device name
```bash
iwconfig
```
Write down the name of the wifi adapter, in this case it is wlan1

### 2. Set into monitor mode 
```bash
ifconfig wlan1 down
iwconfig wlan1 mode monitor
ifconfig wlan1 up
iwconfig
```
Its mode should be **monitor**, with default frequency 2.4G or 5G

----
## Build wifi dumper docker image from source code
```bash
# build
docker build -t linkcd/wifidumper-runner:buster .

# publish to dockerhub
docker login
docker push linkcd/wifidumper-runner:buster
```
I have uploaded it to dockerhub, feel free to build and use your own image.

## Run wifi dumper docker image
```bash
sudo docker run --net="host" --privileged --restart always -e REPORT_PERIOD="30m" -e INTERFACE_DEVICE_NAME="wlan1" -e FORCE_KILL_TIME="5s" -e S3_BUCKET_TARGET_AP="<YOUR_OWN_VALUE>" -e S3_BUCKET_TARGET_CLIENT="<YOUR_OWN_VALUE>"  -e AWS_ACCESS_KEY_ID="<YOUR_OWN_VALUE>" -e AWS_SECRET_ACCESS_KEY="<YOUR_OWN_VALUE>" <YOUR_IMAGE_NAME>
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