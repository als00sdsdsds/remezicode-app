import flet as ft

def main(page: ft.Page):
    page.title = "리메지코드"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 화면을 전환하기 위한 컨테이너
    container = ft.Container(expand=True)
    page.add(container)

    # 화면 전환 함수
    def go_to_login(e):
        container.content = ft.Column([
            ft.Text("로그인", size=30, weight="bold"),
            ft.TextField(label="아이디"),
            ft.TextField(label="비밀번호", password=True),
            ft.ElevatedButton("로그인"),
            ft.TextButton("회원가입")
        ], alignment="center", horizontal_alignment="center")
        page.update()

    # 첫 화면 (로고 화면)
    container.content = ft.GestureDetector(
        content=ft.Container(
            content=ft.Column([
                ft.Text("리메지코드", size=40, weight="bold"),
                ft.Text("화면을 클릭하여 시작하세요")
            ], alignment="center", horizontal_alignment="center"),
            alignment=ft.alignment.center
        ),
        on_tap=go_to_login  # 클릭 시 go_to_login 함수 실행
    )

    page.update()

ft.app(target=main)