from fastapi import FastAPI
from routers import auth, community  # auth 라우터 추가 유입

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "MySQL 연동 완료! 리메지코드 서버가 가동 중입니다."}

# 프론트엔드에서 /api/auth/signup, /api/posts 등으로 일관되게 요청할 수 있도록 접두사(prefix) 설정
app.include_router(auth.router, prefix="/api")
app.include_router(community.router, prefix="/api")