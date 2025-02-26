
# from shotgun_api3 import Shotgun
# # from shotgrid_connector import ShotGridConnector

# class ShotGridConnector:
#     """ShotGrid API와 연동하여 데이터를 가져오는 클래스"""

#     def __init__(self, sg_url, script_name, api_key):
#         """
#         :param sg_url: ShotGrid 서버 URL
#         :param script_name: ShotGrid API 스크립트 이름
#         :param api_key: ShotGrid API 키
#         """
#         self.sg = Shotgun(sg_url, script_name, api_key)

#     def get_user_tasks(self, user_id):
#         """현재 사용자의 Task 목록을 가져옴"""
#         filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
#         fields = ["id", "content", "entity"]
#         tasks = self.sg.find("Task", filters, fields)
#         return tasks

#     def get_task_versions(self, task_id):
#         """특정 Task에 연결된 Version 목록을 가져옴"""
#         filters = [["sg_task", "is", {"type": "Task", "id": task_id}]]
#         fields = ["id", "code", "created_at"]
#         versions = self.sg.find("Version", filters, fields)
#         return versions

#     def update_task_status(self, task_id, new_status):
#         """Task의 상태(PND→IP 등)를 변경"""
#         data = {"sg_status_list": new_status}
#         self.sg.update("Task", task_id, data)

# class ShotGridFileManager:
#     """ShotGrid에서 Task에 연결된 파일 정보를 정렬하는 클래스"""

#     def __init__(self, sg_connector):
#         """
#         sg_connector: ShotGridConnector 인스턴스
#         """
#         self.sg_connector = sg_connector

#     def get_sorted_files_for_user(self, user_id, sort_by="created_at"):
#         """
#         주어진 사용자의 Task와 연결된 파일 정보를 정렬하여 반환.

#         user_id: ShotGrid에서 검색할 사용자 ID
#         sort_by: 정렬 기준 (예: "created_at", "name")
#         return: 정렬된 파일 목록 (리스트)
#         """
#         # 1️ 현재 사용자의 Task 목록 가져오기
#         tasks = self.sg_connector.get_user_tasks(user_id)
#         if not tasks:
#             return []

#         file_list = []

#         # 2️ 각 Task에 연결된 파일(Version) 정보 가져오기
#         for task in tasks:
#             task_id = task["id"]
#             versions = self.sg_connector.get_task_versions(task_id)  # Task의 Version 정보 가져오기

#             for version in versions:
#                 file_list.append({
#                     "task_id": task_id,
#                     "task_name": task["content"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 3️ 파일 목록을 정렬 (기본: 생성 날짜 기준)
#         sorted_files = sorted(file_list, key=lambda x: x[sort_by])

#         return sorted_files


# # 사용 예시
# SG_URL = "https://minseo.shotgrid.autodesk.com"
# SCRIPT_NAME = "Viper"
# API_KEY = "jvceqpsfqvbl1azzcns?haksI"

# sg_connector = ShotGridConnector(SG_URL, SCRIPT_NAME, API_KEY)
# file_manager = ShotGridFileManager(sg_connector)

# user_id = 1234  # 예제 사용자 ID
# sorted_files = file_manager.get_sorted_files_for_user(user_id, sort_by="created_at")

# for file in sorted_files:
#     print(file)






# ############################################################################################################
# ######################################### 오류 시 수정코드 ##################################################
# ############################################################################################################

# class ShotGridConnector:
#     """ShotGrid API와 연동하여 데이터를 가져오는 클래스"""

#     def __init__(self, sg_url, script_name, api_key):
#         self.sg = Shotgun(sg_url, script_name, api_key)

#     def get_user_tasks(self, user_id):
#         filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
#         fields = ["id", "content", "entity", "task_assignees"]
#         return self.sg.find("Task", filters, fields) or []

#     def get_task_versions(self, task_id):
#         filters = [["sg_task", "is", {"type": "Task", "id": task_id}]]
#         fields = ["id", "code", "created_at"]
#         return self.sg.find("Version", filters, fields) or []

# # id: Task의 id
# # content: Task의 제목
# # entity: Task가 연결된 Asset 또는 Shot
# # task_assignees: 작업을 할당받은 사용자
 
# class ShotGridFileManager:
#     """ShotGrid에서 Task에 연결된 파일 정보를 정렬하는 클래스"""

#     def __init__(self, sg_connector):
#         self.sg_connector = sg_connector

#     def get_sorted_files_for_user(self, user_id, sort_by="created_at"):
#         tasks = self.sg_connector.get_user_tasks(user_id)
#         if not tasks:
#             return []

