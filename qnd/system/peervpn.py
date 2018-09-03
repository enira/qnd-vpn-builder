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

    def task_clients(self):
        session = db.session
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
            
            db.session.delete(network)
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
