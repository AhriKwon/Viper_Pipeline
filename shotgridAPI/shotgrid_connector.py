import shotgun_api3

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    # ShotGrid 서버 정보 설정
    SG_URL = "https://minseo.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper"
    API_KEY = "jvceqpsfqvbl1azzcns?haksI"

    # ShotGrid API 연결
    sg = shotgun_api3.Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

    def get_user_tasks(user_id):
        """현재 사용자의 Task 목록을 가져옴"""
        tasks = ShotGridConnector.sg.find(
            "Task",
            [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
            ["id", "content", "sg_status_list", "entity"]
        )
        return tasks

    def get_task_status(task_id):
        """특정 Task의 상태(PND, IP, FIN)를 가져옴"""
        task = ShotGridConnector.sg.find_one(
            "Task",
            [["id", "is", task_id]],
            ["sg_status_list"]
        )
        if task:
            return task["sg_status_list"]
        else:
            None

    def filter_tasks_by_status(tasks, status):
        """특정 상태(PND, IP, FIN)에 해당하는 Task만 필터링"""
        if task["sg_status_list"] == status : 
            for task in tasks:
                return task

    def update_task(task_id, new_status):
        """Task 상태를 업데이트 (예: PND → IP)"""
        ShotGridConnector.sg.update(
            "Task",
            task_id,
            {"sg_status_list": new_status}
        )

    def sync_task_status(user_id):
        """ShotGrid의 최신 Task 상태를 로더 UI와 동기화"""
        tasks = ShotGridConnector.get_user_tasks(user_id)
        updated_tasks = {task["id"]: task["sg_status_list"] for task in tasks}
        
        return updated_tasks