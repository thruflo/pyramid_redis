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
import pyramid.exceptions
import redis

try:
    import urlparse
except ImportError:  # py3
    import urllib.parse as urlparse

from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import directlyProvides


class IRedisClientConfiguration(Interface):

    """Marker interface provided by RedisClientConfiguration"""


class RedisClientConfiguration(dict):

    """Parse the application settings into connection pool kwargs."""

    def __init__(self, **kwargs):
        self.parse_url = kwargs.get('parse_url', urlparse.urlparse)
        self.pool_cls = kwargs.get('pool_cls', redis.BlockingConnectionPool)

    def __call__(self, settings):
        """Unpack the settings. Parse the url into components and build
          a dict to return. As an alternative, you may also provide a
          unix_socket_path.
        """
        self.clear()  # make sure you can reconfigure the client
        db = settings.get('redis.db', 0)
        config = {'db': int(db)}
        if ('redis.unix_socket_path' in settings and
                settings['redis.unix_socket_path'] is not None):
            config['unix_socket_path'] = settings['redis.unix_socket_path']
        elif ('redis.url' in settings and
                settings['redis.url'] is not None):  # should default to
                                                     # `redis://localhost:6379`
            # Unpack.
            url = settings['redis.url']

            # Parse into a config dict.
            o = self.parse_url(url)
            config.update({
                'host': o.hostname,
                'port': o.port,
            })
            if o.password:
                config['password'] = o.password

            max_connections = settings.get('redis.max_connections', None)
            if max_connections is not None:
                config['max_connections'] = int(max_connections)
            config = {'connection_pool': self.pool_cls(**config)}
        else:
            raise pyramid.exceptions.ConfigurationError(
                """To use redis with pyramid, redis.url or
                redis.unix_socket_path should be provided"""
            )
        self.update(config)
        return self


class RedisFactory(object):

    def __init__(self, **kwargs):
        self.get_registry = kwargs.get('get_registry', getGlobalSiteManager)
        self.config = kwargs.get('parse_config', RedisClientConfiguration())
        self.provides = kwargs.get('provides', directlyProvides)
        self.redis_cls = kwargs.get('redis_cls', redis.StrictRedis)

    def __call__(self, settings, registry=None):
        """Returns a ``redis`` client that uses a client configuration
           registered in the ``registry`` provided that is, in turn,
           configured with the ``settings`` provided.
        """

        # If called without a registry, i.e.: not within the context of a
        # Pyramid application, then register the connection pool in a
        # zope.component registry.
        if registry is None:
            registry = self.get_registry()

        # Query the registry for a client_configuration. If it doesn't exist,
        # instantiate and register one for next time.
        redis_client_conf = registry.queryUtility(IRedisClientConfiguration)
        if not redis_client_conf:
            redis_client_conf = self.config(settings)  # update RedisClientConf
            self.provides(self.config, IRedisClientConfiguration)
            registry.registerUtility(self.config,
                                     IRedisClientConfiguration)

        # And use it to instantiate a redis client.
        return self.redis_cls(**redis_client_conf)


class GetRedisClient(object):

    """Provide the redis factory as a Pyramid request method."""

    def __init__(self, **kwargs):
        self.redis_factory = kwargs.get('redis_factory', RedisFactory())

    def __call__(self, request):
        registry = request.registry
        return self.redis_factory(registry.settings, registry=registry)
