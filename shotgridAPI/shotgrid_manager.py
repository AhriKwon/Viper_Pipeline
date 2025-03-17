import os
from typing import TypedDict
from shotgrid_db import ShotgridDB
from shotgrid_connector import ShotGridAPI
sg_db = ShotgridDB()
sg_api = ShotGridAPI()

class PublishedFileData(TypedDict):
    file_name: str
    file_path: str
    description: str
    thumbnail: str

class ShotGridManager:
    """
    ShotGrid 데이터 관리 (프로젝트, Task, 퍼블리시, Work 파일)
    """

    def __init__(self, db_name="shotgrid_db"):
        self.db = ShotgridDB(db_name)

    def get_project(self, project_name):
        """
        특정 프로젝트 데이터 조회
        """
        return self.db.get_project_by_name(project_name)
    
    def get_projects(self):
        """
        특정 유저가 참여하고 있는 프로젝트 목록을 조회
        """
        projects = []
        data = self.db.get_database()
        for project in data:
            projects.append(project["project_name"])
        return projects

    def get_project_assets(self, project_name):
        """
        특정 프로젝트의 모든 에셋 정보 가져오기
        """
        project = self.db.get_project_by_name(project_name)
        return project.get("assets", []) if project else []
    
    def get_project_sequences(self, project_name):
        """
        특정 프로젝트의 모든 시퀀스 정보 가져오기
        """
        project = self.db.get_project_by_name(project_name)
        return project.get("sequences", []) if project else []
    
    def get_project_tasks(self, project_name):
        """
        특정 프로젝트의 모든 테스크 정보 가져오기
        """
        project = self.db.get_project_by_name(project_name)
        tasks = []
        
        for asset in project.get("assets", []):
            for task in asset.get("tasks", []):
                tasks.append(task)

        for sequence in project.get("sequences", []):
            for shot in sequence.get("shots", []):
                for task in shot.get("tasks", []):
                    tasks.append(task)

        return tasks

    def get_tasks_by_user(self, user_id: int) -> list:
        """
        특정 유저 ID를 기반으로 해당 유저에게 할당된 모든 Task를 조회하는 함수
        :param user_id: 조회할 유저의 ID
        :return: 해당 유저에게 할당된 Task 목록
        """
        tasks = []
        projects = self.db.get_database()
        
        for project in projects:
            for asset in project.get("assets", []):
                for task in asset.get("tasks", []):
                    if any(assignee["id"] == user_id for assignee in task.get("task_assignees", [])):
                        tasks.append(task)

            for sequence in project.get("sequences", []):
                for shot in sequence.get("shots", []):
                    for task in shot.get("tasks", []):
                        if any(assignee["id"] == user_id for assignee in task.get("task_assignees", [])):
                            tasks.append(task)

        return tasks
    
    def filter_tasks_by_status(self, tasks, status):
        """
        특정 상태(WTG, IP, FIN)에 해당하는 Task만 필터링
        """
        filtered_tasks=[]
        for task in tasks:
            if task["sg_status_list"] == status :
                filtered_tasks.append(task)
        
        return filtered_tasks
    
    def get_task_by_id(self, task_id: int) -> dict:
        """
        특정 Task ID를 입력하면 해당 Task 정보를 반환하는 함수
        :param task_id: 조회할 Task의 ID
        :return: Task 정보 (딕셔너리 형태)
        """
        projects = self.db.get_database()
        
        for project in projects:
            for asset in project.get("assets", []):
                for task in asset.get("tasks", []):
                    if task["id"] == task_id:
                        return task

            for sequence in project.get("sequences", []):
                for shot in sequence.get("shots", []):
                    for task in shot.get("tasks", []):
                        if task["id"] == task_id:
                            return task

        return None  # Task가 존재하지 않을 경우 None 반환

    def get_works_for_task(self, task_id):
        """
        특정 Task의 워크 파일 가져오기
        """
        task = self.get_task_by_id(task_id)
        works = task["works"]

        if task is None:
            print(f"⚠️ 오류: task_id {task_id}에 해당하는 Task가 없습니다.")
            return []  # 빈 리스트 반환

        return works

    def get_publishes_for_task(self, task_id):
        """
        특정 Task의 퍼블리시 파일 가져오기
        """
        task = self.get_task_by_id(task_id)
        publishes = task["publishes"]

        return publishes
    
    def get_publish_path(self, project_name, task_id):
        """
        테스크 ID를 기반으로 퍼블리시된 파일이 저장되는 경로를 반환
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            return None
        
        # 퍼블리시 경로 설정
        project = project_name
        task_name = task["content"].rsplit('_',1)[1]
        asset_name = task["content"].rsplit('_',1)[0]

        assets = self.get_project_assets(project_name)

        for asset in assets:
            if asset["code"] == asset_name:
                asset_type = asset.get("sg_asset_type", "unknown")

        # 애셋 테스크인지 샷 테스크인지 확인
        if task_name in ["LAY", "ANM", "FX", "LGT", "CMP"] :
            sequence = task["content"].rsplit('_')[0]
            shot = task["content"].rsplit('_',1)[0]
            publish_path = f"/nas/show/{project}/seq/{sequence}/{shot}/{task_name}/pub"
        else:
            publish_path = f"/nas/show/{project}/assets/{asset_type}/{asset_name}/{task_name}/pub"

        return publish_path
    
    def get_thumbnail_save_path(self):
        """
        썸네일 저장 경로 생성
        """
        project, entity_type, entity_name, task_name = sg_api.get_publish_metadata()
        base_path = f"/nas/show/{project}/{'assets' if entity_type == 'Asset' else 'seq'}/{entity_name}/{task_name}/pub/thumb"
        return os.path.join(base_path, f"{task_name}.png")
    
    def get_task_id_from_file(self, file_path):
        """
        DB를 통해 파일 경로에서 Task ID를 추출하여 반환
        """
        return sg_db.get_task_id_from_file(file_path)

    def publish(self, task_id: int, version_path: str, data: PublishedFileData):
        """
        파일 퍼블리시 후 데이터베이스 및 ShotGrid에 반영
        """
        try:
            print(f"퍼블리시 데이터 확인: {data}")

            if not isinstance(data, dict):
                raise TypeError(f"데이터 타입 오류: data는 dict여야 합니다. 현재 타입: {type(data)}")
            
            # 데이터베이스에 저장
            sg_db.add_published_file(task_id, data)

            # ShotGrid에 버전 파일 등록
            version = sg_api.create_version(task_id, version_path, data["thumbnail"], data["description"])
            if not version:
                print(f"⚠️ ShotGrid 버전 생성 실패: {data['file_path']}")
                return None
        
            # ShotGrid에 퍼블리시된 파일 등록
            published_file = sg_api.create_published_file(task_id, version, data)
            if not published_file:
                print(f"⚠️ ShotGrid 퍼블리시 실패: {data['file_path']}")
                return None
        
            # 퍼블리시된 썸네일을 태스크 썸네일로 업데이트
            sg_api.update_entity("Task", task_id, None, data["thumbnail"])

            print(f"퍼블리시 완료: {published_file['code']} (ID: {published_file['id']})")
            return published_file
        
        except TypeError as e:
            print(f"데이터 타입 오류: {e}")
            return None
        
        except Exception as e:
            print(f"퍼블리시 중 오류 발생: {e}")
            return None

    def close(self):
        """
        MongoDB 연결 종료
        """
        self.db.close()