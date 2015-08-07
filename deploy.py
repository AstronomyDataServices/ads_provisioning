import glob
import platform
import boto
import os
import time
import logging
import io
import ConfigParser

from fabric.api import run, sudo, put, env, require, local, task, lcd
from fabric.context_managers import cd, hide, settings, prefix
from fabric.contrib.console import confirm
from fabric.contrib.files import append, sed, comment, exists
from fabric.decorators import task, serial
from fabric.operations import prompt
from fabric.utils import puts, abort, fastprint


logging_conf = """[loggers]
keys=root, deploy

[handlers]
keys=consoleHandler, fileHandler, errorHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=ERROR
handlers=consoleHandler

[logger_deploy]
level=DEBUG
handlers=fileHandler, errorHandler, consoleHandler
qualname=deploy
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
handlers= fileHandler,  errorHandler, consoleHandler
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s
datefmt='%m/%d/%Y %I:%M:%S %p'

[handler_fileHandler]
class=handlers.RotatingFileHandler
args=('deploy.log','a','maxBytes=10000','backupCount=2, delay=True')
formatter=simpleFormatter
delay=True
level=DEBUG

[handler_errorHandler]
class=handlers.RotatingFileHandler
args=('deploy.log','a','maxBytes=10000','backupCount=2, delay=True')
formatter=simpleFormatter
delay=True
level=ERROR"""

log_conf_file = os.path.join(os.path.dirname(__file__), 'logging.conf')
if os.path.exists(log_conf_file):
    logging.config.fileConfig(log_conf_file)
else:
    logging.config.fileConfig(io.BytesIO(logging_conf))

# create logger
logger = logging.getLogger('deploy')
log = logger

# check to see if a config file exists, if not parse the config string above.
config_file = os.path.join(os.path.dirname(__file__), 'deploy.conf')
config = ConfigParser.RawConfigParser(allow_no_value=True)
if os.path.exists(config_file):
    config.read(config_file)
else:
    log.error('no config file found')

conf = config._sections['development']

if conf['debug'] == 'True':
    DEBUG_LEVEL = 'DEBUG'
else:
    DEBUG_LEVEL = 'INFO'

log.setLevel(DEBUG_LEVEL)
log.debug('config -> ' + str(conf))

#log.info('testicles')
