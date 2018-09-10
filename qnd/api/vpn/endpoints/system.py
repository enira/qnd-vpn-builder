import os

from flask import request
from flask_restplus import Resource

from api.vpn.serializers import setting, network, network_update
from api.restplus import api

import logging.config
log = logging.getLogger(__name__)

ns = api.namespace('system', description='Operations related to system settings')


@ns.route('/setting')
@api.response(404, 'Error 404.')
class Settings(Resource):

    @api.marshal_with(setting)
    def get(self, setting_id):
        """
        Returns a setting.
        """
        # this is a todo
        return None

    @api.response(201, 'Setting successfully created.')
    @api.expect(setting)
    def post(self):
        """
        Creates a new setting.
        Use this method to create a new datastore.
        * Send a JSON object with the properties in the request body.
        ```
        {
          "name": "New datastore name",
          "username": "New datastore username",
          "password": "New datastore password",
          "host": "New datastore host",
          "type": "New datastore type"
        }
        ```
        """
        data = request.json
        create_datastore(data)
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
        delete_pool(id)
        return None, 204
