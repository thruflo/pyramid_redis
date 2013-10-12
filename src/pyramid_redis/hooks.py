# -*- coding: utf-8 -*-

"""Provides a ``RedisFactory`` to get a configured redis client from a
  settings dictionary, e.g.::
  
      >>> factory = RedisFactory()
      >>> client = factory({'redis.url': 'redis://localhost:6379'})
  
  And ``GetRedisClient`` which wraps the factory so it can be used as a
  Pyramid request method.
"""

__all__ = [
    'GetRedisClient',
    'RedisFactory',
]

import logging
logger = logging.getLogger(__name__)

import redis

try:
    import urlparse
except ImportError: #py3
    import urllib.parse as urlparse

from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import directlyProvides

class IRedisConnectionPool(Interface):
    """Marker interface provided by RedisConnectionPool utilities."""


class ParseConfig(object):
    """Parse the application settings into connection pool kwargs."""
    
    def __init__(self, **kwargs):
        self.parse_url = kwargs.get('parse_url', urlparse.urlparse)
    
    def __call__(self, settings):
        """Unpack the settings. Parse the url into components and build
          a dict to return.
        """
        
        # Unpack.
        url = settings['redis.url']
        db = settings.get('redis.db', 0)
        max_connections = settings.get('redis.max_connections', None)
        
        # Parse into a config dict.
        o = self.parse_url(url)
        config = {
            'host': o.hostname,
            'port': o.port,
            'db': db
        }
        if o.password:
            config['password'] = o.password
        if max_connections is not None:
            config['max_connections'] = max_connections
        return config
    

class RedisFactory(object):
    def __init__(self, **kwargs):
        self.get_registry = kwargs.get('get_registry', getGlobalSiteManager)
        self.parse_config = kwargs.get('parse_config', ParseConfig())
        self.pool_cls = kwargs.get('pool_cls', redis.BlockingConnectionPool)
        self.provides = kwargs.get('provides', directlyProvides)
        self.redis_cls = kwargs.get('redis_cls', redis.StrictRedis)
    
    def __call__(self, settings, registry=None):
        """Returns a ``redis`` client that uses a connection pool registered in
          the ``registry`` provided that is, in turn, configured with the
          ``settings`` provided.
        """
        
        # If called without a registry, i.e.: not within the context of a
        # Pyramid application, then register the connection pool in a
        # zope.component registry.
        if registry is None:
            registry = self.get_registry()
        
        # Query the registry for a connection pool. If it doesn't exist,
        # instantiate and register one for next time.
        connection_pool = registry.queryUtility(IRedisConnectionPool)
        if not connection_pool:
            kwargs = self.parse_config(settings)
            connection_pool = self.pool_cls(**kwargs)
            self.provides(connection_pool, IRedisConnectionPool)
            registry.registerUtility(connection_pool, IRedisConnectionPool)
        
        # And use it to instantiate a redis client.
        return self.redis_cls(connection_pool=connection_pool)
    


class GetRedisClient(object):
    """Provide the redis factory as a Pyramid request method."""
    
    def __init__(self, **kwargs):
        self.redis_factory = kwargs.get('redis_factory', RedisFactory())
    
    def __call__(self, request):
        registry = request.registry
        return self.redis_factory(registry.settings, registry=registry)
    

