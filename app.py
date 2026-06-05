import flet as ft

def main(page: ft.Page):
    page.title = "리메지코드"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 페이지 컨테이너: 정렬 오류 방지를 위해 표준 속성 사용
    container = ft.Container(
        content=ft.Column(
            [
                ft.Text("리메지코드", size=40, weight="bold"),
                ft.Text("화면을 클릭하여 시작하세요")
            ],
            alignment="center",
            horizontal_alignment="center"
        ),
        expand=True
    )
    
    page.add(container)

ft.app(target=main)