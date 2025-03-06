from pymongo import MongoClient

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