import tkinter as tk
from tkinter import ttk, messagebox
import config

# =============================================================================
# 3단계: 메인 어플리케이션 클래스
# =============================================================================
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"공유창고 관리 시스템 - {config.current_user}님")
        self.root.geometry("1100x700")
        self.setup_ui()

    def setup_ui(self):
        # 1. 헤더 설정
        header = tk.Frame(self.root, bg="#343a40", height=50)
        header.pack(fill="x")
        role = "관리자" if config.is_admin else "입주민"
        
        tk.Label(header, text=f"접속자: {config.current_user} ({role})", bg="#343a40", fg="white", font=("맑은 고딕", 12)).pack(side="right", padx=20, pady=10)
        tk.Label(header, text="우리동네 물건 관리", bg="#343a40", fg="gold", font=("맑은 고딕", 15, "bold")).pack(side="left", padx=20, pady=10)

        # 2. 탭 컨테이너
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_tab1_manage()   # 물건 관리 탭
        self.create_tab2_register() # 등록 탭
        
        if config.is_admin:
            self.create_tab3_admin() # 관리자 탭

    # -------------------------------------------------------------------------
    # [탭 1] 물건 조회 및 관리
    # -------------------------------------------------------------------------
    def create_tab1_manage(self):
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="  물건 조회 및 관리  ")

        # 리스트 영역
        list_frame = tk.Frame(tab1)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "물건명", "보관위치", "구분", "소유자", "상태")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # 헤더 설정
        self.tree.heading("ID", text="번호")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("물건명", text="물건 이름")
        self.tree.column("물건명", width=250)
        self.tree.heading("보관위치", text="창고 위치")
        self.tree.column("보관위치", width=150, anchor="center")
        self.tree.heading("구분", text="유형")
        self.tree.column("구분", width=80, anchor="center")
        self.tree.heading("소유자", text="소유자")
        self.tree.column("소유자", width=100, anchor="center")
        self.tree.heading("상태", text="현재 상태")
        self.tree.column("상태", width=120, anchor="center")

        # 태그 색상
        self.tree.tag_configure('available', foreground='green')
        self.tree.tag_configure('in_use', foreground='blue')
        self.tree.tag_configure('broken', foreground='red')

        # 버튼 영역
        btn_frame = tk.Frame(tab1, bg="#f1f3f5", pady=10)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="새로고침", command=self.refresh_list, width=15).pack(side="right", padx=10)
        
        # 공공재 버튼
        tk.Frame(btn_frame, width=30, bg="#f1f3f5").pack(side="left")
        tk.Label(btn_frame, text="[공공재]", bg="#f1f3f5", font=("bold")).pack(side="left")
        tk.Button(btn_frame, text="대여하기", bg="#e3f2fd", command=self.borrow_public).pack(side="left", padx=5)
        tk.Button(btn_frame, text="반납하기", bg="#e3f2fd", command=self.return_public).pack(side="left", padx=5)
        
        # 개인물건 버튼
        tk.Frame(btn_frame, width=20, bg="#f1f3f5").pack(side="left")
        tk.Label(btn_frame, text="[개인물건]", bg="#f1f3f5", font=("bold")).pack(side="left")
        tk.Button(btn_frame, text="꺼내기(출고)", bg="#fff3e0", command=lambda: self.personal_action('OUT')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="넣기(입고)", bg="#fff3e0", command=lambda: self.personal_action('IN')).pack(side="left", padx=5)

        self.refresh_list()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        sql = """
            SELECT i.item_id, i.item_name, w.location_name, 
                   i.is_public, h.name as owner_name, i.status
            FROM Item i
            JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
            LEFT JOIN Household h ON i.owner_household_id = h.household_id
            WHERE i.is_public = 1 OR i.owner_household_id = %s
            ORDER BY i.item_id ASC
        """
        config.cursor.execute(sql, (config.current_household_id,))
        rows = config.cursor.fetchall()

        for row in rows:
            type_str = "공공재" if row['is_public'] else "개인물건"
            owner_str = row['owner_name'] if row['owner_name'] else "(공용)"
            status_map = {'available': '입고(보관중)', 'in_use': '출고(사용중)', 'broken': '수리필요(파손)'}
            status_disp = status_map.get(row['status'], row['status'])
            
            self.tree.insert("", "end", values=(
                row['item_id'], row['item_name'], row['location_name'], 
                type_str, owner_str, status_disp
            ), tags=(row['status'],))

    # --- 기능 메서드 ---
    def borrow_public(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("알림", "물건을 선택하세요.")
        val = self.tree.item(sel[0])['values']
        item_id, name, type_, status = val[0], val[1], val[3], val[5]

        if type_ != "공공재": return messagebox.showerror("오류", "개인 물건은 대여 불가")
        if "입고" not in status: return messagebox.showerror("오류", "대여 가능한 상태가 아님")

        if messagebox.askyesno("대여", f"[{name}] 대여하시겠습니까?"):
            try:
                config.cursor.execute("INSERT INTO Borrow (item_id, household_id, status) VALUES (%s, %s, 'borrowed')", (item_id, config.current_household_id))
                config.cursor.execute("INSERT INTO AccessLog (item_id, household_id, action) VALUES (%s, %s, 'OUT')", (item_id, config.current_household_id))
                config.conn.commit()
                messagebox.showinfo("성공", "대여 완료")
                self.refresh_list()
            except Exception as e:
                config.conn.rollback()
                messagebox.showerror("오류", str(e))

    def return_public(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("알림", "물건을 선택하세요.")
        val = self.tree.item(sel[0])['values']
        item_id, name, type_, status = val[0], val[1], val[3], val[5]

        if type_ != "공공재": return messagebox.showerror("오류", "공공재만 반납 가능")
        if "출고" not in status: return messagebox.showerror("오류", "대여중이 아님")

        # 본인 확인
        config.cursor.execute("SELECT borrow_id FROM Borrow WHERE item_id=%s AND household_id=%s AND status='borrowed'", (item_id, config.current_household_id))
        if not config.cursor.fetchone(): return messagebox.showerror("권한 없음", "본인이 대여한 물건만 반납 가능")

        is_bad = messagebox.askyesno("상태 확인", "물건이 파손되었습니까?\n(예=파손, 아니오=정상)")
        condition = 'bad' if is_bad else 'good'

        try:
            config.cursor.execute("UPDATE Borrow SET return_date=CURRENT_DATE, status='returned', return_condition=%s WHERE item_id=%s AND status='borrowed'", (condition, item_id))
            config.cursor.execute("INSERT INTO AccessLog (item_id, household_id, action) VALUES (%s, %s, 'IN')", (item_id, config.current_household_id))
            config.conn.commit()
            messagebox.showinfo("성공", "반납 완료")
            self.refresh_list()
        except Exception as e:
            config.conn.rollback()
            messagebox.showerror("오류", str(e))

    def personal_action(self, action):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("알림", "물건을 선택하세요.")
        val = self.tree.item(sel[0])['values']
        item_id, type_, status = val[0], val[3], val[5]

        if type_ == "공공재": return messagebox.showerror("오류", "공공재는 대여/반납 이용")
        
        target_status = 'in_use' if action == 'OUT' else 'available'
        if action == 'OUT' and "출고" in status: return messagebox.showerror("오류", "이미 출고됨")
        if action == 'IN' and "입고" in status: return messagebox.showerror("오류", "이미 입고됨")

        try:
            config.cursor.execute("UPDATE Item SET status=%s WHERE item_id=%s", (target_status, item_id))
            config.cursor.execute("INSERT INTO AccessLog (item_id, household_id, action) VALUES (%s, %s, %s)", (item_id, config.current_household_id, action))
            config.conn.commit()
            messagebox.showinfo("성공", "처리되었습니다.")
            self.refresh_list()
        except Exception as e:
            config.conn.rollback()
            messagebox.showerror("오류", str(e))

    # -------------------------------------------------------------------------
    # [탭 2] 물건 등록
    # -------------------------------------------------------------------------
    def create_tab2_register(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="  신규 등록  ")
        
        frame = tk.Frame(tab2, pady=50)
        frame.pack()

        tk.Label(frame, text="물건 이름:", font=("맑은 고딕", 12)).grid(row=0, column=0, pady=10, sticky="e")
        self.entry_reg_name = tk.Entry(frame, width=30)
        self.entry_reg_name.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(frame, text="보관 창고:", font=("맑은 고딕", 12)).grid(row=1, column=0, pady=10, sticky="e")
        
        # 창고 로드
        self.wh_dict = {}
        try:
            config.cursor.execute("SELECT warehouse_id, location_name FROM Warehouse")
            for w in config.cursor.fetchall():
                self.wh_dict[w['location_name']] = w['warehouse_id']
        except: pass
        
        self.combo_wh = ttk.Combobox(frame, values=list(self.wh_dict.keys()), state="readonly", width=27)
        self.combo_wh.grid(row=1, column=1, pady=10, padx=10)
        if self.wh_dict: self.combo_wh.current(0)

        self.var_public = tk.BooleanVar()
        if config.is_admin:
            tk.Checkbutton(frame, text="공공재로 등록", variable=self.var_public).grid(row=2, column=1, pady=20, sticky="w")

        tk.Button(frame, text="등록 완료", command=self.register_item, bg="#007bff", fg="white", width=20).grid(row=3, column=0, columnspan=2, pady=30)

    def register_item(self):
        name = self.entry_reg_name.get().strip()
        wh_name = self.combo_wh.get()
        if not name or not wh_name: return messagebox.showwarning("알림", "정보 입력 필요")

        wh_id = self.wh_dict[wh_name]
        is_pub = 1 if (config.is_admin and self.var_public.get()) else 0
        owner = None if is_pub else config.current_household_id

        try:
            sql = "INSERT INTO Item (warehouse_id, item_name, owner_household_id, is_public, status) VALUES (%s, %s, %s, %s, 'available')"
            config.cursor.execute(sql, (wh_id, name, owner, is_pub))
            config.conn.commit()
            messagebox.showinfo("성공", "등록되었습니다.")
            self.entry_reg_name.delete(0, "end")
            self.refresh_list()
        except Exception as e:
            config.conn.rollback()
            messagebox.showerror("실패", str(e))

    # -------------------------------------------------------------------------
    # [탭 3] 관리자 탭
    # -------------------------------------------------------------------------
    def create_tab3_admin(self):
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="  세대 관리 (관리자)  ")
        
        frame = tk.Frame(tab3, pady=30)
        frame.pack()
        
        cols = ["동", "호", "이름", "전화번호", "비밀번호"]
        self.adm_entries = {}
        for i, col in enumerate(cols):
            tk.Label(frame, text=col).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(frame, width=25)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.adm_entries[col] = entry

        tk.Button(frame, text="세대 추가", command=self.add_household, width=20).grid(row=6, column=0, columnspan=2, pady=20)

    def add_household(self):
        vals = [e.get().strip() for e in self.adm_entries.values()]
        if any(not v for v in vals): return messagebox.showwarning("알림", "모든 정보 입력")
        
        try:
            sql = "INSERT INTO Household (dong, ho, name, phone, password) VALUES (%s, %s, %s, %s, %s)"
            config.cursor.execute(sql, tuple(vals))
            config.conn.commit()
            messagebox.showinfo("성공", "추가되었습니다.")
            for e in self.adm_entries.values(): e.delete(0, "end")
        except Exception as e:
            messagebox.showerror("실패", str(e))

    def run(self):
        self.root.mainloop()