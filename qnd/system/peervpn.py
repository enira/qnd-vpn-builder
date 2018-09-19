import threading
import datetime
import logging
import os 

import uuid
import json

import logging.config
log = logging.getLogger(__name__)

from apscheduler.schedulers.background import BackgroundScheduler
from system.bridge import Bridge
import configparser

from database import db
from database.models import Network, Client

class PeerVPN(object):
    log = None

    """
    Internal flow of the application.
    """
    __lock = threading.Lock()
    __instance = None

    _delay = 0

    _local = False
    _username = None
    _password = None
    _hostname = None


    @classmethod
    def instance(cls):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = cls()

        return cls.__instance

    _scheduler = None

    def init(self):
        # checking if debug
        if os.path.isfile('config.ini'):
            # load the external mover
            config = configparser.ConfigParser()
            config.read('config.ini')
            self._local = False

            self._hostname = config['debug']['hostname']
            self._username = config['debug']['username']
            self._password = config['debug']['password']
        else:
            self._local = True

    def download(self, path):
        session = db.session
        value = None

        # get all clients that require creation
        clients = session.query(Client).filter(Client.key == path).all()
        if len(clients) == 0:
            value = None

        for package in clients:
            value = package.package

        session.close()

        return value

    def initialize_scheduler(self):
        """
        Initialize the schedulere. Create all tasks that need to be runned.
        """

        log.info("Creating scheduler...")
        # initialize the scheduler
        self._scheduler = BackgroundScheduler()

        # run
        self._scheduler.add_job(self.task_networks, 'cron', minute='*', second='*/5', id='task_networks', max_instances=1, coalesce=True)
        self._scheduler.add_job(self.task_clients, 'cron', minute='*', second='*/5', id='task_clients', max_instances=1, coalesce=True)

        self._scheduler.start()

        log.info('Scheduler initialized')

    def initialize_networks(self):
        # read from database
        session = db.session
        networks = session.query(Network).all()
        for network in networks:
            print(network.id)
            # with each network check the health
            self.status_network(network)

        session.close()

    def status_network(self, network):
        connection = Bridge(self._hostname, self._username, self._password, self._local)
        result = connection.sudo_command('systemctl status peervpn' + str(network.id) + ' | grep -i Active: | awk \'{ print $2 }\'', self._password)


        connection.disconnect()

        return str(result[len(result) - 1])

    def add_network(self, network):
        connection = Bridge(self._hostname, self._username, self._password, self._local)

        # small fix
        result = connection.sudo_command('mkdir /etc/peervpn', self._password)

        # check if the service exists
        

        result = connection.sudo_command('[ -f /etc/peervpn/peervpn' + str(network.id) + '.conf ] && echo 1 || echo 0', self._password)
        if result[1][0] == 48:
            # config file does not exists
            contents = self._generate_config(network)
            result = connection.command('echo -e \"' + contents + '\" >> /tmp/peervpn' + str(network.id) + '.conf')
            result = connection.sudo_command('mv /tmp/peervpn' + str(network.id) + '.conf /etc/peervpn/peervpn' + str(network.id) + '.conf', self._password)

        # add service
        result = connection.sudo_command('[ -f /etc/systemd/system/peervpn' + str(network.id) + '.service ] && echo 1 || echo 0', self._password)
        if result[1][0] == 48:
            # config file does not exists
            contents = self._generate_service(network)
            result = connection.sudo_command('echo -e \"' + contents + '\" >> /tmp/peervpn' + str(network.id) + '.service', self._password)
            result = connection.sudo_command('mv /tmp/peervpn' + str(network.id) + '.service /etc/systemd/system/peervpn' + str(network.id) + '.service', self._password)

        # reload daemons (just to be sure)
        result = connection.sudo_command('systemctl daemon-reload', self._password)

        # start service
        result = connection.sudo_command('systemctl start peervpn' + str(network.id) + '.service', self._password)

        # check if started
        result = connection.sudo_command('systemctl status peervpn' + str(network.id) + '  | grep -i Active | awk \'{print $2}\' ', self._password)

        connection.disconnect()

    def remove_network(self, network):
        connection = Bridge(self._hostname, self._username, self._password, self._local)

        # stop service
        result = connection.sudo_command('systemctl stop peervpn' + str(network.id) + '.service', self._password)

        # check if stopped
        result = connection.sudo_command('systemctl status peervpn' + str(network.id) + ' | grep -i Active | awk \'{print $2}\'', self._password)

        # remove service
        result = connection.sudo_command('rm /etc/systemd/system/peervpn' + str(network.id) + '.service', self._password)
        result = connection.sudo_command('rm /etc/peervpn/peervpn' + str(network.id) + '.conf', self._password)

        # reload daemons
        result = connection.sudo_command('systemctl daemon-reload', self._password)

        connection.disconnect()

    def redeploy_network(self, network):
        self.remove_network(network)
        self.add_network(network)

    def build_client_pacakge(self, client, session):
        connection = Bridge(self._hostname, self._username, self._password, self._local)

        # prepare raspberry pi image for zero wireless
        if client.type == 'rzw' or client.type == 'rz':
            client.status = "copying"
            session.add(client)
            session.commit()

            # finding the disk mount sector from the image
            result = connection.command('fdisk -lu /opt/qndvpnbuilder/data/bin/2018-06-27-raspbian-stretch-lite.img | grep -i Linux | awk \'{ print $2 }\'')

            offset = 512 * int(result[0])

            # copy the image
            result = connection.sudo_command('cp /opt/qndvpnbuilder/data/bin/2018-06-27-raspbian-stretch-lite.img /opt/qndvpnbuilder/data/tmp/image' + str(client.id) + '.img', self._password)

            client.status = "compiling"
            session.add(client)
            session.commit()

            # create the mount point
            connection.sudo_command('mkdir /tmp/image' + str(client.id), self._password)

            # mount the image
            result = connection.sudo_command('mount -o loop,offset=' + str(offset) + ' /opt/qndvpnbuilder/data/tmp/image' + str(client.id) + '.img /tmp/image' + str(client.id), self._password)

            # create the config file folder
            result = connection.sudo_command('mkdir /tmp/image' + str(client.id) + '/etc/peervpn/', self._password)

            # add the peervpn.conf file
            contents = self._generate_client(client, self._hostname)
            result = connection.sudo_command('echo -e \"' + contents + '\" >> /tmp/client_peervpn' + str(client.id) + '.conf', self._password)
            result = connection.sudo_command('mv /tmp/client_peervpn' + str(client.id) + '.conf /tmp/image' + str(client.id) + '/etc/peervpn/peervpn.conf', self._password)

            # add the peervpn.service file
            contents = self._generate_client_service()
            result = connection.sudo_command('echo -e \"' + contents + '\" >> /tmp/client_peervpn' + str(client.id) + '.service', self._password)
            result = connection.sudo_command('mv /tmp/client_peervpn' + str(client.id) + '.service /tmp/image' + str(client.id) + '/etc/systemd/system/peervpn.service', self._password)

            # add the rc.local file
            contents = self._generate_rc_local()
            result = connection.sudo_command('echo -e \"' + contents + '\" >> /tmp/client_rclocal' + str(client.id) , self._password)
            result = connection.sudo_command('mv /tmp/client_rclocal' + str(client.id) + ' /tmp/image' + str(client.id) + '/etc/rc.local', self._password)

            # add raspberry pi executables
            #result = connection.sudo_command('cp /opt/qndvpnbuilder/data/bin/peervpn/arm/peervpn /tmp/image' + str(client.id) + '/usr/local/bin/peervpn', self._password)

            if client.type == 'rzw':
                # zero wifi
                arguments = json.loads(client.arguments)
                contents = self._generate_wpa_supplicant(arguments["ssid"], arguments["password"])

                result = connection.sudo_command('echo -e \"' + contents + '\" >> /tmp/client_wpa' + str(client.id) , self._password)
                result = connection.sudo_command('mv /tmp/client_wpa' + str(client.id) + ' /tmp/image' + str(client.id) + '/etc/wpa_supplicant/wpa_supplicant.conf', self._password)

            # unmount the image
            result = connection.sudo_command('umount /tmp/image' + str(client.id) , self._password)
            
            client.status = "compressing"
            session.add(client)
            session.commit()

            # zip the image
            result = connection.sudo_command('zip /opt/qndvpnbuilder/data/tmp/image' + str(client.id) + '.zip /opt/qndvpnbuilder/data/tmp/image' + str(client.id) + '.img', self._password)

            # move the zip file
            package = str(uuid.uuid4())

            result = connection.sudo_command('mv /opt/qndvpnbuilder/data/tmp/image' + str(client.id) + '.zip /opt/qndvpnbuilder/data/deploy/packages/' + package + '.zip' , self._password)
            client.package = package
            client.key = str(uuid.uuid4())
            client.status = "cleanup"
            session.add(client)
            session.commit()

            # remove the temp image file
            result = connection.sudo_command('rm /opt/qndvpnbuilder/data/tmp/image' + str(client.id) + '.img', self._password)


        connection.disconnect()

    def _generate_wpa_supplicant(self, ssid, password):
        return self._construct([
            "network={",
            "    ssid=\"" + ssid + "\"",
            "    psk=\"" + password + "\"",
            "}"
            ])

    def _generate_client(self, client, public_ip):
        return self._construct([
            "networkname " + client.network.name,
            "psk " + client.network.password,
            "port "+ str(client.network.port),
            "initpeers " + public_ip + " " + str(client.network.port),
            "interface peervpn0" ,
            "ifconfig4 " + client.ip + "/" + str(client.network.netmask)
            ])

    def _generate_config(self, network):

        return self._construct([
            "networkname " + network.name,
            "psk " + network.password,
            "port "+ str(network.port),
            "enabletunneling yes",
            "interface peervpn" + str(network.id),
            "ifconfig4 " + network.ip + "/" + str(network.netmask)
            ])

    def _generate_service(self, network):
        return self._construct([
            "[Unit]",
            "Description=PeerVPN " + str(network.id) + " network service",
            "Wants=network-online.target",
            "After=network-online.target",
            "",
            "[Service]",
            "ExecStart=/usr/local/bin/peervpn /etc/peervpn/peervpn" + str(network.id) + ".conf",
            "",
            "[Install]",
            "WantedBy=multi-user.target"
            ])

    def _generate_client_service(self):
        return self._construct([
            "[Unit]",
            "Description=PeerVPN network service",
            "Wants=network-online.target",
            "After=network-online.target",
            "",
            "[Service]",
            "ExecStart=/usr/local/bin/peervpn /etc/peervpn/peervpn.conf",
            "",
            "[Install]",
            "WantedBy=multi-user.target"
            ])

    def _generate_rc_local(self):
        return self._construct([
            '#!/bin/sh -e',
            '',
            'FILE=\\"/home/pi/.initialized\\"',
            '',
            'if [ -f \\"\\$FILE\\" ];',
            'then',
            '   echo \\"Client bootstrapped.\\"',
            'else',
            '   echo \\"Preparing...\\"',
            '   apt-get update',
            '   apt-get -y upgrade',
            '   apt install -y libssl1.0-dev',
            '   cd /tmp',
            '   wget https://peervpn.net/files/peervpn-0-044.tar.gz',
            '   tar xzvf peervpn*',
            '   cd /tmp/peervpn-0-044',
            '   make',
            '   make install',
            '   cp /tmp/peervpn*/peervpn /usr/local/bin',
            '   systemctl enable peervpn',
            '   touch /home/pi/.initialized',
            '   echo \\"Done.\\"',
            '   reboot',
            'fi',
            '',
            'exit 0'
            ])

    def _construct(self, lines):
        config = ""
        for line in lines:
            config = config + line + "\n"

        return config

    def task_clients(self):
        session = db.session

        # get all clients that require creation
        created = session.query(Client).filter(Client.status == "pending").all()
        for client in created:
            client.status = "building"
            db.session.add(client)
            db.session.commit()

            self.build_client_pacakge(client, session)
            client.status = "ready"

            db.session.add(client)
            db.session.commit()

        session.close()

    def task_networks(self):
        """
        Check up on tasks
        """
        session = db.session
        # get all networks that require creation
        created = session.query(Network).filter(Network.status == "created").all()
        for service in created:
            service.status = "creating"
            db.session.add(service)
            db.session.commit()

            self.add_network(service)
            service.status = "healthy"

            db.session.add(service)
            db.session.commit()

        # get all networks that require redeploy
        updated = session.query(Network).filter(Network.status == "updated").all()
        for service in updated:
            service.status = "updating"
            db.session.add(service)
            db.session.commit()

            self.redeploy_network(service)
            service.status = "healthy"
            db.session.add(service)
            db.session.commit()

        # get all networks that require deleting
        deleted = session.query(Network).filter(Network.status == "deleted").all()
        for service in deleted:
            service.status = "deleting"
            db.session.add(service)
            db.session.commit()

            self.remove_network(service)
            
            db.session.delete(service)
            db.session.commit()

        self._delay = self._delay + 1

        if self._delay > 6:
            self._delay = 0
            # check health of networks
            all = session.query(Network).all()
            for network in all:
                if self.status_network(network) != "b'active'":
                    network.status = "failed"
                    db.session.add(network)
                    db.session.commit()

        session.close()
