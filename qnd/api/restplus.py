import traceback
import os
import sys

from flask_restplus import Api
import settings

import logging.config
log = logging.getLogger(__name__)

api = Api(version='alpha-1', title='Quick \'n Dirty VPN builder', description='Quick \'n Dirty VPN builder API')

@api.errorhandler
def default_error_handler(e):
    """
    Default error handler
    """
    message = 'An unhandled exception occurred.'
    
    # if debug mode, expand error (always there for alpha releases)
    if settings.FLASK_DEBUG:
        message = "";
        exc_type, exc_value, exc_traceback = sys.exc_info()
        message = message + "\n*** format_exc, first and last line:"
        formatted_lines = traceback.format_exc().splitlines()
        message = message + formatted_lines[0]
        message = message + formatted_lines[-1]
        message = message + "\n*** format_exception:"
        message = message + repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback))
        message = message + "\n*** extract_tb:"
        message = message + repr(traceback.extract_tb(exc_traceback))
        message = message + "\n*** format_tb:"
        message = message + repr(traceback.format_tb(exc_traceback))
        message = message + "\n*** tb_lineno:", exc_traceback.tb_lineno

    log.exception(message)
    return {'message': message}, 500


