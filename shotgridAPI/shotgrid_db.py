from pymongo import MongoClient, UpdateOne
from typing import TypedDict
from datetime import datetime

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
        print(f"✅ 프로젝트 {project_data['project_name']} 저장 완료!")
    
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
        """
        collection = self.db["projects"]
        result = collection.update_one(
            {f"{entity_type}.id": entity_id},
            {"$set": {f"{entity_type}.$.sg_status_list": new_status}}
        )
        return result.modified_count
    
    def add_workfile(self, task_id: int, file_path) -> int:
        """
        새로운 Work 파일이 생성되었을 때 경로를 DB에 추가
        """
        collection = self.db["projects"]
        result = collection.update_one(
            {"assets.tasks.id": task_id},
            {"$push": {"assets.$[].tasks.$[task].works": {"path": file_path, "created_at": datetime.utcnow()}}},
            array_filters=[{"task.id": task_id}]
        )
        return result.modified_count
    
    def add_published_file(self, task_id: int, data:PublishedFileData) -> int:
        """
        퍼블리시된 파일을 DB에 추가

        Args:
            task_id (int): Task의 ID
            data (PublishedFileData): 퍼블리시될 파일의 정보
                - file_name (str): 파일 이름
                - file_path (str): 파일 경로
                - description (str): 설명
                - thumbnail (str): 썸네일 URL

        Returns:
            int: 수정된 문서의 개수
        """
        collection = self.db["projects"]
        result = collection.update_one(
            {"assets.tasks.id": task_id},
            {"$push": {"assets.$[].tasks.$[task].publishes": {
                "file_name": data["file_name"],
                "path": data["file_path"],
                "description": data["description"],
                "thumbnail": data["thumbnail"],
                "created_at": datetime.utcnow()
            }}},
            array_filters=[{"task.id": task_id}]
        )
        return result.modified_count
    
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

    def close(self):
        """
        MongoDB 연결 종료
        """
        self.client.close()