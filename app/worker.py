import os

import psycopg

from clients import jh_redis_client


DATABASE_URL = os.environ["DATABASE_URL"]


jh_redis_client.ping()
with psycopg.connect(DATABASE_URL) as conn:
    conn.execute("SELECT 1")
print("redis ok, db ok")


while True:
    item = jh_redis_client.blpop(
        keys="jh-clicks",
        timeout=5,
    )
    if item is None:
        continue
    _, code = item

    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            query="UPDATE Links SET clicks = clicks + 1 WHERE code = %s",
            params=(code,), 
        )
    print(f"click_counted: {code}")
