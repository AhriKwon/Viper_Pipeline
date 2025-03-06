



import json
import datetime
from collections import defaultdict
from shotgun_api3 import Shotgun


class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    SG_URL = "https://hi.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper_key"
    API_KEY = "qmnpuxldvlr(exx6wnrtziwWy"
    sg = Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

    @staticmethod
    def get_supervisor_id(json_path):
        """JSON 파일에서 supervisor 부서의 사용자 ID 목록을 가져옴"""
        with open(json_path, "r") as file:
            data = json.load(file)

        supervisors = [user["id"] for user in data["assignee"] if user["dept"] == "supervisor"]
        return supervisors

    @staticmethod
    def get_all_tasks_sorted(json_path):
        """모든 사용자의 Task 목록을 due_date 기준으로 정렬하여 가져오기"""
        supervisor_id = ShotGridConnector.get_supervisor_id(json_path)

        if not supervisor_id:
            return {"error": "No supervisors found in the project metadata."}

        # supervisor가 아닌 모든 사용자의 Task 조회 (supervisor들은 제외)
        filters = [["task_assignees", "not_in", [{"type": "HumanUser", "id": user_id} for user_id in supervisor_id]]]
        fields = ["id", "content", "sg_status_list", "entity", "task_assignees", "due_date"]

        tasks = ShotGridConnector.sg.find("Task", filters, fields) or []

        # 현재 날짜 기준으로 due_date가 가까운 순으로 정렬
        def parse_date(task):
            due_date = task.get("due_date")
            if due_date is None:
                due_date = "9999-12-31"  # 기본값 설정 (미설정된 경우 가장 마지막으로 정렬됨)
            return datetime.datetime.strptime(due_date, "%Y-%m-%d")

        sorted_tasks = sorted(tasks, key=parse_date)

        return sorted_tasks


# **사용법**
json_path = "/nas/api_project/project_metadata.json"  # 업로드한 JSON 파일 경로
sorted_tasks = ShotGridConnector.get_all_tasks_sorted(json_path)

print("\n[모든 사용자의 Task 목록 (Due Date 순 정렬)]")
for task in sorted_tasks:
    print(f"Task ID: {task['id']}, Task Name: {task['content']}, Due Date: {task.get('due_date', 'N/A')}")
