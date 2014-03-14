# -*- coding: utf-8 -*-

"""Provide environment variable configured ``DEFAULT_SETTINGS``."""

import os

stub = os.environ.get('REDIS_KEY', 'REDIS')

REDIS_DB = '{0}_DB'.format(stub)
REDIS_URL = '{0}_URL'.format(stub)
REDIS_MAX_CONNECTIONS = '{0}_MAX_CONNECTIONS'.format(stub)

DEFAULT_SETTINGS = {
    'redis.db': os.environ.get(REDIS_DB, 0),
    'redis.url': os.environ.get(REDIS_URL, 'redis://localhost:6379'),
    'redis.max_connections': os.environ.get(REDIS_MAX_CONNECTIONS, None),
}
