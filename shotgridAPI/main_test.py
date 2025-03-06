
from shotgrid_db import ShotgridDB
from shotgrid_connector import ShotGridAPI
from shotgrid_manager import ShotGridManager

# 사용 예시
sg_db = ShotgridDB()
sg_api = ShotGridAPI()
manager = ShotGridManager()


# # 특정 유저 ID (예: 132)로 해당 유저가 속한 프로젝트 조회
# user_projects = sg_api.get_user_projects(132)
# # 유저의 프로젝트 정보를 데이터베이스에 저장
# for project in user_projects:
#     project_data = sg_api.get_project_details(project["id"])
#     sg_db.save_project_data(project_data)

# 특정 프로젝트의 에셋 조회
project_name = "Viper"
assets = manager.get_project_assets(project_name)
print(f"📂 프로젝트 {project_name}의 에셋 목록: {assets}")

# 특정 프로젝트의 시퀀스 조회
project_name = "Viper"
assets = manager.get_project_sequences(project_name)
print(f"📂 프로젝트 {project_name}의 시퀀스 목록: {assets}")

# 특정 Task의 id로 해당 Task 정보 조회
task_id = 6049
task = manager.get_task_by_id(task_id)
print(f"🗂 Task {task_id}의 정보: {task}")

# 특정 Task의 퍼블리시 파일 가져오기
task_id = 6049
published_files = manager.get_publishes_for_task(task_id)
print(f"🗂 Task {task_id}의 퍼블리시 파일: {published_files}")

# 유저 ID로 Task 조회
user_id = 132
tasks = manager.get_tasks_by_user(user_id)
print(f"🔍 유저 {user_id}의 테스크 목록: {tasks}")

# 특정 상태의 Task 필터링
ip_tasks = manager.filter_tasks_by_status(tasks, "ip")
print(f"🔍 유저 {user_id}의 ip 테스크 목록: {ip_tasks}")

# 로컬 Work 파일 검색
# work_files = manager.find_work_files(project_name)
# print(f"💾 로컬 Work 파일 목록: {work_files}")

# # 특정 Task 설명 업데이트
# manager.update_task_description(task_id, "이 테스크는 중요함!")

# manager.close()