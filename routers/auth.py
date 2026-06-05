from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup")
async def signup(request: models.SignUpRequest, db: Session = Depends(get_db)):
    # 사용자 생성 로직
    user = models.User(
        email=request.email,
        password=request.password, 
        phone_number=request.phone_number,
        nickname=request.nickname
    )
    db.add(user)
    db.commit()
    return {"status": "success", "message": "회원가입이 완료되었습니다."}