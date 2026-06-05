from fastapi import FastAPI
from routers import community

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "MySQL 연동 완료! 리메지코드 서버가 가동 중입니다."}

app.include_router(community.router, prefix="/api")