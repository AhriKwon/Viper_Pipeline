
"""
추가해야 할 함수들



1. Task가 상태변경(PND->IP) 되면 현 상태가 맞는지 확인하는 함수

2. 날짜별 파일 정렬 함수

3. 각 상태별 파일 정렬 (wtg 파일 따로, pndng 파일 따로, ip 파일 따로, fin 파일 따로 정렬해주는) 함수

"""




#####################################################################################################################################
############### 각 상태별 파일 정렬 (wtg 파일 따로, pndng 파일 따로, ip 파일 따로, fin 파일 따로 정렬해주는) 함수 ########################
#####################################################################################################################################




import os
from collections import defaultdict
from shotgun_api3 import Shotgun

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    def __init__(self):
        """ShotGrid API 연결"""
        self.SG_URL = "https://minseo.shotgrid.autodesk.com"
        self.SCRIPT_NAME = "Viper"
        self.API_KEY = "jvceqpsfqvbl1azzcns?haksI"  # API 키 가져오기
        self.sg = Shotgun(self.SG_URL, self.SCRIPT_NAME, self.API_KEY)
        self.user_data = None  # 로그인한 사용자 정보 저장

    def login_user(self, username):
        """ShotGrid에서 로그인한 사용자 정보를 가져오기"""
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = self.sg.find_one("HumanUser", filters, fields)

        if user:
            self.user_data = user
            return user
        else:
            return {"error": "User not found"}

    def get_user_tasks(self):
        """현재 로그인한 사용자에게 할당된 Task 목록을 가져옴"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "content", "sg_status_list", "entity"]
        return self.sg.find("Task", filters, fields) or []

    def get_user_shots(self):
        """현재 로그인한 사용자가 작업 중인 Shot 목록을 가져옴"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]

        filters = [
            ["task_assignees", "in", {"type": "HumanUser", "id": user_id}],
            ["entity", "type_is", "Shot"]
        ]
        fields = ["entity", "content", "sg_status_list"]

        tasks = self.sg.find("Task", filters, fields) or []

        shots = []
        for task in tasks:
            if task["entity"]:
                shots.append({
                    "shot_id": task["entity"]["id"],
                    "shot_name": task["entity"]["name"],
                    "task_name": task["content"],
                    "status": task["sg_status_list"]
                })

        return shots

    def get_user_assets(self):
        """현재 로그인한 사용자가 작업 중인 Asset 목록을 가져옴"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]

        filters = [
            ["task_assignees", "in", {"type": "HumanUser", "id": user_id}],
            ["entity", "type_is", "Asset"]
        ]
        fields = ["entity", "content", "sg_status_list"]

        tasks = self.sg.find("Task", filters, fields) or []

        assets = []
        for task in tasks:
            if task["entity"] and task["entity"]["type"] == "Asset":
                assets.append({
                    "asset_id": task["entity"]["id"],
                    "asset_name": task["entity"]["name"],
                    "task_name": task["content"],
                    "status": task["sg_status_list"]
                })

        return assets

    def categorize_and_sort_tasks(self):
        """Task 목록을 wtg, pndng, ip, fin 상태로 분류하고 정렬"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        categorized_tasks = defaultdict(list)
        tasks = self.get_user_tasks()

        for task in tasks:
            status = task.get("sg_status_list", "unknown").lower()
            if status in ["wtg", "pndng", "ip", "fin"]:
                categorized_tasks[status].append(task)

        for status, items in categorized_tasks.items():
            categorized_tasks[status] = sorted(items, key=lambda x: x.get("id", 0))

        return categorized_tasks

    def categorize_and_sort_shots(self):
        """Shot 목록을 wtg, pndng, ip, fin 상태로 분류하고 정렬"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        categorized_shots = defaultdict(list)
        shots = self.get_user_shots()

        for shot in shots:
            status = shot.get("status", "unknown").lower()
            if status in ["wtg", "pndng", "ip", "fin"]:
                categorized_shots[status].append(shot)

        for status, items in categorized_shots.items():
            categorized_shots[status] = sorted(items, key=lambda x: x.get("shot_id", 0))

        return categorized_shots

    def categorize_and_sort_assets(self):
        """Asset 목록을 wtg, pndng, ip, fin 상태로 분류하고 정렬"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        categorized_assets = defaultdict(list)
        assets = self.get_user_assets()

        for asset in assets:
            status = asset.get("status", "unknown").lower()
            if status in ["wtg", "pndng", "ip", "fin"]:
                categorized_assets[status].append(asset)

        for status, items in categorized_assets.items():
            categorized_assets[status] = sorted(items, key=lambda x: x.get("asset_id", 0))

        return categorized_assets