#         file_list = []
#         for task in tasks:
#             task_id = task.get("id")
#             versions = self.sg_connector.get_task_versions(task_id)

#             for version in versions:
#                 file_list.append({
#                     "task_id": task_id,
#                     "task_name": task.get("content", "Unnamed Task"),
#                     "version_id": version.get("id"),
#                     "file_name": version.get("code", "Unknown"),
#                     "created_at": version.get("created_at", "")
#                 })

#         sorted_files = sorted(file_list, key=lambda x: x[sort_by] or "")
#         return sorted_files




#################################################################################################################
######################################### 태스크 샷 에셋만 가져오도록 수정한 코드 ##################################
#################################################################################################################




# from shotgun_api3 import Shotgun

# class ShotGridConnector:
#     """ShotGrid API와 연동하여 로그인한 사용자에 대한 Tasks, Shots, Assets 데이터를 가져오는 클래스"""

#     def __init__(self, sg_url, script_name, api_key):
#         self.sg = Shotgun(sg_url, script_name, api_key)
#         self.user_data = None  # 로그인한 사용자 데이터 저장용

#     def get_user_data(self, username):
#         """ShotGrid에서 로그인한 사용자 정보 가져오기"""
#         filters = [["login", "is", username]]
#         fields = ["id", "name", "email"]
#         user = self.sg.find_one("HumanUser", filters, fields)

#         if user:
#             self.user_data = user  # 사용자 정보 저장
#             return user
#         else:
#             return {"error": "User not found"}

#     def get_user_tasks(self):
#         """로그인한 사용자에게 할당된 Task 목록 가져오기"""
#         if not self.user_data:
#             return {"error": "User not authenticated"}

#         user_id = self.user_data["id"]
#         filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
#         fields = ["id", "content", "entity", "sg_status_list"]
#         return self.sg.find("Task", filters, fields) or []

#     def get_user_shots(self):
#         """로그인한 사용자가 작업 중인 Shots 목록 가져오기"""
#         if not self.user_data:
#             return {"error": "User not authenticated"}

#         user_id = self.user_data["id"]
#         filters = [["sg_artist", "is", {"type": "HumanUser", "id": user_id}]]
#         fields = ["id", "code", "sg_status_list"]
#         return self.sg.find("Shot", filters, fields) or []

#     def get_user_assets(self):
#         """로그인한 사용자가 작업 중인 Assets 목록 가져오기"""
#         if not self.user_data:
#             return {"error": "User not authenticated"}

#         user_id = self.user_data["id"]
#         filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
#         fields = ["id", "code", "sg_status_list"]
#         return self.sg.find("Asset", filters, fields) or []


# class ShotGridFileManager:
#     """ShotGrid에서 로그인한 사용자의 Task, Shot, Asset에 연결된 파일 정보를 정렬하는 클래스"""

#     def __init__(self, sg_connector):
#         self.sg_connector = sg_connector

#     def get_sorted_files_for_user(self, sort_by="created_at"):
#         """
#         로그인한 사용자의 Task, Shot, Asset에 연결된 파일 정보를 정렬하여 반환.
#         """
#         if not self.sg_connector.user_data:
#             return {"error": "User not authenticated"}

#         file_list = []

#         # 1. 사용자 Tasks에 연결된 파일 가져오기
#         tasks = self.sg_connector.get_user_tasks()
#         for task in tasks:
#             task_id = task["id"]
#             versions = self.sg_connector.sg.find("Version", [["sg_task", "is", {"type": "Task", "id": task_id}]], 
#                                                  ["id", "code", "created_at"])
#             for version in versions:
#                 file_list.append({
#                     "category": "Task",
#                     "task_id": task_id,
#                     "task_name": task["content"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 2. 사용자 Shots에 연결된 파일 가져오기
#         shots = self.sg_connector.get_user_shots()
#         for shot in shots:
#             shot_id = shot["id"]
#             versions = self.sg_connector.sg.find("Version", [["entity", "is", {"type": "Shot", "id": shot_id}]], 
#                                                  ["id", "code", "created_at"])
#             for version in versions:
#                 file_list.append({
#                     "category": "Shot",
#                     "shot_id": shot_id,
#                     "shot_name": shot["code"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 3. 사용자 Assets에 연결된 파일 가져오기
#         assets = self.sg_connector.get_user_assets()
#         for asset in assets:
#             asset_id = asset["id"]
#             versions = self.sg_connector.sg.find("Version", [["entity", "is", {"type": "Asset", "id": asset_id}]], 
#                                                  ["id", "code", "created_at"])
#             for version in versions:
#                 file_list.append({
#                     "category": "Asset",
#                     "asset_id": asset_id,
#                     "asset_name": asset["code"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 4. 파일 목록을 정렬
#         sorted_files = sorted(file_list, key=lambda x: x[sort_by])

