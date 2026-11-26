import redis

from clients import jh_redis_client


def count_click(code: str) -> None:
    try:
        jh_redis_client.rpush("jh-clicks", code)
    except redis.exceptions.ConnectionError:
        print(f"redis down, click counting is unavailable code:{code}")
        