# 사용 예시
sg_connector = ShotGridConnector()

# 로그인한 사용자 정보 가져오기
username = "owlgrowl0v0@gmail.com"
user_data = sg_connector.login_user(username)

if "error" not in user_data:
    print(f"로그인 성공: {user_data}")

    # 1️ Task 목록을 상태별로 분류 및 정렬
    categorized_tasks = sg_connector.categorize_and_sort_tasks()
    print("\n [Task 목록 - 상태별 정리]")
    for status, items in categorized_tasks.items():
        print(f"\n [{status.upper()} 상태]:")
        for item in items:
            print(item)

    # 2️ Shot 목록을 상태별로 분류 및 정렬
    categorized_shots = sg_connector.categorize_and_sort_shots()
    print("\n [Shot 목록 - 상태별 정리]")
    for status, items in categorized_shots.items():
        print(f"\n [{status.upper()} 상태]:")
        for item in items:
            print(item)

    # 3️ Asset 목록을 상태별로 분류 및 정렬
    categorized_assets = sg_connector.categorize_and_sort_assets()
    print("\n [Asset 목록 - 상태별 정리]")
    for status, items in categorized_assets.items():
        print(f"\n [{status.upper()} 상태]:")
        for item in items:
            print(item)

else:
    print(user_data["error"])



###############################################################################################################################################


"""
추가해야 할 함수들



1. Task가 상태변경(PND->IP) 되면 현 상태가 맞는지 확인하는 함수

2. 날짜별 파일 정렬 함수

3. 각 상태별 파일 정렬 (wtg 파일 따로, pndng 파일 따로, ip 파일 따로, fin 파일 따로 정렬해주는) 함수

"""


import os
from collections import defaultdict
from shotgun_api3 import Shotgun

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    def __init__(self):
        """ShotGrid API 연결"""
        self.SG_URL = "https://minseo.shotgrid.autodesk.com"
        self.SCRIPT_NAME = "Viper"
        self.API_KEY = "jvceqpsfqvbl1azzcns?haksI"  # API 키 가져오기
        self.sg = Shotgun(self.SG_URL, self.SCRIPT_NAME, self.API_KEY)
        self.user_data = None  # 로그인한 사용자 정보 저장

    def login_user(self, username):
        """ShotGrid에서 로그인한 사용자 정보를 가져오기"""
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = self.sg.find_one("HumanUser", filters, fields)

        if user:
            self.user_data = user
            return user
        else:
            return {"error": "User not found"}

    def get_user_tasks(self):
        """현재 로그인한 사용자에게 할당된 Task 목록을 가져옴 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "content", "sg_status_list", "entity", "start_date", "due_date"]
        return self.sg.find("Task", filters, fields) or []

    def get_user_shots(self):
        """현재 로그인한 사용자가 작업 중인 Shot 목록을 가져옴 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        
        filters = [
            ["task_assignees", "in", {"type": "HumanUser", "id": user_id}],
            ["entity", "type_is", "Shot"]
        ]
        fields = ["entity", "content", "sg_status_list", "start_date", "due_date"]

        tasks = self.sg.find("Task", filters, fields) or []

        shots = []
        for task in tasks:
            if task["entity"]:
                shots.append({
                    "shot_id": task["entity"]["id"],
                    "shot_name": task["entity"]["name"],
                    "task_name": task["content"],
                    "status": task["sg_status_list"],
                    "start_date": task.get("start_date", "N/A"),
                    "due_date": task.get("due_date", "N/A")
                })

        return shots

    def get_user_assets(self):
        """현재 로그인한 사용자가 작업 중인 Asset 목록을 가져옴 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        
        filters = [
            ["task_assignees", "in", {"type": "HumanUser", "id": user_id}],
            ["entity", "type_is", "Asset"]
        ]
        fields = ["entity", "content", "sg_status_list", "start_date", "due_date"]

        tasks = self.sg.find("Task", filters, fields) or []

        assets = []
        for task in tasks:
            if task["entity"] and task["entity"]["type"] == "Asset":
                assets.append({
                    "asset_id": task["entity"]["id"],
                    "asset_name": task["entity"]["name"],
                    "task_name": task["content"],
                    "status": task["sg_status_list"],
                    "start_date": task.get("start_date", "N/A"),
                    "due_date": task.get("due_date", "N/A")
                })

        return assets

    def categorize_and_sort_tasks(self):
        """Task 목록을 wtg, pndng, ip, fin 상태로 분류하고 정렬 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        categorized_tasks = defaultdict(list)
        tasks = self.get_user_tasks()

        for task in tasks:
            status = task.get("sg_status_list", "unknown").lower()
            if status in ["wtg", "pndng", "ip", "fin"]:
                categorized_tasks[status].append(task)

        for status, items in categorized_tasks.items():
            categorized_tasks[status] = sorted(items, key=lambda x: x.get("id", 0))

        return categorized_tasks

    def categorize_and_sort_shots(self):
        """Shot 목록을 wtg, pndng, ip, fin 상태로 분류하고 정렬 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        categorized_shots = defaultdict(list)
        shots = self.get_user_shots()

        for shot in shots:
            status = shot.get("status", "unknown").lower()
            if status in ["wtg", "pndng", "ip", "fin"]:
                categorized_shots[status].append(shot)

        for status, items in categorized_shots.items():
            categorized_shots[status] = sorted(items, key=lambda x: x.get("shot_id", 0))

        return categorized_shots

    def categorize_and_sort_assets(self):
        """Asset 목록을 wtg, pndng, ip, fin 상태로 분류하고 정렬 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        categorized_assets = defaultdict(list)
        assets = self.get_user_assets()

        for asset in assets:
            status = asset.get("status", "unknown").lower()
            if status in ["wtg", "pndng", "ip", "fin"]:
                categorized_assets[status].append(asset)

        for status, items in categorized_assets.items():
            categorized_assets[status] = sorted(items, key=lambda x: x.get("asset_id", 0))

        return categorized_assets


