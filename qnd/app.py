import os
from flask import Flask, Blueprint, request, send_from_directory, redirect

import settings

# enpoint binding
from api.vpn.endpoints.system import ns as vpn_system_namespace
from api.vpn.endpoints.ui import ns as vpn_ui_namespace
from api.vpn.endpoints.networks import ns as vpn_networks_namespace

from api.restplus import api

# import database
from database import db
import database

from system.peervpn import PeerVPN

# setting logging
import logging.config
# logging.config.fileConfig(os.path.join(os.path.dirname(os.path.realpath(__file__)),'logging.conf'), disable_existing_loggers=False)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# flask
app = Flask(__name__)

database.assign(app)

app.secret_key = settings.secret_key()

app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
#app.config['SQLALCHEMY_POOL_SIZE'] = settings.SQLALCHEMY_POOL_SIZE
#app.config['SQLALCHEMY_MAX_OVERFLOW'] = settings.SQLALCHEMY_MAX_OVERFLOW
app.config['SESSION_TYPE'] = settings.SESSION_TYPE


db.init_app(app)

blueprint = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint)

api.add_namespace(vpn_system_namespace)
api.add_namespace(vpn_ui_namespace)
api.add_namespace(vpn_networks_namespace)

app.register_blueprint(blueprint)

def initialize_app():
    """
    Initialize the application
    """
    log.info('Initializing application...')
    # TODO: add app specific things

    # check database version and mirate if needed
    database.check_version(app)

    # init PeerVPN application
    PeerVPN.instance().init()

    # Check and start all services in database
    PeerVPN.instance().initialize_networks()

    # Initialize the scheduler
    PeerVPN.instance().initialize_scheduler()

    log.info('Done.')

@app.route('/')
def index():
    """
    Default route, redirects to the gui index.html page
    """
    return redirect('gui/index.html')

@app.route('/gui/<path:path>')
def send_gui(path):
    """
    Handler for GUI component.
    Only used by test, in production overridden by nginx
    """
    return send_from_directory('gui', path)

def main():
    """
    Main running configuration
    """

    log.info('>>>>> Starting server <<<<<')
    try:
        # run flask
        app.run(port=8080, host='0.0.0.0', debug=settings.FLASK_DEBUG, use_reloader=False)
    except:
        log.error('That \'s an uncaught error.')

# initialize application
initialize_app()

if __name__ == "__main__":
    main()
