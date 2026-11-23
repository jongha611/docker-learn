# python
FROM python:3.12-slim


# uv 공식 스타트 가이드: 
# https://docs.astral.sh/uv/guides/integration/docker/#getting-started
# COPY의 마지막 인자는 컨테이너를 가리킨다
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /bin/


# environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON_DOWNLOADS=0


# 절대경로 주의
# 두 가지 작업 수행 -> mkdir -p /app && cd /app
WORKDIR /app


# 의존성 카피
COPY pyproject.toml uv.lock .python-version ./

# uv 실행 -> python -m venv /app/.venv 및 의존성 설치
RUN uv sync --locked --no-cache

# 절대경로 주의
# 환경변수 추가 전 $PATH의 대략적인 형태: /usr/local/bin:/usr/bin:/bin 등
# 여기에 /app/.venv/bin을 추가하여 uvicorn 실행 시 가상환경의 패키지를 우선적으로 참조하도록 함
# 가상환경 활성화 -> source /app/.venv/bin/activate
ENV PATH="/app/.venv/bin:$PATH"


# COPY의 마지막 인자는 컨테이너를 가리킨다
# 로컬 소스 -> 컨테이너
COPY . .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# 이미지 빌드 ex)
    # docker build -t docker-learn-app ./app

# 컨테이너 실행 ex)
    # docker run (--rm) (-d) -p 8000:8000 docker-learn-app

# 컨테이너 종료 ex)
    # docker stop <container_id> (일부분 입력 가능)

