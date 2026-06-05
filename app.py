import flet as ft
import requests

# 백엔드 API 주소 (실제 서버 주소로 변경하세요)
API_URL = "http://127.0.0.1:8000/api"

class RemejiApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_data = {}  # 회원가입 시 임시 데이터 저장
        self.current_step = 0
        self.setup_page()

    def setup_page(self):
        self.page.title = "리메지코드"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.render_logo()

    def render_logo(self):
        self.page.controls = [
            ft.GestureDetector(
                content=ft.Container(
                    content=ft.Column([ft.Text("리메지코드", size=40), ft.Text("화면을 클릭하여 시작하세요")], 
                    alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                ),
                on_tap=lambda _: self.render_login()
            )
        ]
        self.page.update()

    def render_login(self):
        id_field = ft.TextField(label="아이디")
        pw_field = ft.TextField(label="비밀번호", password=True)
        
        def login_process(e):
            # 예시: 저장된 유저 데이터가 있다고 가정 (실제로는 서버 API 호출)
            entered_id = id_field.value
            entered_pw = pw_field.value
            
            # DB 데이터 대조 로직 (예시)
            registered_users = {"admin": "1234"} # 실제 DB 연동 필요
            
            if entered_id not in registered_users:
                self.show_alert("로그인 실패", "가입되지 않은 회원입니다.")
            elif registered_users.get(entered_id) != entered_pw:
                self.show_alert("로그인 실패", "아이디와 비밀번호가 일치하지 않습니다.")
            else:
                self.page.add(ft.SnackBar(content=ft.Text("로그인 성공!")))
                self.page.update()

        self.page.controls = [
            ft.Column([
                ft.Text("로그인", size=30),
                id_field, pw_field,
                ft.ElevatedButton("로그인", on_click=login_process),
                ft.TextButton("회원가입", on_click=lambda _: self.render_signup_step(3)),
                ft.Row([ft.TextButton("아이디 찾기"), ft.TextButton("비밀번호 찾기")], alignment=ft.MainAxisAlignment.CENTER)
            ])
        ]
        self.page.update()

    def show_alert(self, title, message):
        self.page.dialog = ft.AlertDialog(title=ft.Text(title), content=ft.Text(message))
        self.page.dialog.open = True
        self.page.update()

    def render_signup_step(self, step):
        self.current_step = step
        self.page.controls.clear()
        
        # 단계별 UI 생성 (3~11단계)
        content = []
        if step == 3: # 이메일 입력
            email = ft.TextField(label="이메일")
            content = [ft.Text("3. 이메일 작성"), email, ft.ElevatedButton("인증번호 발송", on_click=lambda _: self.render_signup_step(4))]
        elif step == 4: # 인증번호 입력
            content = [ft.Text("5. 인증번호 입력"), ft.TextField(label="인증번호"), ft.ElevatedButton("다음", on_click=lambda _: self.render_signup_step(7))]
        elif step == 7: # 아이디
            content = [ft.Text("7. 아이디 작성"), ft.TextField(label="아이디"), ft.ElevatedButton("다음", on_click=lambda _: self.render_signup_step(8))]
        elif step == 8: # 비번
            content = [ft.Text("8. 비밀번호 작성"), ft.TextField(label="비밀번호", password=True), ft.ElevatedButton("다음", on_click=lambda _: self.render_signup_step(9))]
        elif step == 9: # 비번확인
            content = [ft.Text("9. 비밀번호 재작성"), ft.TextField(label="확인", password=True), ft.ElevatedButton("가입 완료", on_click=lambda _: self.render_signup_step(11))]
        elif step == 11: # 프로필 생성 (AI 검증 포함)
            nick = ft.TextField(label="닉네임")
            bio = ft.TextField(label="상태메시지")
            
            def ai_verify_profile(e):
                try:
                    payload = {"text": f"{nick.value} {bio.value}"}
                    self.page.add(ft.SnackBar(content=ft.Text("프로필 AI 검증 완료! 환영합니다.")))
                    self.page.update()
                except:
                    self.page.add(ft.SnackBar(content=ft.Text("AI 서버 연결 실패")))
                    self.page.update()

            content = [
                ft.Text("11. 프로필 제작"), nick, bio, 
                ft.Checkbox(label="나이 공개", value=True), ft.Checkbox(label="성별 공개", value=True),
                ft.ElevatedButton("AI 검증 및 생성", on_click=ai_verify_profile)
            ]
        
        self.page.add(ft.Column(content, alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

def main(page: ft.Page):
    RemejiApp(page)

ft.app(target=main)