import os
from shotgrid_db import ShotgridDB

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

        for shot in project.get("shots", []):
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

            for shot in project.get("shots", []):
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

            for shot in project.get("shots", []):
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

        return works

    def get_publishes_for_task(self, task_id):
        """
        특정 Task의 퍼블리시 파일 가져오기
        """
        task = self.get_task_by_id(task_id)
        publishes = task["publishes"]

        return publishes

    def close(self):
        """
        MongoDB 연결 종료
        """
        self.db.close()
