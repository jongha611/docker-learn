from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

import os
import secrets
import string

# postgresql
import psycopg
# redis
import redis

from clients import jh_cache
from feature import count_click


DATABASE_URL = os.environ["DATABASE_URL"]
ALPHABET = string.ascii_letters + string.digits


app = FastAPI()


class ShortenRequest(BaseModel):

    url:HttpUrl


def new_code(length: int=6) -> str:
    completed_code = "".join(secrets.choice(ALPHABET) for _ in range(length))
    return completed_code


@app.get("/health")
def health_check():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("SELECT 1")
    jh_cache.ping()
    return {
        "feeling": "good",
        "redis": jh_cache.info("server")["redis_version"],
    }


@app.post("/api/shorten")
def shorten(req: ShortenRequest):
    code = new_code()
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            "INSERT INTO links (code, url) VALUES (%s, %s)",
            (code, str(req.url)),
        )
    return {"code": code, "short_url": f"/{code}"}


@app.get("/api/stats/{code}")
def stats(code):
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "SELECT url, clicks, created_at FROM links WHERE code = %s",
            (code,),
        ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="not found",
        )
    return {
        "code": code,
        "url": row[0],
        "clicks": row [1],
        "created at": row[2],
    }


@app.get("/{code}")
def follow(code: str):
    try:
        url = jh_cache.get(f"jh-link: {code}")
    # except: fall back 경로가 있는데 새로운 에러를 발생시키지 말것 (raise)
    except redis.exceptions.ConnectionError:
        print("redis down, fall back to db")
        url = None
    if url is not None:
        print(f"cache hit: {code}")
        count_click(code)
        return RedirectResponse(
            url,
            status_code=302,
        )
    print(f"cache miss: {code}")
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            row = conn.execute(
                "SELECT url FROM links WHERE code = %s",
                (code,),
            ).fetchone()
    except psycopg.OperationalError:
        print("db down, can not verify the code")
        raise HTTPException(
            status_code=503,
            detail="service is unavailable",
        )
    # 방어코드를 작성하지 않을 경우 생길 수 있는 문제 1:
    # 사용자의 잘못된 요청 -> 그러나 내 코드 터진걸로 안내 및 기록 (internal server error)
    if row is None:
        # raise는 실행되는 순간 함수를 끝냄
        # 그래서 if 아래로 내려왔다는 것 자체가 이미 "row가 있다"는 뜻
        # return을 고려하거나 else를 쓸 필요 없음
        raise HTTPException(
            status_code=404,
            detail="not found",
        )
    try:
        jh_cache.set(f"jh-link: {code}", row[0], ex=3600)
    except redis.exceptions.ConnectionError:
        print("redis down, saving cache is unavailable")
    count_click(code)
    return RedirectResponse(
        url=row[0],
        status_code=302,
    )
