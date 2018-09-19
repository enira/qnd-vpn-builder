#!/bin/bash

# update operating system
apt-get update
apt-get -y upgrade

# install all needed packages
apt-get -y install python3 python3-pip build-essential libssl-dev libffi-dev python-dev git nginx unzip wget zip

# create the vpn builder folder
mkdir -p /opt/qndvpnbuilder/

# download latest 
wget https://github.com/enira/qnd-vpn-builder/archive/master.zip -O /opt/qndvpnbuilder/latest.zip
unzip /opt/qndvpnbuilder/latest.zip -d /opt/qndvpnbuilder/
rm /opt/qndvpnbuilder/latest.zip
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/qnd /opt/qndvpnbuilder/qnd

# install requirements
pip3 install -r /opt/qndvpnbuilder/qnd/requirements.txt 

# move nginx file
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/install/ubuntu-xenial/nginx.conf /etc/nginx/nginx.conf

# starting nginx
systemctl restart nginx

# on boot 
systemctl enable nginx

# create the service user
adduser --system --no-create-home --group qnd

# chown folder
chown -R qnd:qnd /opt/qndvpnbuilder/qnd/

# create a log folder for the service 
mkdir -p /var/log/qnd/
chown qnd:qnd /var/log/qnd/
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/install/ubuntu-xenial/qnd.service /etc/systemd/system/qnd.service

# create the data directory
mkdir -p /opt/qndvpnbuilder/data

# create the data image
dd if=/dev/zero of=/opt/qndvpnbuilder/data.img bs=1 count=0 seek=10G

# create a btrfs file system
mkfs.btrfs -m single /opt/qndvpnbuilder/data.img

# mount the file system
mount -o loop -t btrfs /opt/qndvpnbuilder/data.img /opt/qndvpnbuilder/data

# make data folder
mkdir -p /opt/qndvpnbuilder/data/deploy/packages
mkdir -p /opt/qndvpnbuilder/data/bin
mkdir -p /opt/qndvpnbuilder/data/tmp

# change ownership
chown qnd:qnd /opt/qndvpnbuilder/data/deploy
chown qnd:qnd /opt/qndvpnbuilder/data/bin
chown qnd:qnd /opt/qndvpnbuilder/data/tmp

# mark it as compressed
chattr +c /opt/qndvpnbuilder/data/deploy
chattr +c /opt/qndvpnbuilder/data/bin
chattr +c /opt/qndvpnbuilder/data/tmp

# move the binary files - peervpn arm
mkdir -p /opt/qndvpnbuilder/data/bin/peervpn/arm/
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/resources/peervpn/arm/peervpn /opt/qndvpnbuilder/data/bin/peervpn/arm/peervpn

# move the binary files - peervpn win32
mkdir -p /opt/qndvpnbuilder/data/bin/peervpn/win32/
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/resources/peervpn/win32/peervpn.exe /opt/qndvpnbuilder/data/bin/peervpn/win32/peervpn.exe

# move the binary files - etcher
mkdir -p /opt/qndvpnbuilder/data/bin/etcher/
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/resources/etcher/Etcher-Portable-1.4.4-x64.exe /opt/qndvpnbuilder/data/bin/etcher/Etcher-Portable-1.4.4-x64.exe
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/resources/etcher/Etcher-Portable-1.4.4-x86.exe /opt/qndvpnbuilder/data/bin/etcher/Etcher-Portable-1.4.4-x86.exe

# download the latest raspberry pi image
wget http://director.downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-06-29/2018-06-27-raspbian-stretch-lite.zip -O /opt/qndvpnbuilder/data/bin/2018-06-27-raspbian-stretch-lite.zip 
unzip /opt/qndvpnbuilder/data/bin/2018-06-27-raspbian-stretch-lite.zip -d /opt/qndvpnbuilder/data/bin/
rm /opt/qndvpnbuilder/data/bin/2018-06-27-raspbian-stretch-lite.zip

# download the peervpn binaries
wget https://peervpn.net/files/peervpn-0-044-linux-x86.tar.gz -O /tmp/peervpn-0-044-linux-x86.tar.gz
cd /tmp

# unpack
tar xzvf /tmp/peervpn*

# copy the binaries
mkdir /etc/peervpn
cp /tmp/peervpn*/peervpn /usr/local/bin
cp /tmp/peervpn*/peervpn.conf /etc/peervpn/

# copy the binary files - peervpn x64
mkdir -p /opt/qndvpnbuilder/data/bin/peervpn/x64/
cp /tmp/peervpn*/peervpn /opt/qndvpnbuilder/data/bin/peervpn/x64
	
# cleanup
rm -rf /tmp/peervpn
rm -rf /opt/qndvpnbuilder/qnd-vpn-builder-master

# setting rights
chown -R qnd:qnd qndvpnbuilder/

# start the service
systemctl start qnd
systemctl enable qnd
