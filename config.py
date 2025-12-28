# [설정] 전역 변수 공유 파일
# 다른 파일에서 import config 하여 사용합니다.

conn = None                 # DB 연결 객체
cursor = None               # DB 커서 객체
current_user = None         # 로그인한 사용자 이름
current_household_id = None # 로그인한 사용자 ID (PK)
is_admin = False            # 관리자 여부