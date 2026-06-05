import flet as ft

# 유저 정보를 저장하는 임시 데이터베이스
user_db = {}

def main(page: ft.Page):
    page.title = "리메지코드"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    container = ft.Container(expand=True)
    page.add(container)

    def change_view(view_name):
        container.content = build_view(view_name)
        page.update()

    def build_view(view_name):
        if view_name == "logo":
            return ft.GestureDetector(
                content=ft.Column(
                    [ft.Text("리메지코드", size=40, weight="bold"), ft.Text("클릭하여 시작")],
                    alignment="center", horizontal_alignment="center"
                ),
                on_tap=lambda e: change_view("main_dashboard") if page.session.get("logged_in") else change_view("login")
            )
        
        elif view_name == "login":
            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)
            def login_check(e):
                if id_f.value in user_db and user_db[id_f.value]["pw"] == pw_f.value:
                    page.session.set("logged_in", True)
                    change_view("main_dashboard")
                else:
                    page.show_dialog(ft.AlertDialog(title=ft.Text("알림"), content=ft.Text("아이디 또는 비밀번호가 틀렸습니다.")))
            return ft.Column(
                [
                    ft.Text("로그인", size=30), id_f, pw_f,
                    ft.ElevatedButton("로그인", on_click=login_check),
                    ft.TextButton("회원가입", on_click=lambda e: change_view("signup"))
                ], alignment="center"
            )

        elif view_name == "signup":
            email_f = ft.TextField(label="이메일")
            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)
            def register(e):
                user_db[id_f.value] = {"pw": pw_f.value, "email": email_f.value}
                change_view("welcome")
            return ft.Column([ft.Text("회원가입"), email_f, id_f, pw_f, ft.ElevatedButton("가입하기", on_click=register)], alignment="center")

        elif view_name == "welcome":
            return ft.GestureDetector(
                content=ft.Column([ft.Text("환영합니다!", size=30), ft.Text("클릭하여 입장")], alignment="center"),
                on_tap=lambda e: change_view("main_dashboard")
            )

        elif view_name == "main_dashboard":
            page.session.set("logged_in", True)
            return ft.Column(
                [
                    ft.Text("리메지코드 메인 화면", size=30),
                    ft.ElevatedButton("로그아웃", on_click=lambda e: logout(e))
                ], alignment="center"
            )
        return ft.Text("로딩 중...")

    def logout(e):
        page.session.set("logged_in", False)
        change_view("login")

    # 앱 실행 시 로그인 상태 확인
    if page.session.get("logged_in"):
        change_view("main_dashboard")
    else:
        change_view("logo")

ft.app(target=main)