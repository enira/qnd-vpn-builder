import os

from flask import request
from flask_restplus import Resource

from api.vpn.serializers import client, client_update, client_create
from api.vpn.business import create_client, update_client, delete_client
from api.restplus import api

import logging.config
log = logging.getLogger(__name__)

from database.models import Client
from database import db

ns = api.namespace('client', description='Operations related to clients')

@ns.route('/')
class ClientCollection(Resource):

    @api.marshal_list_with(client)
    def get(self):
        """
        Returns list of all clients.
        """
        clients = db.session.query(Client).all()
        return clients

    @api.response(201, 'Client successfully created.')
    @api.expect(client_create)
    def post(self):
        """
        Creates a new client.
        * Send a JSON object with the pool details request body.
        ```
        {
            todo
        }
        ```
        """
        data = request.json
        create_client(data)
        return None, 201

    
@ns.route('/<int:id>')
@api.response(404, 'Client not found.')
class ClientItem(Resource):

    @api.marshal_with(client)
    def get(self, id):
        """
        Returns a client.
        """
        return db.session.query(Client).filter(Client.id == id).one()
    
    @api.expect(client_update)
    @api.response(204, 'Client successfully updated.')
    def put(self, id):
        """
        Updates a client.
        * Send a JSON object with the new name in the request body.
        ```
        {
            todo
        }
        ```
        * Specify the ID of the network to modify in the request URL path.
        """
        data = request.json
        update_client(id, data)
        return None, 204

    @api.response(204, 'Client successfully deleted.')
    def delete(self, id):
        """
        Deletes a client.
        """
        delete_client(id)
        return None, 204

