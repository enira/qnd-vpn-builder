from database import db
from database.models import Network

import logging.config
log = logging.getLogger(__name__)


# Networks
def create_network(data):
    """
    Create a new network.
    """
    name = data.get('name')
    port = data.get('port')
    password = data.get('password')
    netmask = data.get('netmask')
    ip = data.get('ip')
    status = 'created'

    network = Network(name=name, 
                      port=port, 
                      netmask=netmask, 
                      ip=ip, status=status, 
                      password = password)

    db.session.add(network)
    db.session.commit()



def update_network(network_id, data):
    """
    Update a network
    """
    network = db.session.query(Network).filter(Network.id == network_id).one()

    if data.get('name') != None:
        name = data.get('name')
        network.name = name

    if data.get('port') != None:
        port = data.get('port')
        network.port = port

    if data.get('password') != None:
        password = data.get('password')
        network.password = password

    if data.get('netmask') != None:
        netmask = data.get('netmask')
        network.netmask = netmask

    if data.get('ip') != None:
        ip = data.get('ip')
        network.ip = ip

    network.status = 'updated'

    db.session.add(network)
    db.session.commit()

def delete_network(network_id):
    """
    Delete a network.
    """
    network = db.session.query(Network).filter(Network.id == network_id).one()
    network.status = 'deleted'
    db.session.add(network)
    db.session.commit()


# Clients
def create_client(data):
    """
    Create a new client.
    """
    ip = data.get('ip')
    type = data.get('type')
    package = data.get('package')
    network_id = data.get('network_id')
    network = db.session.query(Network).filter(Network.id == network_id).one()
    status = 'created'

    client = Client(ip=ip, 
                    type=type,
                    package=package,
                    network=network,
                    status=status)

    db.session.add(client)
    db.session.commit()



def update_client(client_id, data):
    """
    Update a client
    """
    client = db.session.query(Client).filter(Client.id == client_id).one()

    if data.get('name') != None:
        name = data.get('name')
        network.name = name

    if data.get('port') != None:
        port = data.get('port')
        network.port = port

    if data.get('password') != None:
        password = data.get('password')
        network.password = password

    if data.get('netmask') != None:
        netmask = data.get('netmask')
        network.netmask = netmask

    if data.get('ip') != None:
        ip = data.get('ip')
        network.ip = ip

    network.status = 'updated'

    db.session.add(network)
    db.session.commit()

def delete_client(client_id):
    """
    Delete a client.
    """
    client = db.session.query(Client).filter(Client.id == client_id).one()
    client.status = 'deleted'
    db.session.add(client)
    db.session.commit()