#         return sorted_files


# # 사용 예시
# SG_URL = "https://minseo.shotgrid.autodesk.com"
# SCRIPT_NAME = "Viper"
# API_KEY = "your_api_key_here"

# # ShotGrid API 연결
# sg_connector = ShotGridConnector(SG_URL, SCRIPT_NAME, API_KEY)

# # 로그인한 사용자 정보 가져오기
# username = "artist@studio.com"
# user_data = sg_connector.get_user_data(username)

# if "error" not in user_data:
#     file_manager = ShotGridFileManager(sg_connector)

#     # 로그인한 사용자의 Task, Shot, Asset 관련 파일 가져오기
#     sorted_files = file_manager.get_sorted_files_for_user(sort_by="created_at")

#     for file in sorted_files:
#         print(file)
# else:
#     print(user_data["error"])



########################################################################################################################

# import shotgun_api3
# import os, sys
# from shotgun_api3 import Shotgun

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))

# from shotgrid_connector import ShotGridConnector
# from user_authenticator import UserAuthenticator



# class ShotGridConnector:
#     """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

#     # ShotGrid 서버 정보 설정
#     SG_URL = "https://minseo.shotgrid.autodesk.com"
#     SCRIPT_NAME = "Viper"
#     API_KEY = "jvceqpsfqvbl1azzcns?haksI"

#     # ShotGrid API 연결
#     sg = shotgun_api3.Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

#     def get_user_tasks(user_id):
#         """현재 사용자의 Task 목록을 가져옴"""
#         tasks = ShotGridConnector.sg.find(
#             "Task",
#             [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
#             ["id", "content", "sg_status_list", "entity"]
#         )
#         return tasks

#     def get_task_status(task_id):
#         """특정 Task의 상태(PND, IP, FIN)를 가져옴"""
#         task = ShotGridConnector.sg.find_one(
#             "Task",
#             [["id", "is", task_id]],
#             ["sg_status_list"]
#         )
#         if task:
#             return task["sg_status_list"]
#         else:
#             None

#     def filter_tasks_by_status(tasks, status):
#         """특정 상태(PND, IP, FIN)에 해당하는 Task만 필터링"""
#         if task["sg_status_list"] == status : 
#             for task in tasks:
#                 return task

#     def update_task(task_id, new_status):
#         """Task 상태를 업데이트 (예: PND → IP)"""
#         ShotGridConnector.sg.update(
#             "Task",
#             task_id,
#             {"sg_status_list": new_status}
#         )

#     def sync_task_status(user_id):
#         """ShotGrid의 최신 Task 상태를 로더 UI와 동기화"""
#         tasks = ShotGridConnector.get_user_tasks(user_id)
#         updated_tasks = {task["id"]: task["sg_status_list"] for task in tasks}
        
#         return updated_tasks


# class ShotGridFileManager:
#     """ShotGrid에서 로그인한 사용자의 Task, Shot, Asset에 연결된 파일 정보를 정렬하는 클래스"""

#     def __init__(self, sg_connector):
#         self.sg_connector = sg_connector

#     def get_sorted_files_for_user(self, sort_by="created_at"):
#         """로그인한 사용자의 Task, Shot, Asset에 연결된 파일 정보를 정렬하여 반환"""
#         if not self.sg_connector.user_data:
#             return {"error": "User not authenticated"}

#         file_list = []

