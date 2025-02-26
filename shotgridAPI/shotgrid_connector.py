import os
import shotgun_api3

class ShotGridConnector:
    """
    ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스
    """
    # ShotGrid 서버 정보 설정
    SG_URL = "https://minseo.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper"
    API_KEY = "jvceqpsfqvbl1azzcns?haksI"

    # ShotGrid API 연결
    sg = shotgun_api3.Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

    @staticmethod
    def get_user_tasks(user_id):
        """
        현재 사용자의 Task 목록을 가져옴
        """
        tasks = ShotGridConnector.sg.find(
            "Task",
            [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
            ["id", "content", "sg_status_list", "entity"]
        )
        return tasks
    
    @staticmethod
    def get_publishes_for_task(task_id):
        """
        특정 Task에 연결된 PublishedFile을 조회
        """
        # PublishedFile 엔티티에서 Task ID를 기준으로 검색
        filters = [["task", "is", {"type": "Task", "id": task_id}]]
        fields = ["id", "code", "path", "description", "image", "created_at"]
        order = [{"field_name": "created_at", "direction": "desc"}]  # 최신순 정렬

        publishes = ShotGridConnector.sg.find("PublishedFile", filters, fields, order)
        publish_files = []
        
        # 퍼블리시 된 파일을 리스트로 리턴
        if publishes:
            print(f"Task {task_id}에 연결된 퍼블리시 파일 목록:")
            for publish in publishes:
                publish_dict = {
                    'id' : publish['id'],
                    'file_name' : publish['code'],
                    'path' : publish['path']['local_path'],
                    'description' : publish['description'],
                    'thumbnail' : publish['image'],
                    'created_at' : publish['created_at']
                }
                publish_files.append(publish_dict)
            return publish_files
        
        # 테스크 안에 퍼블리시 된 파일이 없는 경우
        else:
            print(f"⚠ Task {task_id}에 연결된 퍼블리시 파일이 없습니다.")
            return []

    @staticmethod
    def get_task_status(task_id):
        """
        특정 Task의 상태(PND, IP, FIN)를 가져옴
        """
        task = ShotGridConnector.sg.find_one(
            "Task",
            [["id", "is", task_id]],
            ["sg_status_list"]
        )
        if task:
            return task["sg_status_list"]
        else:
            None

    @staticmethod
    def filter_tasks_by_status(tasks, status):
        """
        특정 상태(PND, IP, FIN)에 해당하는 Task만 필터링
        """
        if task["sg_status_list"] == status : 
            for task in tasks:
                return task

    @staticmethod
    def update_task_status(task_id, new_status):
        """
        Task 상태를 업데이트 (예: PND → IP)
        """
        ShotGridConnector.sg.update(
            "Task", task_id, {"sg_status_list": new_status}
        )

    @staticmethod
    def sync_task_status(user_id):
        """
        ShotGrid의 최신 Task 상태를 로더 UI와 동기화
        (특정 사용자의 테스크 상태만 불러옴)
        """
        tasks = ShotGridConnector.get_user_tasks(user_id)
        updated_tasks = {task["id"]: task["sg_status_list"] for task in tasks}
        
        return updated_tasks

    @staticmethod
    def create_pub_file(task_id, file_path, thumbnail_path, description):
        """
        새로운 퍼블리시 파일을 Task에 등록
        """
        file_name = os.path.basename(file_path)
        data = {
            "code": file_name,
            "image": thumbnail_path,
            "description": description,
            "task": {"type": "Task", "id": task_id},
            "path": {"local_path": file_path}
        }
        return ShotGridConnector.sg.create("PublishedFile", data)

    @staticmethod
    def update_entity(entity_type, entity_id, description, thumbnail_path):
        """
        특정 엔티티의 설명 또는 썸네일 업데이트
        """
        if description:
            ShotGridConnector.sg.update(
                entity_type, entity_id, {"description": description}
                )
        if thumbnail_path:
            ShotGridConnector.sg.upload_thumbnail(
                entity_type, entity_id, thumbnail_path
                )

    @staticmethod
    def delete_published_file(publish_id):
        """
        특정 퍼블리시 파일 삭제
        """
        ShotGridConnector.sg.delete("PublishedFile", publish_id)

    @staticmethod
    def update_task_thumbnail(task_id):
        """
        특정 Task의 썸네일을 최신 퍼블리시된 파일의 썸네일로 업데이트
        """
        publish_files = ShotGridConnector.get_publishes_for_task(task_id)

        if not publish_files:
            print(f"⚠ Task {task_id}에 연결된 퍼블리시 파일이 없습니다.")
            return False
        
        latest_publish = publish_files[0]
        latest_thumbnail = latest_publish.get("thumbnail")

        if not latest_thumbnail:
            print(f"⚠ 최신 퍼블리시 파일(ID {latest_publish['id']})에 썸네일이 없습니다.")
            return False
        
        ShotGridConnector.sg.update("Task", task_id, {"image": latest_thumbnail})
        print(f"Task {task_id}의 썸네일이 최신 퍼블리시 썸네일로 업데이트되었습니다!")
        return True
