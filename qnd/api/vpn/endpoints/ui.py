import psutil
from sys import platform

import copy

from flask import request
from flask_restplus import Resource

from api.vpn.serializers import system 
from api.restplus import api


import logging.config
log = logging.getLogger(__name__)

ns = api.namespace('ui', description='Operations related to ui')
    
@ns.route('/system')
@api.response(404, 'Statistics not found.')
class SystemItem(Resource):

    @api.marshal_with(system)
    def get(self):
        """
        Returns System stats.
        """
        cpu_max = None
        if 'linux' in platform:
            # for Linux VMs the code cannot find the maximum CPU speed :(
            cpu_max = 0
        else:
            cpu_max = psutil.cpu_freq().max

        try:
            root_disk_pct = psutil.disk_usage('/')[3]
        except:
            root_disk_pct = 25
        
        try:
            data_disk_pct = psutil.disk_usage('/opt/qndvpnbuilder/data')[3]
        except:
            data_disk_pct = 25

        obj = type('',(object,),{"cpu_load": psutil.cpu_percent() ,
                                 "ram_pct": psutil.virtual_memory().percent ,
                                 "ram_used": psutil.virtual_memory().used,
                                 "ram_max": psutil.virtual_memory().total,
                                 "cpu_num": psutil.cpu_count(logical=False),
                                 "cpu_freq": cpu_max,
                                 "root_disk_pct": root_disk_pct,
                                 "data_disk_pct": data_disk_pct,
                                })()

        return obj