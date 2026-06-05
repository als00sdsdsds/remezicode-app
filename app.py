import flet as ft
import requests

def main(page: ft.Page):
    page.title = "리메지코드 회원가입"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 단계별 데이터 저장
    user_data = {
        "email": "", "code": "", "id": "", "password": "", 
        "nickname": "", "bio": "", "age": "", "gender": "", "birth": ""
    }
    current_step = 1

    # 입력창 정의
    email_field = ft.TextField(label="이메일")
    code_field = ft.TextField(label="인증번호 6자리")
    id_field = ft.TextField(label="아이디")
    pw_field = ft.TextField(label="비밀번호", password=True)
    pw_check_field = ft.TextField(label="비밀번호 확인", password=True)
    
    # 상세 프로필 입력창
    nickname_field = ft.TextField(label="닉네임")
    bio_field = ft.TextField(label="상태메시지")
    age_field = ft.TextField(label="나이")
    age_private = ft.Checkbox(label="나이 비공개", value=False)
    gender_field = ft.Dropdown(label="성별", options=[ft.dropdown.Option("남성"), ft.dropdown.Option("여성")])
    gender_private = ft.Checkbox(label="성별 비공개", value=False)
    birth_field = ft.TextField(label="생년월일 (YYYYMMDD)")
    birth_private = ft.Checkbox(label="생일 비공개", value=False)

    # AI 검증 함수
    def verify_profile(e):
        profile_text = f"닉네임: {nickname_field.value}, 상태메시지: {bio_field.value}"
        # 백엔드 AI 분석 API 호출 (실제 환경에서는 서버 경로에 맞게 수정)
        try:
            # 예시용 호출 방식입니다.
            response = requests.post("http://127.0.0.1:8000/api/analyze", json={"text": profile_text})
            result = response.json()
            
            if result.get("violated"):
                page.add(ft.AlertDialog(title=ft.Text("검증 실패"), content=ft.Text(f"사유: {result.get('reason')}")))
                page.update()
            else:
                go_to_step(9)
        except Exception as ex:
            page.add(ft.SnackBar(content=ft.Text("AI 검증 서버 연결에 실패했습니다.")))
            page.update()

    def go_to_step(step):
        nonlocal current_step
        current_step = step
        page.controls.clear()
        page.add(build_step_ui())
        page.update()

    def build_step_ui():
        if current_step == 1:
            return ft.Column([ft.Text("1. 이메일 입력", size=20, weight="bold"), email_field, 
                              ft.ElevatedButton("인증번호 발송", on_click=lambda e: go_to_step(2))])
        elif current_step == 2:
            return ft.Column([ft.Text("2. 인증번호 입력", size=20, weight="bold"), code_field, 
                              ft.ElevatedButton("다음 단계", on_click=lambda e: go_to_step(3))])
        elif current_step == 3:
            return ft.Column([ft.Text("3. 인증 확인 완료", size=20, weight="bold"), 
                              ft.ElevatedButton("다음 단계", on_click=lambda e: go_to_step(4))])
        elif current_step == 4:
            return ft.Column([ft.Text("4. 아이디 설정", size=20, weight="bold"), id_field, 
                              ft.ElevatedButton("다음 단계", on_click=lambda e: go_to_step(5))])
        elif current_step == 5:
            return ft.Column([ft.Text("5. 비밀번호 설정", size=20, weight="bold"), pw_field, 
                              ft.ElevatedButton("다음 단계", on_click=lambda e: go_to_step(6))])
        elif current_step == 6:
            return ft.Column([ft.Text("6. 비밀번호 확인", size=20, weight="bold"), pw_check_field, 
                              ft.ElevatedButton("다음 단계", on_click=lambda e: go_to_step(7))])
        elif current_step == 7:
            return ft.Column([ft.Text("7. 회원가입 완료", size=20, weight="bold"), 
                              ft.ElevatedButton("로그인 하기", on_click=lambda e: go_to_step(8))])
        elif current_step == 8:
            return ft.Column([ft.Text("8. 프로필 정보 입력", size=20, weight="bold"), 
                              nickname_field, bio_field, 
                              ft.Row([age_field, age_private]), 
                              ft.Row([gender_field, gender_private]), 
                              ft.Row([birth_field, birth_private]),
                              ft.ElevatedButton("AI 검증 및 프로필 생성", on_click=verify_profile)])
        return ft.Text("가입 성공!")

    page.add(build_step_ui())

ft.app(target=main)