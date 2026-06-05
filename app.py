import flet as ft

def main(page: ft.Page):
    page.title = "리메지코드"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    view_container = ft.Container()
    page.add(view_container)

    def go_to(view_name):
        view_container.content = build_view(view_name)
        page.update()

    def build_view(view_name):
        if view_name == "logo":
            return ft.GestureDetector(
                content=ft.Container(
                    content=ft.Column([ft.Text("리메지코드", size=40), ft.Text("클릭하여 시작")], alignment=ft.MainAxisAlignment.CENTER), 
                    alignment=ft.alignment.center
                ),
                on_tap=lambda _: go_to("login")
            )
        elif view_name == "login":
            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)
            return ft.Column([
                ft.Text("로그인", size=30), id_f, pw_f, 
                ft.ElevatedButton("로그인", on_click=lambda _: login_check(id_f.value, pw_f.value)), 
                ft.TextButton("회원가입", on_click=lambda _: go_to("signup_3")), 
                ft.Row([ft.TextButton("아이디 찾기"), ft.TextButton("비밀번호 찾기")], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER)
        elif view_name == "signup_3":
            return ft.Column([ft.Text("3. 이메일 작성"), ft.TextField(label="이메일"), ft.ElevatedButton("인증번호 발송", on_click=lambda _: go_to("signup_11"))], alignment=ft.MainAxisAlignment.CENTER)
        elif view_name == "signup_11":
            nick = ft.TextField(label="닉네임")
            bio = ft.TextField(label="상태메시지")
            return ft.Column([
                ft.Text("11. 프로필 제작"), nick, bio, 
                ft.Checkbox(label="나이 비공개"), ft.Checkbox(label="성별 비공개"), 
                ft.ElevatedButton("AI 검증 및 완료", on_click=lambda _: page.show_snack_bar(ft.SnackBar(content=ft.Text("AI 검증 완료! 가입 성공"))))
            ], alignment=ft.MainAxisAlignment.CENTER)
        return ft.Text("로딩중...")

    def login_check(uid, upw):
        if not uid or not upw: page.show_dialog(ft.AlertDialog(title=ft.Text("알림"), content=ft.Text("가입되지 않은 회원입니다.")))
        else: page.show_snack_bar(ft.SnackBar(content=ft.Text("로그인 성공!")))
        page.update()

    go_to("logo")

ft.app(target=main)