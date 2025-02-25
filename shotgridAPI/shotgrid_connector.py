import shotgun_api3

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    def init(self, sg_url, script_name, api_key):
        # ShotGrid 서버 정보 설정
        self.sg_url = sg_url
        self.script_name = script_name
        self.api_key = api_key
        # ShotGrid API 연결
        self.sg = shotgun_api3.Shotgun(self.sg_url, self.script_name, self.api_key)

    def get_user_tasks(self, user_id):
        """현재 사용자의 Task 목록을 가져옴"""
        tasks = ShotGridConnector.sg.find(
            "Task",
            [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
            ["id", "content", "sg_status_list", "entity"]
        )
        return tasks
    
    def get_publishes_for_task(self, task_id):
        """특정 Task에 연결된 PublishedFile을 조회"""
        # PublishedFile 엔티티에서 Task ID를 기준으로 검색
        filters = [["task", "is", {"type": "Task", "id": task_id}]]
        fields = ["id", "code", "path", "description", "image", "created_at"]
        order = [{"field_name": "created_at", "direction": "desc"}]  # 최신순 정렬

        publishes = ShotGridConnector.sg.find("PublishedFile", filters, fields, order)
        publish_list = []
        
        # 퍼블리시 된 파일을 리스트로 리턴
        if publishes:
            print(f"Task {task_id}에 연결된 퍼블리시 파일 목록:")
            for publish in publishes:
                publish_dict = {
                    'id' : publish['id'],
                    'file_name' : publish['code'],
                    'path' : publish['path']['url'],
                    'description' : publish['description'],
                    'thumbnail' : publish['image'],
                    'created_at' : publish['created_at']
                }
                publish_list.append(publish_dict)
            return publish_list
        
        # 테스크 안에 퍼블리시 된 파일이 없는 경우
        else:
            print(f"⚠ Task {task_id}에 연결된 퍼블리시 파일이 없습니다.")
            return []

    def get_task_status(self, task_id):
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

    def filter_tasks_by_status(self, tasks, status):
        """특정 상태(PND, IP, FIN)에 해당하는 Task만 필터링"""
        if task["sg_status_list"] == status : 
            for task in tasks:
                return task

    def update_task(self, task_id, new_status):
        """Task 상태를 업데이트 (예: PND → IP)"""
        ShotGridConnector.sg.update(
            "Task",
            task_id,
            {"sg_status_list": new_status}
        )

    def sync_task_status(self, user_id):
        """ShotGrid의 최신 Task 상태를 로더 UI와 동기화"""
        tasks = ShotGridConnector.get_user_tasks(user_id)
        updated_tasks = {task["id"]: task["sg_status_list"] for task in tasks}
        
        return updated_tasks