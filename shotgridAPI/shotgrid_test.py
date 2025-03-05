
from user_authenticator import UserAuthenticator
from shotgrid_connector import ShotGridConnector


"""
실행 예시
"""

# 사용자 로그인
user = UserAuthenticator.login("owlgrowl0v0@gmail.com")
if user:
    print(f"로그인 성공! 사용자 ID: {user['id']}, 역할: {user['permission_rule_set']}")

# 특정 사용자의 Task 가져오기
tasks = ShotGridConnector.get_user_tasks(user["id"])
print(f"할당된 Task: {tasks}")

# Task 상태 확인
task_id = tasks[0]["id"]  # 첫 번째 Task의 ID 사용
status = ShotGridConnector.get_task_status(task_id)
print(f"Task {task_id} 상태: {status}")

# Task 안에 있는 published 파일 가져오기
task_id = 6057 # 퍼블리시 파일이 있는 경우에만 내부 파일이 떠서 임의로 특정 테스크 아이디를 사용
publish_list = ShotGridConnector.get_publishes_for_task(task_id)
print(f"Task {task_id} 퍼블리시 파일: {publish_list}")

# # Task 상태 업데이트
# ShotGridConnector.update_task(task_id, "ip")  # 작업 시작 (IP 상태로 변경)
# print(f"Task {task_id} 상태를 'In Progress'로 변경 완료!")

# # Task 완료 처리
# ShotGridConnector.mark_task_as_complete(task_id)
# print(f"Task {task_id} 상태를 'Final'로 변경 완료!")