#         # 1. 사용자 Tasks에 연결된 파일 가져오기
#         tasks = self.sg_connector.get_user_tasks()
#         for task in tasks:
#             task_id = task["id"]
#             versions = self.sg_connector.sg.find("Version", [["sg_task", "is", {"type": "Task", "id": task_id}]], 
#                                                  ["id", "code", "created_at"])
#             for version in versions:
#                 file_list.append({
#                     "category": "Task",
#                     "task_id": task_id,
#                     "task_name": task["content"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 2. 사용자 Shots에 연결된 파일 가져오기
#         shots = self.sg_connector.get_user_shots()
#         for shot in shots:
#             shot_id = shot["id"]
#             versions = self.sg_connector.sg.find("Version", [["entity", "is", {"type": "Shot", "id": shot_id}]], 
#                                                  ["id", "code", "created_at"])
#             for version in versions:
#                 file_list.append({
#                     "category": "Shot",
#                     "shot_id": shot_id,
#                     "shot_name": shot["code"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 3. 사용자 Assets에 연결된 파일 가져오기
#         assets = self.sg_connector.get_user_assets()
#         for asset in assets:
#             asset_id = asset["id"]
#             versions = self.sg_connector.sg.find("Version", [["entity", "is", {"type": "Asset", "id": asset_id}]], 
#                                                  ["id", "code", "created_at"])
#             for version in versions:
#                 file_list.append({
#                     "category": "Asset",
#                     "asset_id": asset_id,
#                     "asset_name": asset["code"],
#                     "version_id": version["id"],
#                     "file_name": version["code"],
#                     "created_at": version["created_at"]
#                 })

#         # 4. 파일 목록을 정렬
#         sorted_files = sorted(file_list, key=lambda x: x[sort_by])

#         return sorted_files


# # 사용 예시
# sg_connector = ShotGridConnector

# # 로그인한 사용자 정보 가져오기
# username = "owlgrowl0v0@gmail.com"
# user_data = UserAuthenticator.login(username)

# if "error" not in user_data:
#     file_manager = ShotGridFileManager(sg_connector)

#     # 로그인한 사용자의 Task, Shot, Asset 관련 파일 가져오기
#     sorted_files = file_manager.get_sorted_files_for_user(sort_by="created_at")

#     for file in sorted_files:
#         print(file)
# else:
#     print(user_data["error"])




##############################################################################################################################################


import os
import sys
import shotgun_api3
from shotgun_api3 import Shotgun

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator


class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""


# 샷그리드를 연동하기 위해 url, 스크립트 이름, api 키를가져옴
# (url, 스크립트 이름, api 키)가 담긴 shotgun을 sg 로 설정한다
# 로그인한 사용자의 정보는 none으로 지정하여 정보가 담기도록

    def __init__(self):
        """ShotGrid API 연결"""
        self.SG_URL = "https://minseo.shotgrid.autodesk.com"
        self.SCRIPT_NAME = "Viper"
        self.API_KEY = "jvceqpsfqvbl1azzcns?haksI" 
        self.sg = Shotgun(self.SG_URL, self.SCRIPT_NAME, self.API_KEY)
        self.user_data = None  


# 로그인한 유저의 정보를 가져온다
# field는 아이디, 이름, 이메일 
# field, fuilter 가 일치하는 유저를 불러오는 user

    def login_user(self, username):
        """ShotGrid에서 로그인한 사용자 정보를 가져오기"""
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = self.sg.find_one("HumanUser", filters, fields)

# 일치해야 코드가 실행되도록 한다 

        if user:
            self.user_data = user
            return user
        else:
            return {"error": "User not found"}


# 로그인 후 유저가 확인되면
# 그 유저에게 부여된 task,
    def get_user_tasks(self):
        """현재 로그인한 사용자에게 할당된 Task 목록을 가져옴"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "content", "sg_status_list", "entity"]
        return self.sg.find("Task", filters, fields) or []


# 사용 예시
# sg_connector = 앞에서 한 클래스(유저 로그인을 확인하고 할당된 task(이때 task는 항
# 목, 진행상태 등의 정보의 일치로 확인한다) 를 찾는다 

sg_connector = ShotGridConnector()


username = "owlgrowl0v0@gmail.com"
user_data = sg_connector.login_user(username)

if "error" not in user_data:
    print(f"로그인 성공: {user_data}")

    # 1. 로그인한 사용자의 Task 가져오기
    user_tasks = sg_connector.get_user_tasks()
    print("\n[사용자 Task 목록]:")
    for task in user_tasks:
        print(f"Task ID: {task['id']}, Name: {task['content']}, Status: {task['sg_status_list']}")

    # 2. 로그인한 사용자의 Shot 가져오기
    user_shots = sg_connector.get_user_shots()
    print("\n[사용자 Shot 목록]:")
    for shot in user_shots:
        print(f"Shot ID: {shot['id']}, Name: {shot['code']}, Status: {shot['sg_status_list']}")

    # 3. 로그인한 사용자의 Asset 가져오기
    user_assets = sg_connector.get_user_assets()
    print("\n[사용자 Asset 목록]:")
    for asset in user_assets:
        print(f"Asset ID: {asset['id']}, Name: {asset['code']}, Status: {asset['sg_status_list']}")
else:
    print(user_data["error"])
