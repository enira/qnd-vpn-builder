from flask_restplus import fields
from api.restplus import api

setting = api.model('setting', {
    'key': fields.String(required=True, description='key'),
    'value': fields.String(required=True, description='value'),
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



