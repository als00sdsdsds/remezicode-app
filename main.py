from fastapi import FastAPI
from database import engine, Base
from routers import auth, community

# 🚀 서버 시작 시 MySQL에 테이블이 없다면 자동으로 만들어주는 코드
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Remezicode API Server",
    description="MySQL과 연동되어 영구 저장이 가능한 리메지코드 최종 백엔드",
    version="2.0.0"
)

# 나눠진 폴더의 기능들을 한곳으로 조립
app.include_router(auth.router)
app.include_router(community.router)

@app.get("/")
def read_root():
    return {"message": "MySQL 연동 완료! 최고 퀄리티의 리메지코드 서버가 가동 중입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)