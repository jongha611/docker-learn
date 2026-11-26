import os

import redis

# ============== 2026-11-26, S6-a 스텝 진행 중 교훈 ============= #

# 이 파일은 이 파일을 임포트 하는 스크립트 파일 안에서 전문이 실행된다 (from a import b 라고 a가 실행된다)
# DATABASE_URL = os.environ["DATABASE_URL"] 은 처음에 적혀있었지만 이 파일을 임포트 하는 worker.py 에서 에러를 내서 삭제하였다 KeyError
# compose.yaml 에 의하면 worker 컨테이너 안에는 DATABASE_URL 환경변수가 들어있지 않았기 때문이다
# worker 의 프로세스가 이 파일의 사본을 해당 컨테이너에서 실행시키는 구조
# 따라서 임포트되는 파일은 이 파일을 임포트하는 컨테이너들이 가진 환경변수만 사용해야 한다. 또는 임포트하는 컨테이너에 환경변수를 compose.yaml을 통해 주입시켜도 된다
REDIS_URL = os.environ["REDIS_URL"]


jh_redis_client = redis.Redis.from_url(
    url=REDIS_URL,
    decode_responses=True,
    # 클라이언트-레디스 연결 중 클라이언트의 소켓 마감 시간 
    # worker의 <client>.blpop의 인자인 timeout=5 보다 길어야 함 (같으면 순서에 의해 0.00001초라도 차이가 나는 물리시간적 구조가 생겨 nil 응답을 못 받고 TimeoutError)
    socket_timeout=10,
)
