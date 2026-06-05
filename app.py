import flet as ft

def main(page: ft.Page):
    page.title = "Remezicode 앱"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # 1. AI 검증 로직 (금지어 체크)
    def is_content_safe(text):
        forbidden_words = ["바보", "나쁜말", "욕설"]
        return not any(word in text for word in forbidden_words)

    # 2. 화면 이동 함수들
    def go_to_signup(e):
        page.clean()
        page.add(signup_view)
        page.update()

    def go_to_profile(e):
        page.clean()
        page.add(profile_view)
        page.update()

    def go_to_login(e):
        page.clean()
        page.add(login_view)
        page.update()

    def go_to_main(e):
        # AI 검증 수행
        if not is_content_safe(nickname_field.value) or not is_content_safe(status_field.value):
            page.show_snack_bar(ft.SnackBar(content=ft.Text("가이드라인을 준수해주세요! (부적절한 단어 포함)")))
            return
        page.clean()
        page.add(tab_bar, home_view)
        page.update()

    # 3. 화면 구성 요소
    # 로그인 화면
    login_view = ft.Container(
        content=ft.Column([
            ft.Text("로그인", size=30, weight="bold"),
            ft.TextField(label="아이디"),
            ft.TextField(label="비밀번호", password=True),
            ft.ElevatedButton("로그인", on_click=go_to_main, width=200),
            ft.TextButton("회원가입하기", on_click=go_to_signup)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40
    )

    # 회원가입 화면
    signup_view = ft.Container(
        content=ft.Column([
            ft.Text("회원가입", size=30, weight="bold"),
            ft.TextField(label="아이디"),
            ft.TextField(label="이메일"),
            ft.ElevatedButton("인증번호 발송", on_click=lambda _: print("인증번호 전송")),
            ft.TextField(label="인증번호 6자리"),
            ft.TextField(label="비밀번호", password=True),
            ft.ElevatedButton("다음 단계", on_click=go_to_profile, width=200)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40
    )

    # 프로필 설정 화면
    nickname_field = ft.TextField(label="닉네임")
    status_field = ft.TextField(label="상태 메시지")
    profile_view = ft.Container(
        content=ft.Column([
            ft.Text("프로필 설정", size=30, weight="bold"),
            ft.CircleAvatar(content=ft.Icon("person"), radius=50),
            ft.ElevatedButton("프로필 사진 변경"),
            nickname_field,
            status_field,
            ft.ElevatedButton("가입 완료 (AI 검증)", on_click=go_to_main, width=200)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40
    )

    # 4. 네비게이션 및 메인 화면
    def tab_changed(e):
        index = e.control.selected_index
        page.clean()
        page.add(tab_bar)
        if index == 0:
            page.add(home_view)
        else:
            page.add(mail_view)
        page.update()

    tab_bar = ft.NavigationBar(
        selected_index=0,
        on_change=tab_changed,
        destinations=[
            ft.NavigationBarDestination(icon="home", label="홈"),
            ft.NavigationBarDestination(icon="mail", label="우체통"),
        ],
    )

    home_view = ft.Container(
        content=ft.Column([
            ft.Text("오늘의 마음 나누기", size=20, weight="bold"),
            ft.TextField(label="고민 입력", multiline=True, min_lines=3),
            ft.ElevatedButton("글 등록", icon="send")
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=20
    )

    mail_view = ft.Container(
        content=ft.Column([
            ft.Text("내 우체통", size=20, weight="bold"),
            ft.ListTile(leading=ft.Icon("email"), title=ft.Text("첫 번째 위로 편지")),
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=20
    )

    # 초기 앱 실행
    page.add(login_view)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)