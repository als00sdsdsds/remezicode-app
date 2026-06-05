import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
import google.generativeai as genai
from config import GOOGLE_API_KEY, AI_SYSTEM_INSTRUCTION
from database import get_db
import models

router = APIRouter(prefix="/api", tags=["Community"])

# 제미나이 AI 초기화 세팅
genai.configure(api_key=GOOGLE_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

async def analyze_with_ai(text: str) -> dict:
    try:
        prompt = f"{AI_SYSTEM_INSTRUCTION}\n\n[검사할 텍스트]\n{text}"
        response = ai_model.generate_content(prompt)
        try:
            return json.loads(response.text.strip())
        except:
            if "바보" in text or "010-" in text:
                return {"violated": True, "reason": "유해 문구 또는 개인정보 의심 단어 감지"}
            return {"violated": False, "reason": ""}
    except Exception:
        return {"violated": False, "reason": "AI 오프라인 가상 통과"}


# =========================================================================
# 1️⃣ [고민/공감글 작성 및 조회 관련 API] (1번 기능 및 최신순/인기순 페이징)
# =========================================================================

# [고민/공감글 작성하기]
@router.post("/posts")
async def create_post(request: models.PostCreateRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    # 제미나이 AI 실시간 내용 검수
    ai_result = await analyze_with_ai(request.content)
    if ai_result.get("violated"):
        raise HTTPException(status_code=400, detail=f"AI 심사 탈락: {ai_result.get('reason')}")
    
    available_at = datetime.now()
    if request.category == "타임캡슐" and request.years_to_lock > 0:
        available_at = datetime.now() + timedelta(days=365 * request.years_to_lock)
        
    new_post = models.Post(
        user_id=request.user_id,
        category=request.category,
        content=request.content,
        available_at=available_at
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"status": "success", "message": "글이 안전하게 등록되었습니다.", "post_id": new_post.id}

# [고민/공감글 조회하기 (최신순/인기순 선택형 + 10개씩 페이징)]
@router.get("/posts")
async def get_posts(
    sort_by: str = Query("latest", description="정렬 방식: latest(최신순) 또는 popular(인기순)"),
    page: int = Query(1, ge=1, description="불러올 페이지 번호"),
    db: Session = Depends(get_db)
):
    limit = 10
    offset = (page - 1) * limit
    
    query = db.query(models.Post).filter(models.Post.is_blocked == False)
    
    if sort_by == "popular":
        query = query.order_by(models.Post.likes_count.desc(), models.Post.created_at.desc())
    else:
        query = query.order_by(models.Post.created_at.desc())
        
    total_count = query.count()
    posts = query.offset(offset).limit(limit).all()
    
    display_posts = []
    now = datetime.now()
    
    for post in posts:
        is_locked = post.available_at > now
        display_content = "🔒 이 타임캡슐은 아직 열어볼 수 없습니다." if is_locked else post.content
        
        author = db.query(models.User).filter(models.User.id == post.user_id).first()
        author_nickname = author.nickname if author else "알 수 없는 나그네"
        
        display_posts.append({
            "id": post.id,
            "author_nickname": author_nickname,
            "category": post.category,
            "content": display_content,
            "is_locked": is_locked,
            "likes_count": post.likes_count,
            "available_at": post.available_at.strftime("%Y-%m-%d"),
            "created_at": post.created_at.strftime("%Y-%m-%d")
        })
        
    return {
        "status": "success",
        "sort_by_applied": sort_by,
        "current_page": page,
        "total_posts": total_count,
        "has_more": (offset + limit) < total_count,
        "posts": display_posts
    }

# [고민글 공감(좋아요) 누르기 API]
@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.is_blocked == False).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
    post.likes_count += 1
    db.commit()
    db.refresh(post)
    return {"status": "success", "message": "고민 글에 따뜻한 공감을 보냈습니다.", "likes_count": post.likes_count}


# =========================================================================
# 2️⃣ [고민글에 대한 답신 편지 작성 및 조회 관련 API] (2번 기능)
# =========================================================================

# [고민글에 대한 답신 편지 보내기]
@router.post("/letters")
async def reply_letter(request: models.LetterCreateRequest, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == request.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="대상 고민 글을 찾을 수 없습니다.")
        
    # 답신 편지 내용 AI 실시간 검증
    ai_result = await analyze_with_ai(request.content)
    if ai_result.get("violated"):
        raise HTTPException(status_code=400, detail=f"AI 심사 탈락: {ai_result.get('reason')}")
        
    new_letter = models.Letter(
        post_id=request.post_id,
        sender_id=request.sender_id,
        receiver_id=post.user_id,  # 원글 작성자가 편지를 수신하게 됨
        content=request.content,
        decoration_id=request.decoration_id
    )
    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    return {"status": "success", "message": "위로의 편지가 배달되었습니다.", "letter_id": new_letter.id}


# =========================================================================
# 3️⃣ [⭐️ 편지 대행 요청 API] (3번 기능 - 4대 정밀 필수 양식 적용)
# =========================================================================

# [3-1. 편지 대행 요청하기 (누구에게/어째서/주제/내용 필수 검증)]
@router.post("/proxy-requests")
async def create_letter_proxy_request(request: models.ProxyRequestCreate, db: Session = Depends(get_db)):
    # 존재하는 사용자인지 체크
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    # 🛡️ 4대 정밀 항목들을 모두 합쳐서 AI 검수 진행
    full_verification_text = (
        f"수신대상: {request.target_recipient}\n"
        f"신청이유: {request.reason}\n"
        f"편지주제: {request.subject}\n"
        f"필수내용: {request.content_requirement}"
    )
    
    ai_result = await analyze_with_ai(full_verification_text)
    if ai_result.get("violated"):
        raise HTTPException(
            status_code=400, 
            detail=f"편지 대행 양식 AI 심사 탈락: {ai_result.get('reason')}"
        )
    
    # 안전함이 증명되면 MySQL 금고의 4대 양식 칸에 정확하게 조각내어 저장
    new_proxy_request = models.LetterProxyRequest(
        user_id=request.user_id,
        target_recipient=request.target_recipient,
        reason=request.reason,
        subject=request.subject,
        content_requirement=request.content_requirement
    )
    db.add(new_proxy_request)
    db.commit()
    db.refresh(new_proxy_request)
    
    return {
        "status": "success", 
        "message": "편지 대행 요청이 규격 양식대로 안전하게 등록되었습니다.", 
        "proxy_request_id": new_proxy_request.id
    }

# [3-2. 전체 편지 대행 요청 리스트 조회하기]
@router.get("/proxy-requests")
async def get_proxy_requests(
    page: int = Query(1, ge=1, description="페이지 번호"),
    db: Session = Depends(get_db)
):
    limit = 10
    offset = (page - 1) * limit
    
    query = db.query(models.LetterProxyRequest).filter(
        models.LetterProxyRequest.is_blocked == False,
        models.LetterProxyRequest.is_completed == False  # 아직 답신을 받지 못한 요청만 선별
    ).order_by(models.LetterProxyRequest.created_at.desc())
    
    total_count = query.count()
    requests = query.offset(offset).limit(limit).all()
    
    display_requests = []
    for req in requests:
        author = db.query(models.User).filter(models.User.id == req.user_id).first()
        author_nickname = author.nickname if author else "익명의 나그네"
        
        display_requests.append({
            "proxy_request_id": req.id,
            "requester_nickname": author_nickname,
            "target_recipient": req.target_recipient,      # 누구에게
            "reason": req.reason,                          # 어째서
            "subject": req.subject,                        # 무슨 주제로
            "content_requirement": req.content_requirement, # 무슨 내용이 들어가야 하는지
            "created_at": req.created_at.strftime("%Y-%m-%d")
        })
        
    return {
        "status": "success",
        "current_page": page,
        "total_requests": total_count,
        "has_more": (offset + limit) < total_count,
        "proxy_requests": display_requests
    }


# =========================================================================
# 4️⃣ [⭐️ 편지 대행에 대한 답신 작성 및 조회 API] (4번 기능)
# =========================================================================

# [4-1. 편지 대행 요청글을 보고 대신 완성도 높은 편지 써서 제출하기(답신)]
@router.post("/proxy-replies")
async def reply_to_proxy_request(request: models.ProxyReplyCreate, db: Session = Depends(get_db)):
    # 대상 대행 요청이 존재하는지 확인
    proxy_req = db.query(models.LetterProxyRequest).filter(
        models.LetterProxyRequest.id == request.proxy_request_id,
        models.LetterProxyRequest.is_blocked == False
    ).first()
    
    if not proxy_req:
        raise HTTPException(status_code=404, detail="대상이 되는 편지 대행 요청글을 찾을 수 없습니다.")
        
    # 완성된 대행 편지 내용 AI 실시간 심사
    ai_result = await analyze_with_ai(request.completed_letter_content)
    if ai_result.get("violated"):
        raise HTTPException(status_code=400, detail=f"AI 대행 편지 심사 탈락: {ai_result.get('reason')}")
        
    # 편지 대행 답글 금고에 저장
    new_reply = models.LetterProxyReply(
        proxy_request_id=request.proxy_request_id,
        writer_id=request.writer_id,
        completed_letter_content=request.completed_letter_content,
        decoration_id=request.decoration_id
    )
    db.add(new_reply)
    
    # 대행 요청 완료 상태로 변경
    proxy_req.is_completed = True
    
    db.commit()
    db.refresh(new_reply)
    
    return {
        "status": "success", 
        "message": "의뢰하신 편지가 온 마음을 담아 정성껏 대행 작성되었습니다.", 
        "proxy_reply_id": new_reply.id
    }

# [4-2. 특정 편지 대행 요청글에 작성된 '답신 편지들' 조회하기]
@router.get("/proxy-requests/{proxy_request_id}/replies")
async def get_replies_for_proxy_request(
    proxy_request_id: int,
    db: Session = Depends(get_db)
):
    replies = db.query(models.LetterProxyReply).filter(
        models.LetterProxyReply.proxy_request_id == proxy_request_id,
        models.LetterProxyReply.is_blocked == False
    ).order_by(models.LetterProxyReply.likes_count.desc(), models.LetterProxyReply.created_at.desc()).all()
    
    display_replies = []
    for reply in replies:
        writer = db.query(models.User).filter(models.User.id == reply.writer_id).first()
        writer_nickname = writer.nickname if writer else "대행 펜벗 나그네"
        
        display_replies.append({
            "reply_id": reply.id,
            "writer_nickname": writer_nickname,
            "completed_letter_content": reply.completed_letter_content,
            "decoration_id": reply.decoration_id,
            "likes_count": reply.likes_count,
            "created_at": reply.created_at.strftime("%Y-%m-%d %H:%M")
        })
        
    return {"status": "success", "replies": display_replies}


# =========================================================================
# 5️⃣ [기타 유틸리티 API] (마이페이지 편지함 및 신고 기능)
# =========================================================================

# [내 우체통 조회 기능]
@router.get("/mailbox/{user_id}")
async def get_my_mailbox(user_id: int, db: Session = Depends(get_db)):
    letters = db.query(models.Letter).filter(models.Letter.receiver_id == user_id, models.Letter.is_blocked == False).all()
    my_letters = []
    for letter in letters:
        sender = db.query(models.User).filter(models.User.id == letter.sender_id).first()
        nickname = sender.nickname if sender else "익명의 나그네"
        
        my_letters.append({
            "letter_id": letter.id,
            "sender_nickname": nickname,
            "content": letter.content,
            "decoration_id": letter.decoration_id,
            "is_read": letter.is_read,
            "created_at": letter.created_at.strftime("%Y-%m-%d %H:%M")
        })
        letter.is_read = True
    db.commit() 
    return {"status": "success", "mailbox": my_letters}

# [고민 글/편지 신고 기능]
@router.post("/report")
async def report_content(request: models.ReportRequest, db: Session = Depends(get_db)):
    target_text = ""
    target_obj = None
    
    if request.target_type == "post":
        target_obj = db.query(models.Post).filter(models.Post.id == request.target_id).first()
        if not target_obj: raise HTTPException(status_code=404, detail="게시글이 없습니다.")
        target_text = target_obj.content
    elif request.target_type == "letter":
        target_obj = db.query(models.Letter).filter(models.Letter.id == request.target_id).first()
        if not target_obj: raise HTTPException(status_code=404, detail="편지가 없습니다.")
        target_text = target_obj.content
        
    ai_prompt = f"사용자 신고 사유: {request.reason}\n위 내용을 바탕으로 재심사해줘."
    ai_result = await analyze_with_ai(target_text + "\n" + ai_prompt)
    
    if ai_result.get("violated"):
        target_obj.is_blocked = True
        db.commit()
        return {"status": "content_removed", "message": "신고가 유효하여 콘텐츠가 차단되었습니다.", "reason": ai_result.get("reason")}
    else:
        return {"status": "report_dismissed", "message": "정상적인 글로 판정되었습니다."}