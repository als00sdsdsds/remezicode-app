from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import Base

# =========================================================================
# 1. MySQL 실제 테이블 구조 정의 (Database Schema)
# =========================================================================

# [회원 정보 테이블]
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    nickname = Column(String(50), default="따뜻한 나그네")
    created_at = Column(DateTime, default=func.now())

# [1번 기능: 일반 고민/공감글 테이블]
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)  # 예: "고민", "일상", "타임캡슐"
    content = Column(Text, nullable=False)
    available_at = Column(DateTime, default=func.now())  # 타임캡슐 오픈 예정일
    is_blocked = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0, nullable=False)  # 공감(좋아요) 수
    created_at = Column(DateTime, default=func.now())

# [2번 기능: 일반 고민글에 대한 답신 편지 테이블]
class Letter(Base):
    __tablename__ = "letters"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    decoration_id = Column(Integer, default=1)  # 편지지 번호
    is_read = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

# [3번 기능: ⭐️ 편지 대행 요청 테이블 (양식 필수 저장!)]
class LetterProxyRequest(Base):
    __tablename__ = "letter_proxy_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 요청자 ID
    
    # 📝 기획하신 4대 필수 양식 컬럼들
    target_recipient = Column(String(100), nullable=False)  # 누구에게 (예: "첫사랑", "어머니")
    reason = Column(Text, nullable=False)                    # 어째서 (예: "고마움을 표현하고 싶어서")
    subject = Column(String(200), nullable=False)           # 무슨 주제로 (예: "어버이날 감사 편지")
    content_requirement = Column(Text, nullable=False)       # 무슨 내용이 들어가는지 (예: "키워주셔서 감사하다는 말")
    
    is_completed = Column(Boolean, default=False)  # 답신을 받아 대행이 완료되었는지 여부
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

# [4번 기능: ⭐️ 편지 대행 요청에 대한 답신(대행 편지) 테이블]
class LetterProxyReply(Base):
    __tablename__ = "letter_proxy_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    proxy_request_id = Column(Integer, ForeignKey("letter_proxy_requests.id"), nullable=False)  # 대상 대행 요청 ID
    writer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 대행 편지 작성해 준 따뜻한 유저 ID
    
    completed_letter_content = Column(Text, nullable=False)  # 작성 완료된 진짜 편지 내용
    decoration_id = Column(Integer, default=1)  # 편지지 번호
    likes_count = Column(Integer, default=0, nullable=False)  # 이 대행 편지가 얼마나 맘에 드는지 공감 수
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


# =========================================================================
# 2. FastAPI 데이터 요청/응답 검증 양식 (Pydantic Schemas)
# =========================================================================
class EmailAuthRequest(BaseModel):
    email: EmailStr

class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: str

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    phone_number: str
    nickname: Optional[str] = "따뜻한 나그네"

# [1번 기능: 일반 고민글 생성 요청 양식]
class PostCreateRequest(BaseModel):
    user_id: int
    category: str 
    content: str
    years_to_lock: Optional[int] = 0 

# [2번 기능: 일반 답신 편지 생성 요청 양식]
class LetterCreateRequest(BaseModel):
    post_id: int
    sender_id: int
    content: str
    decoration_id: int = 1 

# [3번 기능: ⭐️ 편지 대행 요청 생성 양식]
class ProxyRequestCreate(BaseModel):
    user_id: int
    target_recipient: str  # 누구에게
    reason: str            # 어째서
    subject: str           # 무슨 주제로
    content_requirement: str  # 무슨 내용이 들어가야 하는지

# [4번 기능: ⭐️ 편지 대행에 대한 답신 생성 양식]
class ProxyReplyCreate(BaseModel):
    proxy_request_id: int
    writer_id: int
    completed_letter_content: str  # 완성된 대행 편지 내용
    decoration_id: Optional[int] = 1

class ReportRequest(BaseModel):
    reporter_id: int
    target_type: str 
    target_id: int
    reason: str