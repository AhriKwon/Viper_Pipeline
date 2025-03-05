import os
import glob
from datetime import datetime
from shotgrid_db import ShotGridDB

class ShotGridManager:
    """
    ShotGrid 데이터 관리 (프로젝트, Task, 퍼블리시, Work 파일)
    """

    def __init__(self, db_name="shotgrid_db"):
        self.db = ShotGridDB(db_name)

    def get_user_tasks(self, user_id):
        """
        유저 ID를 받아서 할당된 테스크 조회
        """
        return self.db.get_tasks_by_user(user_id)
    
    def show_all_tasks(self):
        """
        DB에 저장된 모든 Task 조회
        """
        tasks = list(self.db.tasks.find({}))
        if tasks:
            print(f"현재 저장된 모든 Task: {tasks}")
        else:
            print("데이터베이스에 Task가 존재하지 않음")

    def get_project_assets(self, project_name):
        """
        특정 프로젝트의 에셋 정보 가져오기
        """
        project = self.db.get_project(project_name)
        return project.get("assets", []) if project else []

    def get_task_published_files(self, task_id):
        """
        특정 Task의 퍼블리시 파일 가져오기
        """
        return self.db.get_published_files(task_id)

    def find_work_files(self, project_name):
        """
        로컬 Work 파일 검색
        """
        project = self.db.get_project(project_name)
        work_root = project["root_directory"] if project else ""

        search_patterns = [
            f"{work_root}/assets/*/*/work/*/*/*.*",
            f"{work_root}/seq/*/*/work/*/*/*.*"
        ]

        work_files = []
        for pattern in search_patterns:
            for file in glob.glob(pattern, recursive=True):
                work_files.append({
                    "file_path": file,
                    "modified_date": datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
                })

        return work_files

    def update_task_description(self, task_id, new_description):
        """
        Task의 설명 업데이트
        """
        self.db.update_project({"id": task_id}, {"description": new_description})

    def close(self):
        """
        MongoDB 연결 종료
        """
        self.db.close()
