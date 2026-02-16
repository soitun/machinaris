import logging
import os
import pytz
import re

from flask import Flask, request
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event

from web.default_settings import DefaultConfig

from common.config import globals

app = Flask(__name__)
app.secret_key = b'$}#P)eu0A.O,s0Mz'
app.config.from_object(DefaultConfig)
# Override config with optional settings file
app.config.from_envvar('WEB_SETTINGS_FILE', silent=True)

def get_locale():
    try:
        accept = request.headers['Accept-Language']
        match = request.accept_languages.best_match(app.config['LANGUAGES'])
        # Workaround for dumb babel match method suggesting 'en' for 'nl' instead of 'nl_NL'
        if match == 'en' and not accept.startswith('en'):
            first_accept = accept.split(',')[0]  # Like 'nl'
            alternative = "{0}_{1}".format(first_accept, first_accept.upper())
            if alternative in app.config['LANGUAGES']:
                return alternative
        app.logger.debug("INIT: Accept-Language: {0}  ---->  matched locale: {1}".format(accept, match))
    except:
        app.logger.debug("INIT: Request had no Accept-Language, returning default locale of en.")
    return request.accept_languages.best_match(app.config['LANGUAGES'])

babel = Babel(app, locale_selector=get_locale,)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

db = SQLAlchemy(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

app.logger.debug("CONTROLLER_HOST={0}".format(app.config['CONTROLLER_HOST']))

# Blueprints
from web.blueprints.landing import landing_bp
from web.blueprints.setup import setup_bp
from web.blueprints.index import index_bp
from web.blueprints.controller import controller_bp
from web.blueprints.plotting import plotting_bp
from web.blueprints.farming import farming_bp
from web.blueprints.alerts import alerts_bp
from web.blueprints.wallet import wallet_bp
from web.blueprints.keys import keys_bp
from web.blueprints.workers import workers_bp
from web.blueprints.drives import drives_bp
from web.blueprints.blockchains import blockchains_bp
from web.blueprints.connections import connections_bp
from web.blueprints.pools import pools_bp
from web.blueprints.settings import settings_bp
from web.blueprints.logs import logs_bp
from web.blueprints.transactions import transactions_bp

app.register_blueprint(landing_bp)
app.register_blueprint(setup_bp)
app.register_blueprint(index_bp)
app.register_blueprint(controller_bp)
app.register_blueprint(plotting_bp)
app.register_blueprint(farming_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(keys_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(drives_bp)
app.register_blueprint(blockchains_bp)
app.register_blueprint(connections_bp)
app.register_blueprint(pools_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(transactions_bp)

# Jinja template filters
@app.template_filter()
def bytesfilter(num, suffix='B'):
    """Convert a number of bytes to a human-readable format."""
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.0f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.0f %s%s" % (num, 'Yi', suffix)

app.jinja_env.filters['bytesfilter'] = bytesfilter

def datetimefilter(value, format="%Y-%m-%d %H:%M"):
    if value:
        #app.logger.info("{0} => {1}".format(value, value.strftime(format)))
        return value.strftime(format)
    else:
        return ""

app.jinja_env.filters['datetimefilter'] = datetimefilter

def timesecondstrimmer(value):
    if value:
        #app.logger.info("{0} => {1}".format(value, value.strftime(format)))
        return value[:value.rindex(':')]
    else:
        return ""

app.jinja_env.filters['timesecondstrimmer'] = timesecondstrimmer

def plotnameshortener(value):
    return value[:30]

app.jinja_env.filters['plotnameshortener'] = plotnameshortener

def launcheridshortener(value):
    #app.logger.info("Shorten: {0}".format(value))
    return value[:12] + '...'

app.jinja_env.filters['launcheridshortener'] = launcheridshortener

def alltheblocks_blockchainlink(blockchain):
   alltheblocks_blockchain = globals.get_alltheblocks_name(blockchain)
   return 'https://alltheblocks.net/{0}'.format(alltheblocks_blockchain)

app.jinja_env.filters['alltheblocks_blockchainlink'] = alltheblocks_blockchainlink

def alltheblocks_blocklink(block, blockchain):
    if blockchain == 'mmx':
        return block # No support at ATB for MMX, so don't link it
    alltheblocks_blockchain = globals.get_alltheblocks_name(blockchain)
    return '<a href="https://alltheblocks.net/{0}/block/0x{1}" class="text-white" target="_blank">{1}</a>'.format(alltheblocks_blockchain, block)

app.jinja_env.filters['alltheblocks_blocklink'] = alltheblocks_blocklink

def escape_single_quotes(value):
    return value.replace("'", "\\'")

app.jinja_env.filters['escape_single_quotes'] = escape_single_quotes