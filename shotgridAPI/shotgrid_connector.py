import shotgun_api3
import os
import glob
from typing import TypedDict
from datetime import datetime

class PublishedFileData(TypedDict):
    file_name: str
    file_path: str
    description: str
    thumbnail: str

class ShotGridAPI:
    """
    샷그리드 API 연결 및 프로젝트 데이터 조회, 업데이트
    """

    SG_URL = "https://5thacademy.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper_key"
    API_KEY = "bxdqpmdbwQnu0ooivsiilii&u"

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
            ["id", "code", "sg_asset_type", "description"]
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
            ["id", "code", "sg_asset_type", "description", "sg_cut_in", "sg_cut_out"]
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
            ["id", "project", "entity", "content", "task_assignees", "sg_status_list", "start_date", "due_date"]
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
            f"/nas/show/*/assets/*/{name}/{task_name}/work/*/scenes/*.*",
            f"/nas/show/*/seq/*/{name}/{task_name}/work/*/scenes/*.*"
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
                'created_at' : publish['created_at']
            }
            for publish in publishes
        ]
    
    @staticmethod
    def get_publish_metadata(task_id):
        """
        프로젝트, 엔티티 타입, 엔티티 이름, 태스크 이름을 샷그리드에서 가져오기
        """
        task = ShotGridAPI.sg.get_entity("Task", task_id, ["project", "entity", "content"])
        
        if not task or "entity" not in task:
            raise ValueError(f"Task ID {task_id}에 대한 정보를 찾을 수 없습니다.")

        project_name = task["project"]["name"]
        entity_type = task["entity"]["type"]  # "Asset" 또는 "Shot"
        entity_name = task["entity"]["name"]
        task_name = task["content"]  # 태스크 이름

        return project_name, entity_type, entity_name, task_name
    
    @staticmethod
    def update_task_status(task_id, new_status):
        """
        Task 상태를 업데이트 (예: PND → IP)
        """
        ShotGridAPI.sg.update(
            "Task", task_id, {"sg_status_list": new_status}
        )
    
    @staticmethod
    def create_version(task_id, file_path, thumbnail_path, description):
        """
        새로운 버전 생성
        """
        file_name = os.path.basename(file_path)

        task_data = ShotGridAPI.sg.find_one("Task", [["id", "is", task_id]], ["project", "entity"])
        if not task_data:
            print(f"⚠️ Task {task_id}를 찾을 수 없습니다.")
            return None
        
        project_id = task_data["project"]["id"]
        link_entity = task_data.get("entity")  # 연결된 Asset, Shot 등

        version_data = {
            "project": {"type": "Project", "id": project_id},
            "code": file_name,  # 버전 이름 (파일명으로 설정)
            "description": description,  # 설명 추가
            "sg_task": {"type": "Task", "id": task_id},  # 연결된 Task
            "entity": {"type": link_entity["type"], "id": link_entity["id"]}
        }

        # ShotGrid에 Version 생성
        version = ShotGridAPI.sg.create("Version", version_data)

        # 파일을 ShotGrid에 업로드 (Uploaded Movie 필드)
        if version:
            ShotGridAPI.sg.upload("Version", version["id"], file_path, field_name="sg_uploaded_movie")
        # 썸네일 업로드
        if os.path.exists(thumbnail_path):
            ShotGridAPI.sg.upload_thumbnail("Version", version["id"], thumbnail_path)

        return version

    @staticmethod
    def create_published_file(task_id, version, data:PublishedFileData):
        """
        퍼블리시된 파일을 ShotGrid에 등록
        """
        try:
            file_name = os.path.basename(data["file_path"])

            task_data = ShotGridAPI.sg.find_one("Task", [["id", "is", task_id]], ["project", "entity"])
            if not task_data or "project" not in task_data:
                print(f"오류: Task {task_id}에 해당하는 프로젝트를 찾을 수 없습니다.")
                return None
            
            project_id = task_data["project"]["id"]
            link_entity = task_data.get("entity")  # 연결된 Asset, Shot 등

            publish_data = {
                "code": file_name,
                "description": data["description"],
                "project": {"type": "Project", "id": project_id},
                "task": {"type": "Task", "id": task_id},
                "entity": {"type": link_entity["type"], "id": link_entity["id"]},
                "path": {"local_path": data["file_path"]}
            }

            publish = ShotGridAPI.sg.create("PublishedFile", publish_data)

            if not publish:
                print(f"⚠️ 퍼블리시 파일 생성 실패: {file_name}")
                return None

            print(f"ShotGrid PublishedFile 생성 완료: {file_name} (ID: {publish['id']})")

            # 썸네일 파일이 존재하면 업로드
            if os.path.exists(data["thumbnail"]):
                ShotGridAPI.sg.upload_thumbnail("PublishedFile", publish["id"], data["thumbnail"])
                print(f"썸네일 업로드 완료: {data['thumbnail']}")
            
            if version:
                ShotGridAPI.sg.update("PublishedFile", publish["id"], {"version": {"type": "Version", "id": version["id"]}})
                print(f"퍼블리시 파일과 Version 연결 완료: {version['id']}")

            return publish
        
        except Exception as e:
            print(f"오류 발생: {e}")
            return None
    
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
    def delete_published_file(publish_id):
        """
        특정 퍼블리시 파일 삭제
        """
        ShotGridAPI.sg.delete("PublishedFile", publish_id)