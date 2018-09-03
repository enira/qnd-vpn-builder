import os

from flask import request
from flask_restplus import Resource

from api.vpn.serializers import network, network_update, network_create
from api.vpn.business import create_network, update_network, delete_network
from api.restplus import api

import logging.config
log = logging.getLogger(__name__)

from database.models import Network
from database import db

ns = api.namespace('network', description='Operations related to networks')

@ns.route('/')
class NetworkCollection(Resource):

    @api.marshal_list_with(network)
    def get(self):
        """
        Returns list of all networks.
        """
        networks = db.session.query(Network).all()
        return networks

    @api.response(201, 'Network successfully created.')
    @api.expect(network_create)
    def post(self):
        """
        Creates a new network.
        * Send a JSON object with the network details request body.
        ```
        {
            'name': 'Name of the network'
            'password': 'Password of the network'
            'port': 'Port used by the network'
            'netmask': 'Netmask used by the network'
            'ip': 'IP address'
        }
        ```
        """
        data = request.json
        create_network(data)
        return None, 201

    
@ns.route('/<int:id>')
@api.response(404, 'Client not found.')
class NetworkItem(Resource):

    @api.marshal_with(network)
    def get(self, id):
        """
        Returns a network.
        """
        return db.session.query(Network).filter(Network.id == id).one()
    
    @api.expect(network_update)
    @api.response(204, 'Network successfully updated.')
    def put(self, id):
        """
        Updates a network.
        * Send a JSON object with the new name in the request body.
        ```
        {
            'name': 'Name of the network'
            'password': 'Password of the network'
            'port': 'Port used by the network'
            'netmask': 'Netmask used by the network'
            'ip': 'IP address'
        }
        ```
        * Specify the ID of the network to modify in the request URL path.
        """
        data = request.json
        update_network(id, data)
        return None, 204

    @api.response(204, 'Network successfully deleted.')
    def delete(self, id):
        """
        Deletes a network.
        """
        delete_network(id)
        return None, 204
