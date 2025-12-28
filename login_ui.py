import tkinter as tk
from tkinter import messagebox
import pymysql
import config
from main_ui import MainApp  # 로그인 성공 시 메인 화면 실행을 위해 import

# =============================================================================
# 1단계: DB 접속 윈도우 클래스
# =============================================================================
class DBLoginWindow:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("공유창고 시스템 - 서버 접속")
        self.setup_ui()
        
    def setup_ui(self):
        # 화면 중앙 배치
        self.win.geometry("400x350")
        self.win.eval('tk::PlaceWindow . center')

        tk.Label(self.win, text="서버 접속 설정", font=("맑은 고딕", 20, "bold")).pack(pady=20)
        
        frame = tk.Frame(self.win)
        frame.pack(pady=10)

        # 입력 필드 생성
        fields = [("호스트", "localhost"), ("포트", "3306"), ("사용자", ""), ("비밀번호", ""), ("DB이름", "")]
        self.entries = {}

        for idx, (label, default) in enumerate(fields):
            tk.Label(frame, text=label, width=10, anchor="e").grid(row=idx, column=0, padx=5, pady=5)
            entry = tk.Entry(frame, width=20)
            if "비밀번호" in label:
                entry.config(show="*")
            entry.insert(0, default)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[label] = entry

        tk.Button(self.win, text="시스템 접속", command=self.connect_db, bg="#007bff", fg="white", width=20, height=2).pack(pady=20)

    def connect_db(self):
        try:
            # config 모듈의 전역 변수에 저장
            config.conn = pymysql.connect(
                host=self.entries["호스트"].get(),
                port=int(self.entries["포트"].get()),
                user=self.entries["사용자"].get(),
                password=self.entries["비밀번호"].get(),
                db=self.entries["DB이름"].get(),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            config.cursor = config.conn.cursor()
            print("[System] DB 연결 성공")
            
            # 현재 창 닫고 로그인 창 열기
            self.win.destroy()
            UserLoginWindow().run()
            
        except Exception as e:
            messagebox.showerror("접속 실패", f"DB 연결 오류:\n{e}\n\nMySQL 실행 여부를 확인하세요.")

    def run(self):
        self.win.mainloop()


# =============================================================================
# 2단계: 사용자 로그인 윈도우 클래스
# =============================================================================
class UserLoginWindow:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("세대 로그인")
        self.setup_ui()

    def setup_ui(self):
        self.win.geometry("400x300")
        self.win.eval('tk::PlaceWindow . center')

        tk.Label(self.win, text="우리동네 공유창고", font=("맑은 고딕", 20, "bold")).pack(pady=30)

        frame = tk.Frame(self.win)
        frame.pack()

        tk.Label(frame, text="이름").grid(row=0, column=0, pady=5)
        self.entry_name = tk.Entry(frame)
        self.entry_name.insert(0, "")
        self.entry_name.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="비밀번호").grid(row=1, column=0, pady=5)
        self.entry_pw = tk.Entry(frame, show="*")
        self.entry_pw.insert(0, "")
        self.entry_pw.grid(row=1, column=1, pady=5)

        tk.Button(self.win, text="로그인", command=self.login, bg="#28a745", fg="white", width=15).pack(pady=20)

    def login(self):
        name = self.entry_name.get().strip()
        pw = self.entry_pw.get().strip()

        sql = "SELECT household_id, name, is_admin FROM Household WHERE name=%s AND password=%s"
        config.cursor.execute(sql, (name, pw))
        result = config.cursor.fetchone()

        if result:
            # config 모듈에 사용자 정보 저장
            config.current_user = result['name']
            config.current_household_id = result['household_id']
            config.is_admin = bool(result['is_admin'])
            
            print(f"[System] 로그인 성공: {config.current_user}")
            
            self.win.destroy()
            MainApp().run()  # 메인 프로그램 실행
        else:
            messagebox.showerror("로그인 실패", "이름 또는 비밀번호를 확인해주세요.")

    def run(self):
        self.win.mainloop()