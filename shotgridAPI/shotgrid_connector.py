import shotgun_api3
import os
import glob
from datetime import datetime

class ShotGridAPI:
    """
    샷그리드 API 연결 및 프로젝트 데이터 조회, 업데이트
    """

    SG_URL = "https://hi.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper_key"
    API_KEY = "qmnpuxldvlr(exx6wnrtziwWy"

    sg = shotgun_api3.Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

    @staticmethod
    def get_user_projects(user_id):
        """
        사용자가 참여 중인 모든 프로젝트 조회
        """
        filters = [["users", "is", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "name"]
        return ShotGridAPI.sg.find("Project", filters, fields)

    @staticmethod
    def get_project_details(project_id):
        """
        프로젝트 내부의 에셋, 시퀀스, 테스크 정보를 조회
        """
        project_data = {}

        # 프로젝트 정보 조회
        project = ShotGridAPI.sg.find_one(
            "Project",
            [["id", "is", project_id]],
            ["id", "name"]
        )
        project_data["project_name"] = project["name"]
        project_data["project_id"] = project["id"]

        # 프로젝트에 속한 유저 조회
        project_data["users"] = ShotGridAPI.sg.find(
            "HumanUser",
            [["projects", "is", {"type": "Project", "id": project_id}]],
            ["id", "name", "department", "roles"]
        )

        # 프로젝트 내 에셋 조회
        project_data["assets"] = ShotGridAPI.get_assets(project_id)

        # 프로젝트 내 시퀀스 조회
        project_data["sequences"] = ShotGridAPI.get_sequences(project_id)

        return project_data

    @staticmethod
    def get_assets(project_id):
        """
        프로젝트 내 모든 에셋 조회
        """
        assets = ShotGridAPI.sg.find(
            "Asset",
            [["project", "is", {"type": "Project", "id": project_id}]],
            ["id", "code", "sg_asset_type", "description"]
        )

        for asset in assets:
            asset["tasks"] = ShotGridAPI.get_tasks("Asset", asset["id"])

        return assets
    
    @staticmethod
    def get_sequences(project_id):
        """
        프로젝트 내 모든 시퀀스 조회
        """
        sequences = ShotGridAPI.sg.find(
            "Sequence",
            [["project", "is", {"type": "Project", "id": project_id}]],
            ["id", "code", "description"]
        )

        for sequence in sequences:
            sequence["shots"] = ShotGridAPI.get_shots(sequence["id"])

        return sequences

    @staticmethod
    def get_shots(sequence_id):
        """
        프로젝트 내 모든 샷 조회
        """
        shots = ShotGridAPI.sg.find(
            "Shot",
            [["sg_sequence", "is", {"type": "Sequence", "id": sequence_id}]],
            ["id", "code", "description"]
        )

        for shot in shots:
            shot["tasks"] = ShotGridAPI.get_tasks("Shot", shot["id"])

        return shots

    @staticmethod
    def get_tasks(entity_type, entity_id):
        """
        특정 에셋 또는 샷에 연결된 모든 테스크 조회
        """
        tasks = ShotGridAPI.sg.find(
            "Task",
            [["entity", "is", {"type": entity_type, "id": entity_id}]],
            ["id", "content", "task_assignees", "sg_status_list", "start_date", "due_date"]
        )

        for task in tasks:
            task["publishes"] = ShotGridAPI.get_publishes(task["id"])
            task["works"] = ShotGridAPI.get_works(task)
        
        return tasks
    
    @staticmethod
    def get_works(task):
        """
        특정 Task의 로컬 Work 파일 검색
        """
        name, task_name = task['content'].rsplit('_', 1)

        search_patterns = [
            f"/nas/show/*/assets/*/{name}/{task_name}/work/*/*/*.*",
            f"/nas/show/*/seq/*/{name}/{task_name}/work/*/*/*.*"
        ]

        work_files = []
        for pattern in search_patterns:
            for file in glob.glob(pattern, recursive=True):
                work_files.append({
                    "file_name": file.rsplit('/', 1)[1],
                    "path": file,
                    "modified_date": datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
                })

        return work_files

    @staticmethod
    def get_publishes(task_id):
        """
        특정 Task에 연결된 PublishedFile을 조회
        """
        # PublishedFile 엔티티에서 Task ID를 기준으로 검색
        filters = [["task", "is", {"type": "Task", "id": task_id}]]
        fields = ["id", "code", "path", "description", "image", "created_at"]
        order = [{"field_name": "created_at", "direction": "desc"}]  # 최신순 정렬

        publishes = ShotGridAPI.sg.find("PublishedFile", filters, fields, order)
        publish_files = []
        
        # 퍼블리시 된 파일을 리스트로 리턴
        return [
            {
                'file_name' : publish['code'],
                'path' : publish['path']['local_path'],
                'description' : publish['description'],
                'thumbnail' : publish['image'],
                'created_at' : publish['created_at']
            }
            for publish in publishes
        ]
    
    
    @staticmethod
    def update_task_status(task_id, new_status):
        """
        Task 상태를 업데이트 (예: PND → IP)
        """
        ShotGridAPI.sg.update(
            "Task", task_id, {"sg_status_list": new_status}
        )

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
        return ShotGridAPI.sg.create("PublishedFile", data)

    @staticmethod
    def update_entity(entity_type, entity_id, description, thumbnail_path):
        """
        특정 엔티티의 설명 또는 썸네일 업데이트
        """
        if description:
            ShotGridAPI.sg.update(
                entity_type, entity_id, {"description": description}
                )
        if thumbnail_path:
            ShotGridAPI.sg.upload_thumbnail(
                entity_type, entity_id, thumbnail_path
                )

    @staticmethod
    def update_task_thumbnail(task_id):
        """
        특정 Task의 썸네일을 최신 퍼블리시된 파일의 썸네일로 업데이트
        """
        publish_files = ShotGridAPI.get_publishes_for_task(task_id)

        if not publish_files:
            print(f"⚠ Task {task_id}에 연결된 퍼블리시 파일이 없습니다.")
            return False
        
        latest_publish = publish_files[0]
        latest_thumbnail = latest_publish.get("thumbnail")

        if not latest_thumbnail:
            print(f"⚠ 최신 퍼블리시 파일(ID {latest_publish['id']})에 썸네일이 없습니다.")
            return False
        
        ShotGridAPI.sg.update("Task", task_id, {"image": latest_thumbnail})
        print(f"Task {task_id}의 썸네일이 최신 퍼블리시 썸네일로 업데이트되었습니다!")
        return True

    @staticmethod
    def delete_published_file(publish_id):
        """
        특정 퍼블리시 파일 삭제
        """
        ShotGridAPI.sg.delete("PublishedFile", publish_id)