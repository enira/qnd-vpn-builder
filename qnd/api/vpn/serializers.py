from flask_restplus import fields
from api.restplus import api

setting = api.model('setting', {
    'key': fields.String(required=True, description='key'),
    'value': fields.String(required=True, description='value'),
})

user = api.model('user', {
    'username': fields.String(readOnly=True, description='Logged in user'),
})

system = api.model('system', {
    'cpu_load': fields.Integer(readOnly=True, description='CPU load (in percent)'),
    'cpu_num': fields.Integer(readOnly=True, description='Amount of cores'),
    'cpu_freq': fields.Integer(readOnly=True, description='CPU frequency (in MHz)'),
    'ram_max': fields.Integer(readOnly=True, description='Installed amount of RAM (in MB)'),
    'ram_used': fields.Integer(readOnly=True, description='RAM used (in MB)'),
    'ram_pct': fields.Integer(readOnly=True, description='RAM used (in percent)'),
    'root_disk_pct': fields.Integer(readOnly=True, description='Root Disk Free(in percent)'),
    'data_disk_pct': fields.Integer(readOnly=True, description='Data Disk Free(in percent)'),
})

network = api.model('network', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a network'),
    'name': fields.String(required=True, description='Name of the network'),
    'port': fields.Integer(required=True, description='Port used by the network'),
    'netmask': fields.Integer(required=True, description='Netmask used by the network'),
    'ip': fields.String(required=True, description='IP address'),
    'status': fields.String(required=True, description='Status'),
})

network_create = api.model('network_create', {
    'name': fields.String(required=True, description='Name of the network'),
    'password': fields.String(required=True, description='Password of the network'),
    'port': fields.Integer(required=True, description='Port used by the network'),
    'netmask': fields.Integer(required=True, description='Netmask used by the network'),
    'ip': fields.String(required=True, description='IP address'),
})

network_update = api.model('network_update', {
    'name': fields.String(required=False, description='Name of the network'),
    'password': fields.String(required=False, description='Password of the network'),
    'port': fields.Integer(required=False, description='Port used by the network'),
    'netmask': fields.Integer(required=False, description='Netmask used by the network'),
    'ip': fields.String(required=False, description='IP address'),
})



client = api.model('client', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a client'),
    'ip': fields.String(required=True, description='The IP of the client'),
    'type': fields.String(required=True, description='Client type'),
    'package': fields.String(required=True, description='Provisioned package'),
    'network_id': fields.Integer(required=True, description='Network id associated'), 
    'status': fields.String(required=True, description='Status'),
})

client_create = api.model('client_create', {
    'ip': fields.String(required=True, description='The IP of the client'),
    'type': fields.String(required=True, description='Client type'),
    'network_id': fields.Integer(required=True, description='Network id associated'), 
})

client_update = api.model('client_update', {
    'ip': fields.String(required=False, description='The IP of the client'),
    'type': fields.String(required=False, description='Client type'),
    'package': fields.String(required=False, description='Provisioned package'),
    'network_id': fields.Integer(required=False, description='Network id associated'), 
})


