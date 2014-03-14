
# 0.1.3

Add `turnstile` module providing a special case `turnstile_client_factory`, which
can be used as a drop in `turnstile.redis_client` entrypoint with the [turnstile]()
rate limiting middleware.

[turnstile]: https://github.com/klmitch/turnstile

# 0.1.2

Explicitly write the `redis.` namespace in the default settings dict keys.

# 0.1.1

Support a `REDIS_KEY` environment variable to make picking up vars from
providers like REDISTOGO and REDISCLOUD easier.

Make sure that DB and MAX_CONNECTIONS are ints.

# 0.1

Initial release.