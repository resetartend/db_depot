# 📦 DB Depot (Shared Warehouse Management System)

**DB Depot**은 파이썬(Python) 기반의 **공유 창고 관리 프로그램**입니다.
직관적인 GUI 환경을 통해 물품의 입출고, 재고 현황 확인, 사용자 관리 등을 효율적으로 처리할 수 있도록 설계되었습니다.

## ✨ 주요 기능 (Key Features)

* **🔐 사용자 로그인 (User Authentication):** `login_ui`를 통한 안전한 사용자 접근 제어.
* **📊 대시보드 및 메인 관리 (Main Dashboard):** `main_ui`를 통해 창고의 전체적인 현황을 한눈에 파악.
* **🗃️ 데이터베이스 연동:** 물품 정보 및 사용자 데이터를 데이터베이스에 안전하게 저장 및 관리.
* **⚙️ 간편한 설정:** `config.py`를 통한 데이터베이스 연결 및 환경 설정 관리.

## 🛠️ 기술 스택 (Tech Stack)

* **Language:** Python 3.x
* **GUI Framework:** (예: PyQt5, Tkinter 등 실제 사용된 라이브러리에 맞춰 수정 필요)
* **Database:** (예: MySQL, SQLite, PostgreSQL 등 `config.py`에서 사용하는 DB 기재)

## 📂 디렉토리 구조 (Directory Structure)

```bash
db_depot/
├── 📄 config.py          # 데이터베이스 연결 및 프로젝트 설정 파일
├── 📄 login_ui.py        # 로그인 화면 UI 구성 코드
├── 📄 main_ui.py         # 메인 관리 화면 UI 구성 코드
├── 📄 run.py             # 프로그램 실행 진입점 (Entry Point)
├── 📄 requirements.txt   # 의존성 패키지 목록
└── 📄 README.md          # 프로젝트 설명서
