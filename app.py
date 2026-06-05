import flet as ft
import sqlite3
from datetime import datetime, timedelta
import re

# -----------------------------
# DB 설정
# -----------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT,
    delete_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS app_state (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

conn.commit()


# -----------------------------
# 자동 삭제
# -----------------------------
def cleanup_deleted_users():
    now = datetime.now().isoformat()
    cursor.execute(
        "DELETE FROM users WHERE delete_at IS NOT NULL AND delete_at < ?",
        (now,)
    )
    conn.commit()


# -----------------------------
# 현재 로그인 유저
# -----------------------------
def get_current_user():
    cursor.execute(
        "SELECT value FROM app_state WHERE key='current_user'"
    )
    row = cursor.fetchone()
    return row[0] if row else None


# -----------------------------
# 탈퇴 예약
# -----------------------------
def request_delete(user_id):
    delete_date = (datetime.now() + timedelta(days=7)).isoformat()

    cursor.execute(
        "UPDATE users SET delete_at=? WHERE id=?",
        (delete_date, user_id)
    )
    conn.commit()


# -----------------------------
# 입력 검증
# -----------------------------
def valid_email(email):
    return email and "@" in email and "." in email

def valid_id(user_id):
    return user_id and len(user_id) >= 5 and re.search(r"[a-zA-Z]", user_id)

def valid_password(pw):
    return (
        pw and len(pw) >= 9 and
        re.search(r"[a-zA-Z]", pw) and
        re.search(r"[0-9]", pw) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw)
    )


# -----------------------------
# 앱 시작
# -----------------------------
def main(page: ft.Page):
    page.title = "리메지코드"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    container = ft.Container(expand=True)
    page.add(container)

    cleanup_deleted_users()

    # -----------------------------
    # alert (안정 버전)
    # -----------------------------
    def alert(title, msg):
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(msg)
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    # -----------------------------
    # 화면 전환
    # -----------------------------
    def change_view(view):
        container.content = build_view(view)
        page.update()

    # -----------------------------
    # 화면 구성
    # -----------------------------
    def build_view(view):

        # ----------------- 로고 -----------------
        if view == "logo":

            def go(e):
                print("CLICK OK")

                if get_current_user():
                    change_view("main")
                else:
                    change_view("login")

            return ft.Container(
                expand=True,
                alignment="center",   # ✅ 수정 (핵심)
                content=ft.InkWell(
                    on_tap=go,
                    content=ft.Column(
                        [
                            ft.Text("리메지코드", size=40),
                            ft.Text("클릭해서 시작")
                        ],
                        alignment="center"
                    )
                )
            )

        # ----------------- 로그인 -----------------
        elif view == "login":

            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)

            def login(e):
                cursor.execute(
                    "SELECT * FROM users WHERE id=? AND password=?",
                    (id_f.value, pw_f.value)
                )
                user = cursor.fetchone()

                if user:
                    cursor.execute(
                        "INSERT OR REPLACE INTO app_state(key,value) VALUES(?,?)",
                        ("current_user", id_f.value)
                    )
                    conn.commit()
                    change_view("main")
                else:
                    alert("로그인 실패", "아이디 또는 비밀번호 오류")

            return ft.Column(
                [
                    ft.Text("로그인", size=30),
                    id_f,
                    pw_f,
                    ft.ElevatedButton("로그인", on_click=login),
                    ft.TextButton("회원가입", on_click=lambda e: change_view("signup"))
                ],
                alignment="center"
            )

        # ----------------- 회원가입 -----------------
        elif view == "signup":

            email_f = ft.TextField(label="이메일")
            id_f = ft.TextField(label="아이디")
            pw_f = ft.TextField(label="비밀번호", password=True)

            def register(e):

                if not valid_email(email_f.value):
                    alert("오류", "이메일 형식 오류")
                    return

                if not valid_id(id_f.value):
                    alert("오류", "아이디는 영문 포함 5자 이상")
                    return

                if not valid_password(pw_f.value):
                    alert("오류", "비밀번호는 영문/숫자/특수문자 9자 이상")
                    return

                cursor.execute("SELECT id FROM users WHERE id=?", (id_f.value,))
                if cursor.fetchone():
                    alert("오류", "이미 존재하는 아이디")
                    return

                cursor.execute(
                    "INSERT INTO users(id,password,email) VALUES(?,?,?)",
                    (id_f.value, pw_f.value, email_f.value)
                )
                conn.commit()

                alert("완료", "회원가입 성공")
                change_view("login")

            return ft.Column(
                [
                    ft.Text("회원가입", size=30),
                    email_f,
                    id_f,
                    pw_f,
                    ft.ElevatedButton("가입하기", on_click=register)
                ],
                alignment="center"
            )

        # ----------------- 메인 -----------------
        elif view == "main":

            user = get_current_user()

            def logout(e):
                cursor.execute("DELETE FROM app_state WHERE key='current_user'")
                conn.commit()
                change_view("login")

            def delete_account(e):
                request_delete(user)
                logout(e)

            return ft.Column(
                [
                    ft.Text("메인 화면", size=30),
                    ft.Text(f"{user}님 환영합니다"),
                    ft.ElevatedButton("로그아웃", on_click=logout),
                    ft.ElevatedButton("회원 탈퇴 (7일 후 삭제)", on_click=delete_account)
                ],
                alignment="center"
            )

        return ft.Text("로딩중")

    # -----------------------------
    # 시작 화면
    # -----------------------------
    if get_current_user():
        change_view("main")
    else:
        change_view("logo")


ft.app(target=main)