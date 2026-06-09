import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일에 저장된 환경변수들을 로드합니다.
load_dotenv()

# 환경변수에서 URL을 가져오고, 없으면 기존 기본 주소를 사용합니다.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:LeeYeBin0901@127.0.0.1/remezicode"
)

# 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스
Base = declarative_base()

# DB 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()