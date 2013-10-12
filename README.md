[pyramid_redis][] is one specific way of integrating [redis-py][] with a
[Pyramid][] web application.

### Features

* provides a redis client at `request.redis`
* configurable per-process blocking connection pool

### Usage

To use, `pip install pyramid_redis` / add `pyramid_redis` to your requirements.txt
and then [include][] the package:

    config.include('pyramid_redis')

### Configuration

Requires the following [INI setting / environment variable][]:

* `redis.url` / `REDIS_URL`

Plus optionally looks for:

* `redis.db` / `REDIS_DB`
* `redis.max_connections` / `REDIS_MAX_CONNECTIONS`

[pyramid_redis]: https://github.com/thruflo/pyramid_redis
[redis-py]: https://github.com/andymccurdy/redis-py
[Pyramid]: http://pypi.python.org/pypi/pyramid
[include]: http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.include
[INI setting / environment variable]: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/environment.html#adding-a-custom-setting
