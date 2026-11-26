import os
import time

import redis
import psycopg

from clients import jh_redis_client


while True:
    item = jh_redis_client.blpop(
        keys="jh-clicks",
        timeout=5,
    )
    if item is None:
        continue
    print(f"popped: {item}")