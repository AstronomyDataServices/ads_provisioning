import os
import logging
import io
import ConfigParser
import logging.config

from fabric.api import run, env
from fabric.decorators import task

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

# env.hosts = [config._sections['env']['hosts']]
env.os_auth_url = config.get('env', 'os_auth_url')
env = [config._sections['env']][0]
log.debug(env)


@task
def test_task():
    result = run('ls -l')
    log.debug(result)


@task
def spawn_vm():
    """Spawn a vanilla instance of Ubuntu"""

    try:
        result = run("nova --os-auth-url " + env['os_auth_url'] + "\
            --os-tenant-id " + env['os_tenant_id'] + "\
            --os-tenant-name " + env['os_tenant_name'] + "\
            --os-username " + env['os_username'] + "\
            --os-password " + env['os_password'] + "\
            boot --image " + env['image'] + "\
            --flavor " + env['flavor'] + "\
            --availability-zone " + env['availability_zone'] + "\
            --security-groups " + env['security_groups'] + "\
            --key-name " + env['key_name'] + " " + env['image_name'])
        log.debug(result)
    except:
        log.exception('Failed to spawn virtual machine :: ')


if __name__ == "__main__":
    # execute only if run as a script
    spawn_vm()
