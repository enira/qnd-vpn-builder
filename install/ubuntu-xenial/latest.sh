!#/bin/bash

# install from
# wget -O - https://raw.githubusercontent.com/enira/qnd-vpn-builder/install/deploy/ubuntu-xenial/latest.sh | sudo bash

# update operating system
apt-get update
apt-get -y upgrade

# install all needed packages
apt-get -y install python python-pip build-essential libssl-dev libffi-dev python-dev git nginx unzip wget

# create the vpn builder folder
mkdir -p /opt/qndvpnbuilder/

# download latest 
wget https://github.com/enira/qnd-vpn-builder/archive/master.zip -O /opt/qndvpnbuilder/latest.zip
unzip /opt/qndvpnbuilder/latest.zip -d /opt/qndvpnbuilder/
rm /opt/qndvpnbuilder/latest.zip
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/qnd /opt/qndvpnbuilder/qnd

# install requirements
pip install -r /opt/qndvpnbuilder/qnd/requirements.txt 

# move nginx file
mv /opt/qndvpnbuilder/qnd-vpn-builder-master/install/ubuntu-xenial/nginx.conf /etc/nginx/nginx.conf

# starting nginx
systemctl restart nginx

# on boot 
systemctl enable nginx

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
mkdir -p /opt/qndvpnbuilder/data/deploy

# mark it as compressed
chattr +c /opt/qndvpnbuilder/data/deploy

systemctl start qnd
systemctl enable qnd

rm -rf /opt/qndvpnbuilder/qnd-vpn-builder-master