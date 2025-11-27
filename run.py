from login_ui import DBLoginWindow

# 프로그램 실행 (Entry Point)

if __name__ == "__main__":
    # 1단계: DB 접속 윈도우 실행
    # (성공 시 내부적으로 로그인 -> 메인 화면으로 전환됨)
    app = DBLoginWindow()
    app.run()