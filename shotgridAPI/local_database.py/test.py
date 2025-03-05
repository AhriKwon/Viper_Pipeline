import json
import os
import shotgun_api3
import glob

# ShotGrid API 설정
SHOTGRID_URL = "https://hi.shotgrid.autodesk.com"
SCRIPT_NAME = "Viper_key"
API_KEY = "qmnpuxldvlr(exx6wnrtziwWy"

# JSON 데이터 저장 경로
DATA_FILE = "shotgrid_project_data.json"


class ShotGridAPI:
    """
    ShotGrid API와 직접 통신하는 클래스
    """

    def __init__(self):
        """
        ShotGrid API 연결
        """
        self.sg = shotgun_api3.Shotgun(SHOTGRID_URL, SCRIPT_NAME, API_KEY)


    def get_project_info(self, project_id):
        """
        프로젝트 정보 조회
        """
        return self.sg.find_one("Project", [["id", "is", project_id]], ["id", "name"])

    def get_sequences(self, project_id):
        """
        프로젝트의 시퀀스 목록 조회
        """
        sequences = self.sg.find("Sequence", [["project", "is", {"type": "Project", "id": project_id}]], ["id", "code"])
        
        return sequences

    def get_shots(self, sequence_id):
        """
        시퀀스 내의 샷 목록 조회
        """
        shots = self.sg.find("Shot", [["sg_sequence", "is", {"type": "Sequence", "id": sequence_id}]], ["id", "code"])
        
        return shots

    def get_assets(self, project_id):
        """
        프로젝트의 에셋 목록 조회
        """
        assets = self.sg.find("Asset", [["project", "is", {"type": "Project", "id": project_id}]], ["id", "code"])
        
        return assets

    def get_tasks(self, entity_type, entity_id):
        """
        특정 Entity(Shot, Asset 등)의 Task 목록 조회
        """
        tasks = self.sg.find("Task", [["entity", "is", {"type": entity_type, "id": entity_id}]],
                            ["id", "content", "sg_status_list", "task_assignees"])
        
        return tasks


    def update_task_status(self, task_id, new_status):
        """
        Task 상태 업데이트
        """
        return self.sg.update("Task", task_id, {"sg_status_list": new_status})

    def upload_thumbnail(self, entity_type, entity_id, thumbnail_path):
        """
        엔티티 썸네일 업로드
        """
        return self.sg.upload_thumbnail(entity_type, entity_id, thumbnail_path)

    def update_entity_description(self, entity_type, entity_id, new_description):
        """
        엔티티 설명 업데이트
        """
        return self.sg.update(entity_type, entity_id, {"description": new_description})

    def publish_file(self, prj_id, task_id, file_path, image_path, file_type, description="Auto Publish"):
        """
        ShotGrid 퍼블리시 파일 등록
        """
        publish_data = {
            "project": {"type": "Project", "id": prj_id},   # 프로젝트 ID
            "task": {"type": "Task", "id": task_id},        # 테스크 ID
            "code": os.path.basename(file_path),            # 파일명
            "path": {"local_path": file_path},              # 로컬 파일 경로
            "description": description,                     # 설명
            "thumbnail" : image_path,                       # 썸네일 파일 경로
            "published_file_type": {"type": "PublishedFileType", "name": file_type},  # 파일 타입
        }
        return self.sg.create("PublishedFile", publish_data)


class ProjectDataManager:
    """
    ShotGrid 데이터를 JSON 데이터베이스로 변환하여 저장하는 클래스
    """

    def __init__(self, project_id):
        self.project_id = project_id
        self.sg_api = ShotGridAPI()
        self.db_manager = LocalDatabaseManager()

    def sync_project_data(self):
        """
        ShotGrid에서 프로젝트 데이터를 가져와 JSON 파일에 저장
        """
        project_info = self.sg_api.get_project_info(self.project_id)
        sequences = self.sg_api.get_sequences(self.project_id)
        assets = self.sg_api.get_assets(self.project_id)

        project_data = {"id": project_info["id"], "name": project_info["name"], "sequences": [], "assets": []}

        for seq in sequences:
            shots = self.sg_api.get_shots(seq["id"])
            sequence_data = {"id": seq["id"], "name": seq["code"], "shots": []}
            for shot in shots:
                tasks = self.sg_api.get_tasks("Shot", shot["id"])
                sequence_data["shots"].append({"id": shot["id"], "name": shot["code"], "tasks": tasks})
            project_data["sequences"].append(sequence_data)

        for asset in assets:
            tasks = self.sg_api.get_tasks("Asset", asset["id"])
            asset_data = {"id": asset["id"], "name": asset["code"], "tasks": tasks}
            project_data["assets"].append(asset_data)

        self.db_manager.update_project_data(project_data)
        print("프로젝트 데이터가 로컬 JSON 파일로 저장.")


class UserTaskManager:
    """
    유저의 Task 및 로컬 Work 파일을 관리
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_tasks_for_user(self, user_id):
        """
        특정 유저의 Task 조회
        """
        return self.db_manager.get_local_work_files()

    def update_task_status(self, task_id, new_status):
        """
        Task 상태 업데이트
        """
        return self.db_manager.update_task_status(task_id, new_status)
