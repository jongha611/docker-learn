import os

import redis


DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]


jh_cache = redis.Redis.from_url(url=REDIS_URL)