# 사용 예시
sg_connector = ShotGridConnector()

# 로그인한 사용자 정보 가져오기
username = "owlgrowl0v0@gmail.com"
user_data = sg_connector.login_user(username)

if "error" not in user_data:
    print(f"로그인 성공: {user_data}")

    # 1️ Task 목록을 상태별로 분류 및 정렬
    categorized_tasks = sg_connector.categorize_and_sort_tasks()
    print("\n [Task 목록 - 상태별 정리]")
    for status, items in categorized_tasks.items():
        print(f"\n [{status.upper()} 상태]:")
        for item in items:
            print(item)
            # (f"Task ID: {item['id']}, Name: {item['content']}, Start: {item.get('start_date', 'N/A')}, Due: {item.get('due_date', 'N/A')}")

    # 2️ Shot 목록을 상태별로 분류 및 정렬
    categorized_shots = sg_connector.categorize_and_sort_shots()
    print("\n [Shot 목록 - 상태별 정리]")
    for status, items in categorized_shots.items():
        print(f"\n [{status.upper()} 상태]:")
        for item in items:
            print(item)
            # (f"Shot ID: {item['shot_id']}, Name: {item['shot_name']}, Task: {item['task_name']}, Start: {item['start_date']}, Due: {item['due_date']}")

    # 3️ Asset 목록을 상태별로 분류 및 정렬
    categorized_assets = sg_connector.categorize_and_sort_assets()
    print("\n [Asset 목록 - 상태별 정리]")
    for status, items in categorized_assets.items():
        print(f"\n [{status.upper()} 상태]:")
        for item in items:
            print(item)
            # (f"Asset ID: {item['asset_id']}, Name: {item['asset_name']}, Task: {item['task_name']}, Start: {item['start_date']}, Due: {item['due_date']}")

else:
    print(user_data["error"])




#####################################################################################################################################################################



