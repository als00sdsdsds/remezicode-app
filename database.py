from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 127.0.0.1로 접속 주소를 바꾸고, '본인의비밀번호'를 실제 비밀번호로 수정하세요
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:LeeYeBin0901@127.0.0.1/remezicode"

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