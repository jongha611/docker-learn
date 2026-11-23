from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

import os
import secrets
import string

import psycopg


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
        return {"feeling": "good"}


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
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
             "SELECT url FROM links WHERE code = %s",
             (code,),
        ).fetchone()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="not found",
            )
        return RedirectResponse(
            url=row[0],
            status_code=302,
        )