import os
from collections import defaultdict
from shotgun_api3 import Shotgun

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    def __init__(self):
        """ShotGrid API 연결"""
        self.SG_URL = "https://minseo.shotgrid.autodesk.com"
        self.SCRIPT_NAME = "Viper"
        self.API_KEY = "jvceqpsfqvbl1azzcns?haksI"  # API 키 가져오기
        self.sg = Shotgun(self.SG_URL, self.SCRIPT_NAME, self.API_KEY)
        self.user_data = None  # 로그인한 사용자 정보 저장

    def login_user(self, username):
        """ShotGrid에서 로그인한 사용자 정보를 가져오기"""
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = self.sg.find_one("HumanUser", filters, fields)

        if user:
            self.user_data = user
            return user
        else:
            return {"error": "User not found"}

    def get_user_tasks(self):
        """현재 로그인한 사용자에게 할당된 Task 목록을 가져옴 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "content", "sg_status_list", "entity", "start_date", "due_date"]
        return self.sg.find("Task", filters, fields) or []

    def get_user_shots(self):
        """현재 로그인한 사용자가 작업 중인 Shot 목록을 가져옴 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        
        filters = [
            ["task_assignees", "in", {"type": "HumanUser", "id": user_id}],
            ["entity", "type_is", "Shot"]
        ]
        fields = ["entity", "content", "sg_status_list", "start_date", "due_date"]

        tasks = self.sg.find("Task", filters, fields) or []

        shots = []
        for task in tasks:
            if task["entity"]:
                shots.append({
                    "shot_id": task["entity"]["id"],
                    "shot_name": task["entity"]["name"],
                    "task_name": task["content"],
                    "status": task["sg_status_list"],
                    "start_date": task.get("start_date", "N/A"),
                    "due_date": task.get("due_date", "N/A")
                })

        return shots

    def get_user_assets(self):
        """현재 로그인한 사용자가 작업 중인 Asset 목록을 가져옴 (Start Date, Due Date 포함)"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        
        filters = [
            ["task_assignees", "in", {"type": "HumanUser", "id": user_id}],
            ["entity", "type_is", "Asset"]
        ]
        fields = ["entity", "content", "sg_status_list", "start_date", "due_date"]

        tasks = self.sg.find("Task", filters, fields) or []

        assets = []
        for task in tasks:
            if task["entity"] and task["entity"]["type"] == "Asset":
                assets.append({
                    "asset_id": task["entity"]["id"],
                    "asset_name": task["entity"]["name"],
                    "task_name": task["content"],
                    "status": task["sg_status_list"],
                    "start_date": task.get("start_date", "N/A"),
                    "due_date": task.get("due_date", "N/A")
                })

        return assets

    def categorize_and_sort_by_dates(self, items, key_id):
        """Start Date, Due Date 기준으로 정렬"""
        categorized_by_start = sorted(items, key=lambda x: x.get("start_date") or "9999-12-31")
        categorized_by_due = sorted(items, key=lambda x: x.get("due_date") or "9999-12-31")

        return {
            "by_start_date": categorized_by_start,
            "by_due_date": categorized_by_due
        }

    def categorize_and_sort_tasks_by_dates(self):
        """Task 목록을 Start Date, Due Date 기준으로 정렬"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        tasks = self.get_user_tasks()
        return self.categorize_and_sort_by_dates(tasks, "id")

    def categorize_and_sort_shots_by_dates(self):
        """Shot 목록을 Start Date, Due Date 기준으로 정렬"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        shots = self.get_user_shots()
        return self.categorize_and_sort_by_dates(shots, "shot_id")

    def categorize_and_sort_assets_by_dates(self):
        """Asset 목록을 Start Date, Due Date 기준으로 정렬"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        assets = self.get_user_assets()
        return self.categorize_and_sort_by_dates(assets, "asset_id")


# 사용 예시
sg_connector = ShotGridConnector()

# 로그인한 사용자 정보 가져오기
username = "owlgrowl0v0@gmail.com"
user_data = sg_connector.login_user(username)

if "error" not in user_data:
    print(f"로그인 성공: {user_data}")

    # 1️ Task 목록을 Start Date, Due Date 기준으로 정렬
    sorted_tasks_by_dates = sg_connector.categorize_and_sort_tasks_by_dates()
    print("\n [Task 목록 - Start Date 기준 정렬]")
    for item in sorted_tasks_by_dates["by_start_date"]:
        print(item)

    print("\n [Task 목록 - Due Date 기준 정렬]")
    for item in sorted_tasks_by_dates["by_due_date"]:
        print(item)

    # 2️ Shot 목록을 Start Date, Due Date 기준으로 정렬
    sorted_shots_by_dates = sg_connector.categorize_and_sort_shots_by_dates()
    print("\n [Shot 목록 - Start Date 기준 정렬]")
    for item in sorted_shots_by_dates["by_start_date"]:
        print(item)

    print("\n [Shot 목록 - Due Date 기준 정렬]")
    for item in sorted_shots_by_dates["by_due_date"]:
        print(item)

    # 3️ Asset 목록을 Start Date, Due Date 기준으로 정렬
    sorted_assets_by_dates = sg_connector.categorize_and_sort_assets_by_dates()
    print("\n [Asset 목록 - Start Date 기준 정렬]")
    for item in sorted_assets_by_dates["by_start_date"]:
        print(item)

    print("\n [Asset 목록 - Due Date 기준 정렬]")
    for item in sorted_assets_by_dates["by_due_date"]:
        print(item)

else:
    print(user_data["error"])
