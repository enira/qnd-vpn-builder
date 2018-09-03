import threading
import datetime
import logging
import os 

import logging.config
log = logging.getLogger(__name__)

from apscheduler.schedulers.background import BackgroundScheduler
from system.bridge import Bridge
import configparser

from database import db
from database.models import Network

class PeerVPN(object):
    log = None

    """
    Internal flow of the application.
    """
    __lock = threading.Lock()
    __instance = None

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


    def initialize_scheduler(self):
        # null
        pass

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

        connection.disconnect()

    def add_network(self, network):
        connection = Bridge(self._hostname, self._username, self._password, self._local)

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
        #systemctl status peervpn137 | grep -i Active | awk '{print $2}'

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

    def build_client_pacakge(self, client):
        connection = Bridge(self._hostname, self._username, self._password, self._local)

        # prepare raspberry pi image for zero wireless
        if client.image == 'rzw':
            # copy the image
            result = connection.command('cp /opt/qndvpnbuilder/2018-06-27-raspbian-stretch-lite.img /tmp/image' + str(client.id) + '.img')

            # create the mount point
            connection.command('mkdir /tmp/image' + str(client.id))

            # finding the disk mount sector from the image
            result = connection.command('fdisk -lu /opt/qndvpnbuilder/2018-06-27-raspbian-stretch-lite.img | grep -i Linux | awk \'{ print $2 }\'')

            offset = 512 * int(result)

            # mount the image
            result = connection.sudo_command('mount -o loop,offset=' + str(offset) + ' /tmp/image' + str(client.id) + '.img', self._password)
            


            # add the peervpn.conf file

            # add the peervpn.service file

            # unmount the image

            # zip the image


        connection.disconnect()




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


    def _construct(self, lines):
        config = ""
        for line in lines:
            config = config + line + "\n"

        return config