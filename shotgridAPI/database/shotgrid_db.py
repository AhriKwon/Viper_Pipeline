from pymongo import MongoClient

class ShotGridDB:
    """
    MongoDB 연결 및 CRUD 기능
    """

    def __init__(self, db_name="shotgrid_db", host="localhost", port=27017):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]  # 데이터베이스 선택

    def get_project(self, project_name):
        """
        특정 프로젝트 데이터를 불러오기
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

    def get_tasks_by_user(self, user_id):
        """
        특정 유저의 Task 목록을 가져오기
        """
        return list(self.db.tasks.find({"assigned_to": user_id}))

    def get_published_files(self, task_id):
        """
        특정 Task에 연결된 퍼블리시 파일 가져오기
        """
        return list(self.db.published_files.find({"task_id": task_id}))

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
