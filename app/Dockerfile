# 파이썬 정의
FROM python:3.12-slim


# uv 정의
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /bin/


# 환경 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-cache

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]