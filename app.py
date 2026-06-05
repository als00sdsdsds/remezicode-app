import flet as ft
import sqlite3

# -----------------------------
# 데이터베이스 초기화
# -----------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT
)
""")
conn.commit()


def main(page: ft.Page):
    page.title = "리메지코드"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    container = ft.Container(expand=True)
    page.add(container)

    def show_message(title, message):
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message)
        )
        page.open(dialog)

    def change_view(view_name):
        container.content = build_view(view_name)
        page.update()

    def build_view(view_name):

        # -----------------------------
        # 로고 화면
        # -----------------------------
        if view_name == "logo":
            return ft.GestureDetector(
                content=ft.Column(
                    [
                        ft.Text("리메지코드", size=40, weight=ft.FontWeight.BOLD),
                        ft.Text("클릭하여 시작")
                    ],
                    alignment="center",
                    horizontal_alignment="center"
                ),
                on_tap=lambda e: change_view(
                    "main_dashboard"
                    if page.client_storage.get("logged_in")
                    else "login"
                )
            )

        # -----------------------------
        # 로그인
        # -----------------------------
        elif view_name == "login":

            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)

            def login_check(e):

                cursor.execute(
                    "SELECT * FROM users WHERE id=? AND password=?",
                    (id_f.value, pw_f.value)
                )

                user = cursor.fetchone()

                if user:
                    page.client_storage.set("logged_in", True)
                    page.client_storage.set("user_id", id_f.value)

                    change_view("main_dashboard")

                else:
                    show_message(
                        "로그인 실패",
                        "아이디 또는 비밀번호가 올바르지 않습니다."
                    )

            return ft.Column(
                [
                    ft.Text("로그인", size=30),
                    id_f,
                    pw_f,
                    ft.ElevatedButton(
                        "로그인",
                        on_click=login_check
                    ),
                    ft.TextButton(
                        "회원가입",
                        on_click=lambda e: change_view("signup")
                    )
                ],
                alignment="center"
            )

        # -----------------------------
        # 회원가입
        # -----------------------------
        elif view_name == "signup":

            email_f = ft.TextField(label="이메일")
            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)

            def register(e):

                if not id_f.value or not pw_f.value:
                    show_message(
                        "오류",
                        "아이디와 비밀번호를 입력하세요."
                    )
                    return

                cursor.execute(
                    "SELECT id FROM users WHERE id=?",
                    (id_f.value,)
                )

                if cursor.fetchone():
                    show_message(
                        "중복 아이디",
                        "이미 사용 중인 아이디입니다."
                    )
                    return

                cursor.execute(
                    """
                    INSERT INTO users(id, password, email)
                    VALUES(?,?,?)
                    """,
                    (
                        id_f.value,
                        pw_f.value,
                        email_f.value
                    )
                )

                conn.commit()

                show_message(
                    "회원가입 완료",
                    "회원가입이 성공적으로 완료되었습니다."
                )

                change_view("welcome")

            return ft.Column(
                [
                    ft.Text("회원가입", size=30),
                    email_f,
                    id_f,
                    pw_f,
                    ft.ElevatedButton(
                        "가입하기",
                        on_click=register
                    )
                ],
                alignment="center"
            )

        # -----------------------------
        # 가입 완료
        # -----------------------------
        elif view_name == "welcome":
            return ft.GestureDetector(
                content=ft.Column(
                    [
                        ft.Text("환영합니다!", size=30),
                        ft.Text("클릭하여 입장")
                    ],
                    alignment="center",
                    horizontal_alignment="center"
                ),
                on_tap=lambda e: change_view("main_dashboard")
            )

        # -----------------------------
        # 메인 대시보드
        # -----------------------------
        elif view_name == "main_dashboard":

            user_id = page.client_storage.get("user_id")

            return ft.Column(
                [
                    ft.Text(
                        "리메지코드 메인 화면",
                        size=30
                    ),
                    ft.Text(
                        f"{user_id}님 환영합니다."
                    ),
                    ft.ElevatedButton(
                        "로그아웃",
                        on_click=logout
                    )
                ],
                alignment="center"
            )

        return ft.Text("로딩 중...")

    # -----------------------------
    # 로그아웃
    # -----------------------------
    def logout(e):
        page.client_storage.set("logged_in", False)

        try:
            page.client_storage.remove("user_id")
        except:
            pass

        change_view("login")

    # -----------------------------
    # 시작 화면
    # -----------------------------
    if page.client_storage.get("logged_in"):
        change_view("main_dashboard")
    else:
        change_view("logo")


ft.app(target=main)