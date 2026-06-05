import flet as ft

def main(page: ft.Page):
page.title = "리메지코드"
page.theme_mode = ft.ThemeMode.LIGHT
page.vertical_alignment = ft.MainAxisAlignment.CENTER
page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

container = ft.Container(expand=True)
page.add(container)

def change_view(view_name):
    container.content = build_view(view_name)
    page.update()

def build_view(view_name):
    # 1. 로고 화면
    if view_name == "logo":
        return ft.GestureDetector(
            content=ft.Column([ft.Text("리메지코드", size=40, weight="bold"), ft.Text("클릭하여 시작")], alignment="center", horizontal_alignment="center"),
            on_tap=lambda e: change_view("login")
        )
    
    # 2. 로그인 및 찾기 화면
    elif view_name == "login":
        id_f = ft.TextField(label="아이디")
        pw_f = ft.TextField(label="비밀번호", password=True)
        return ft.Column([
            ft.Text("로그인", size=30), id_f, pw_f,
            ft.ElevatedButton("로그인", on_click=lambda e: login_action(id_f.value, pw_f.value)),
            ft.TextButton("회원가입", on_click=lambda e: change_view("signup_3")),
            ft.Row([ft.TextButton("아이디 찾기"), ft.TextButton("비밀번호 찾기")], alignment="center")
        ], alignment="center", horizontal_alignment="center")

    # 3. 회원가입 과정
    elif view_name == "signup_3":
        return ft.Column([ft.Text("3. 이메일 작성"), ft.TextField(label="이메일"), ft.ElevatedButton("인증번호 발송", on_click=lambda e: change_view("signup_11"))], alignment="center")

    # 11. 프로필 생성 및 AI 검증
    elif view_name == "signup_11":
        nick = ft.TextField(label="닉네임")
        bio = ft.TextField(label="상태메시지")
        def ai_verify(e):
            page.show_snack_bar(ft.SnackBar(content=ft.Text("AI 검증 완료! 가입 성공")))
        return ft.Column([
            ft.Text("11. 프로필 제작"), nick, bio,
            ft.Checkbox(label="나이 비공개"), ft.Checkbox(label="성별 비공개"), ft.Checkbox(label="생일 비공개"),
            ft.ElevatedButton("AI 검증 및 완료", on_click=ai_verify)
        ], alignment="center", horizontal_alignment="center")
        
    return ft.Text("진행 중...")

def login_action(uid, upw):
    if uid == "user" and upw == "1234":
        page.show_snack_bar(ft.SnackBar(content=ft.Text("로그인 성공!")))
    else:
        page.show_dialog(ft.AlertDialog(title=ft.Text("오류"), content=ft.Text("아이디 또는 비밀번호가 틀렸습니다.")))
    page.update()

change_view("logo")
ft.app(target=main)