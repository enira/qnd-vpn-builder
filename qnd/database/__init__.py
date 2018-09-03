from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

import logging.config
log = logging.getLogger(__name__)

db = SQLAlchemy()

VERSION = '1'

"""
    DB VERSIONS:
    ------------
    1       alpha-1                 current

"""

def assign(app):
    """
    Assign app to db context
    """
    db.app = app

def reset_database(app):
    """
    Resets the database
    """

    from database.models import User, Network, Log, Setting
    log.info('Creating database')

    # drop everything
    db.reflect(app=app)
    db.drop_all(app=app)

    # create again
    db.create_all(app=app)

def check_version(app):
    """
    Reads the version from the database and checks if the database needs to be updated
    """

    from database.models import User, Network, Log, Setting
    session = db.session

    # check version
    try:
        dbversion = session.query(Setting).filter(Setting.key == 'dbversion').one()
    except NoResultFound as e:
        # error no results
        dbversion = None
    except:
        # this is a call to create the database
        reset_database(app)
        dbversion = None

    # no database version to be found, let's create one
    if dbversion == None:
        log.info('No database version found, setting version to ' + VERSION)
        dbversion = Setting(key='dbversion', value=VERSION)

        session.add(dbversion)
        session.commit()
    
    log.info('Running database version: '  + dbversion.value)

    session.close()

    # checking database version
    if dbversion.value == VERSION:
        log.info('Database is up to date.')
    elif dbversion.value > VERSION:
        # hmmm, the database is newer than the application. I can't do anything with that
        log.info('Unrecoverable error: database version is higher than the application can use.')
        exit()
    else:
        # database is not up to date
        log.info('Database migration started.')

        # database migrations 




    

