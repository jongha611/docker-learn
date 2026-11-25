import redis

from clients import jh_cache


def count_click(code: str) -> None:
    try:
        jh_cache.rpush("jh-clicks", code)
    except redis.exceptions.ConnectionError:
        print(f"redis down, click counting is unavailable code:{code}")
        