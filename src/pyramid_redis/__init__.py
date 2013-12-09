# -*- coding: utf-8 -*-

"""Provide a Pyramid confguration entry point."""

import logging
logger = logging.getLogger(__name__)

import os

from .hooks import GetRedisClient

stub = os.environ.get('REDIS_KEY', 'REDIS')
REDIS_DB = '{0}_DB'.format(stub)
REDIS_URL = '{0}_URL'.format(stub)
REDIS_MAX_CONNECTIONS = '{0}_MAX_CONNECTIONS'.format(stub)
DEFAULT_SETTINGS = {
    'redis.db': os.environ.get(REDIS_DB, 0),
    'redis.url': os.environ.get(REDIS_URL, 'redis://localhost:6379'),
    'redis.max_connections': os.environ.get(REDIS_MAX_CONNECTIONS, None),
}

class IncludeMe(object):
    """Unpack the settings and provide ``request.redis``."""
    
    def __init__(self, **kwargs):
        self.default_settings = kwargs.get('default_settings', DEFAULT_SETTINGS)
        self.get_redis = kwargs.get('get_redis', GetRedisClient())
    
    def __call__(self, config):
        settings = config.get_settings()
        for key, value in self.default_settings.items():
            settings.setdefault(key, value)
        config.add_request_method(self.get_redis, 'redis', reify=True)
    

includeme = IncludeMe().__call__
