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


DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]
ALPHABET = string.ascii_letters + string.digits


app = FastAPI()
jh_cache = redis.Redis.from_url(
    url=REDIS_URL,
    decode_responses=True,
)


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
    url = jh_cache.get(f"jh-link: {code}")
    if url is not None:
        print(f"cache hit: {code}")
        return RedirectResponse(
            url,
            status_code=302,
        )
    print(f"cache miss: {code}")
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
             "SELECT url FROM links WHERE code = %s",
             (code,),
        ).fetchone()
    jh_cache.set(f"jh-link: {code}", row[0], ex=3600)
    return RedirectResponse(
        url=row[0],
        status_code=302,
    )
