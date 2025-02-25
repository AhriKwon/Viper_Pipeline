
from shotgun_api3 import Shotgun
from shotgrid_connector import ShotGridConnector

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오는 클래스"""

    # def __init__(self, sg_url, script_name, api_key):
    #     """
    #     :param sg_url: ShotGrid 서버 URL
    #     :param script_name: ShotGrid API 스크립트 이름
    #     :param api_key: ShotGrid API 키
    #     """
    #     self.sg = Shotgun(sg_url, script_name, api_key)

    # def get_user_tasks(self, user_id):
    #     """현재 사용자의 Task 목록을 가져옴"""
    #     filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
    #     fields = ["id", "content", "entity"]
    #     tasks = self.sg.find("Task", filters, fields)
    #     return tasks

    # def get_task_versions(self, task_id):
    #     """특정 Task에 연결된 Version 목록을 가져옴"""
    #     filters = [["sg_task", "is", {"type": "Task", "id": task_id}]]
    #     fields = ["id", "code", "created_at"]
    #     versions = self.sg.find("Version", filters, fields)
    #     return versions

    # def update_task_status(self, task_id, new_status):
    #     """Task의 상태(PND→IP 등)를 변경"""
    #     data = {"sg_status_list": new_status}
    #     self.sg.update("Task", task_id, data)

class ShotGridFileManager:
    """ShotGrid에서 Task에 연결된 파일 정보를 정렬하는 클래스"""

    def __init__(self, sg_connector):
        """
        sg_connector: ShotGridConnector 인스턴스
        """
        self.sg_connector = sg_connector

    def get_sorted_files_for_user(self, user_id, sort_by="created_at"):
        """
        주어진 사용자의 Task와 연결된 파일 정보를 정렬하여 반환.

        user_id: ShotGrid에서 검색할 사용자 ID
        sort_by: 정렬 기준 (예: "created_at", "name")
        return: 정렬된 파일 목록 (리스트)
        """
        # 1️ 현재 사용자의 Task 목록 가져오기
        tasks = self.sg_connector.get_user_tasks(user_id)
        if not tasks:
            return []

        file_list = []

        # 2️ 각 Task에 연결된 파일(Version) 정보 가져오기
        for task in tasks:
            task_id = task["id"]
            versions = self.sg_connector.get_task_versions(task_id)  # Task의 Version 정보 가져오기

            for version in versions:
                file_list.append({
                    "task_id": task_id,
                    "task_name": task["content"],
                    "version_id": version["id"],
                    "file_name": version["code"],
                    "created_at": version["created_at"]
                })

        # 3️ 파일 목록을 정렬 (기본: 생성 날짜 기준)
        sorted_files = sorted(file_list, key=lambda x: x[sort_by])

        return sorted_files


# 사용 예시
SG_URL = "https://minseo.shotgrid.autodesk.com"
SCRIPT_NAME = "Viper"
API_KEY = "jvceqpsfqvbl1azzcns?haksI"

sg_connector = ShotGridConnector(SG_URL, SCRIPT_NAME, API_KEY)
file_manager = ShotGridFileManager(sg_connector)

user_id = 1234  # 예제 사용자 ID
sorted_files = file_manager.get_sorted_files_for_user(user_id, sort_by="created_at")

for file in sorted_files:
    print(file)




############################################################################################################
######################################### 오류 시 수정코드 ##################################################
############################################################################################################

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오는 클래스"""

    def __init__(self, sg_url, script_name, api_key):
        self.sg = Shotgun(sg_url, script_name, api_key)

    def get_user_tasks(self, user_id):
        filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "content", "entity", "task_assignees"]
        return self.sg.find("Task", filters, fields) or []

    def get_task_versions(self, task_id):
        filters = [["sg_task", "is", {"type": "Task", "id": task_id}]]
        fields = ["id", "code", "created_at"]
        return self.sg.find("Version", filters, fields) or []


class ShotGridFileManager:
    """ShotGrid에서 Task에 연결된 파일 정보를 정렬하는 클래스"""

    def __init__(self, sg_connector):
        self.sg_connector = sg_connector

    def get_sorted_files_for_user(self, user_id, sort_by="created_at"):
        tasks = self.sg_connector.get_user_tasks(user_id)
        if not tasks:
            return []

        file_list = []
        for task in tasks:
            task_id = task.get("id")
            versions = self.sg_connector.get_task_versions(task_id)

            for version in versions:
                file_list.append({
                    "task_id": task_id,
                    "task_name": task.get("content", "Unnamed Task"),
                    "version_id": version.get("id"),
                    "file_name": version.get("code", "Unknown"),
                    "created_at": version.get("created_at", "")
                })

        sorted_files = sorted(file_list, key=lambda x: x[sort_by] or "")
        return sorted_files
