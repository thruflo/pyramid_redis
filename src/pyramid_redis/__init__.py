# -*- coding: utf-8 -*-

"""Provide a Pyramid confguration entry point."""

import logging
logger = logging.getLogger(__name__)

from .config import DEFAULT_SETTINGS
from .hooks import GetRedisClient

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
