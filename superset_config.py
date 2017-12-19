# Sample superset_config.py file
# Superset version: 0.22.1
# See https://github.com/apache/incubator-superset/tree/master/superset
# for more customizing options

from .secrets import SECRET_KEY
from werkzeug.contrib.cache import RedisCache

#---------------------------------------------------------
# Superset specific config
#---------------------------------------------------------
ROW_LIMIT = 5000
SUPERSET_WORKERS = 4
SUPERSET_CELERY_WORKERS = 32

# Disabled, running gunicorn with unix socket instead
#SUPERSET_WEBSERVER_PORT = 8088
#---------------------------------------------------------

#---------------------------------------------------------
# Flask App Builder configuration
#---------------------------------------------------------
# Your App secret key
#SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
SQLALCHEMY_DATABASE_URI = 'sqlite:////path/to/superset.db'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''


# Celery config, as of version superset version 0.22, options
# SUPERSET_WORKERS and SUPERSET_CELERY_WORKERS seem to have no effect
# on the superset server, it does not seem to start workers accordingly
# Async sqlab queries need a superset worker spawned from the cli
# with:
# user@host:~$ path/to/venv/bin/superset worker -w n
# where n is the number of celery workers
class CeleryConfig(object):
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
CELERY_CONFIG = CeleryConfig

RESULTS_BACKEND = RedisCache(
    host='localhost',
    port=6379,
    key_prefix='superset_results'
)

# See https://pythonhosted.org/Flask-Cache/#configuring-flask-cache
# for additional CACHE_CONFIG options
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_REDIS_HOST': 'localhost', # change if using a different redis host
    'CACHE_REDIS_PORT': 6379, # change if using a different redis port
    #'CACHE_REDIS_PASSWORD': '', # redis password for server
    'CACHE_REDIS_URL': 'redis://localhost:6379/0', # redis connection uri
}
