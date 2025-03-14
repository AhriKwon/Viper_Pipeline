from pymongo import MongoClient, UpdateOne
from typing import TypedDict
from datetime import datetime

from shotgrid_connector import ShotGridAPI
sg_api = ShotGridAPI()

class PublishedFileData(TypedDict):
    file_name: str
    file_path: str
    description: str
    thumbnail: str

class ShotgridDB:
    """
    MongoDB 데이터 저장 및 관리
    """

    def __init__(self, db_name="shotgrid_db"):
        self.db_name = db_name
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]

    def save_project_data(self, project_data):
        """
        프로젝트 데이터를 MongoDB에 저장
        """
        collection = self.db["projects"]
        collection.update_one(
            {"project_id": project_data["project_id"]},
            {"$set": project_data},
            upsert=True
        )
        print(f"프로젝트 {project_data['project_name']} 저장 완료!")
    
    def get_database(self):
        """
        MongoDB 데이터베이스 객체 반환
        """
        return self.db.projects.find({})

    def get_project_by_name(self, project_name):
        """
        특정 프로젝트 데이터 조회
        """
        return self.db.projects.find_one({"project_name": project_name})
    
    def update_project(self, project_name, updated_data):
        """
        특정 프로젝트 데이터를 업데이트
        """
        self.db.projects.update_one(
            {"project_name": project_name},
            {"$set": updated_data},
            upsert=True  # 데이터가 없으면 생성
        )

    def update_entity_status(self, entity_type, entity_id: int, new_status) -> int:
        """
        특정 엔티티(Task, Asset, Shot 등)의 상태를 변경

        Returns:
            int: 수정된 문서의 개수
        """
        collection = self.db["projects"]
        result = collection.update_one(
            {f"{entity_type}.id": entity_id},
            {"$set": {f"{entity_type}.$.sg_status_list": new_status}}
        )
        return result.modified_count
    
    def add_workfile(self, task_id: int, file_path: str) -> int:
        """
        새로운 Work 파일이 생성되었을 때 경로를 DB에 추가
        """
        collection = self.db["projects"]
        
        # assets.tasks 내부에서 task_id가 있는지 확인
        asset_result = collection.find_one({"assets.tasks.id": task_id})
        if asset_result:
            update_result = collection.update_one(
                {"assets.tasks.id": task_id},
                {"$push": {"assets.$[].tasks.$[task].works": 
                        {"path": file_path, "created_at": datetime.now().isoformat()}}},
                array_filters=[{"task.id": task_id}]
            )
            return update_result.modified_count

        # sequences.shots.tasks 내부에서 task_id가 있는지 확인
        shot_result = collection.find_one({"sequences.shots.tasks.id": task_id})
        if shot_result:
            update_result = collection.update_one(
                {"sequences.shots.tasks.id": task_id},
                {"$push": {"sequences.$[].shots.$[].tasks.$[task].works": 
                        {"path": file_path, "created_at": datetime.now().isoformat()}}},
                array_filters=[{"task.id": task_id}]
            )
            return update_result.modified_count

        # task_id가 어디에도 존재하지 않으면 실패 처리
        print(f"오류: task_id {task_id}를 assets 또는 sequences.shots에서 찾을 수 없습니다.")
        return 0
    
    def add_published_file(self, task_id: int, data:PublishedFileData) -> int:
        """
        퍼블리시된 파일을 DB에 추가

        Args:
            task_id (int): Task의 ID
            data (dict): 퍼블리시될 파일의 정보
                - file_name (str): 파일 이름
                - file_path (str): 파일 경로
                - description (str): 설명
                - thumbnail (str): 썸네일 URL

        Returns:
            int: 수정된 문서의 개수
        """
        collection = self.db["projects"]

        # 먼저 assets 하위의 task인지 확인
        result_assets = collection.update_one(
            {"assets.tasks.id": task_id},
            {"$push": {"assets.$[].tasks.$[task].publishes": {
                "file_name": data["file_name"],
                "path": data["file_path"],
                "description": data["description"],
                "thumbnail": data["thumbnail"],
                "created_at": datetime
            }}},
            array_filters=[{"task.id": task_id}]
        )

        if result_assets.modified_count > 0:
            print(f"Task {task_id}의 퍼블리시 파일이 'assets'에 추가됨")
            return result_assets.modified_count  # assets에 추가된 경우 종료

        # assets에 없었다면 sequences -> shots 내에 있는지 확인
        result_shots = collection.update_one(
            {"sequences.shots.tasks.id": task_id},
            {"$push": {"sequences.$[].shots.$[].tasks.$[task].publishes": {
                "file_name": data["file_name"],
                "path": data["file_path"],
                "description": data["description"],
                "thumbnail": data["thumbnail"],
                "created_at": datetime
            }}},
            array_filters=[{"task.id": task_id}]
        )

        if result_shots.modified_count > 0:
            print(f"Task {task_id}의 퍼블리시 파일이 'sequences -> shots'에 추가됨")
            return result_shots.modified_count  # sequences -> shots에 추가된 경우 종료

        # 두 위치에도 존재하지 않으면 오류 출력
        print(f"⚠️ Task {task_id}를 찾을 수 없습니다. 퍼블리시 파일 추가 실패")
        return 0  # 아무것도 수정되지 않음
    
    def update_description(self, entity_type, entity_id: int, new_description) -> int:
        """
        특정 엔티티(Task, Shot 등)의 설명을 업데이트
        """
        collection = self.db["projects"]
        result = collection.update_one(
            {f"{entity_type}.id": entity_id},
            {"$set": {f"{entity_type}.$.description": new_description}}
        )
        return result.modified_count
    
    def insert_data(self, collection_name, data):
        """
        데이터 삽입
        """
        self.db[collection_name].insert_one(data)
    
    def reset_database(self):
        """
        데이터베이스 전체 초기화 (모든 데이터 삭제)
        """
        self.client.drop_database(self.db_name)  # 데이터베이스 전체 삭제
        print("데이터베이스가 초기화되었습니다.")

    def close(self):
        """
        MongoDB 연결 종료
        """
        self.client.close()