# -*- coding: utf-8 -*-

"""Provides a special case redis client factory for integration with the
  `turnstile`_ rate limiting middleware.
  
  _`turnstile`: https://github.com/klmitch/turnstile
"""

import logging
logger = logging.getLogger(__name__)

import os

from .config import DEFAULT_SETTINGS
from .hooks import RedisFactory

def turnstile_client_factory(env=None, factory=None, settings=None, **ini):
    """Special case ``turnstile.redis_client`` entrypoint -- allows the
      turnstile redis client to be configured by environment variables,
      overrideen by the INI configuration.
      
      (This helps keep the redis connection string out of source code).
    """
    
    # Compose.
    if env is None:
        env = os.environ
    if factory is None:
        factory = RedisFactory()
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    # Unpack the optional max_connections config, either from the turnstile.ini
    # file, or from the ``TURNSTILE_REDIS_MAX_CONNECTIONS`` environment variable.
    db = ini.get('db', os.environ.get('TURNSTILE_REDIS_DB', None))
    max_connections = ini.get('max_connections', os.environ.get(
            'TURNSTILE_REDIS_MAX_CONNECTIONS', None))
    
    # If necessary, patch the settings.
    if db is not None:
        settings['redis.db'] = db
    if max_connections is not None:
        settings['redis.max_connections'] = max_connections
    
    # Return the configured redis client.
    return factory(settings)

