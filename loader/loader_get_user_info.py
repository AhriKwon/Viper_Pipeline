import os, sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_connector import ShotGridConnector

class LoaderMyTaskManager:

    """
    로더 UI의 'My Task' 탭에서 필요한 정보를 불러오는 클래스
    """

    @staticmethod
    def get_my_tasks(user_id):
        """
        현재 로그인한 사용자에게 할당된 Task 목록을 가져온다
        """
        tasks = ShotGridConnector.get_user_tasks(user_id)

        if not tasks:
            print("⚠ 현재 할당된 Task가 없습니다.")
            return []

        formatted_tasks = []
        for task in tasks:
            task_id = task["id"]
            task_name = task["content"]
            task_status = task["sg_status_list"]
            start_date = task["start_date"]
            due_date = task["due_date"]
            entity = task.get("entity", {})
            entity_name = entity.get("name", "Unknown")
            entity_type = entity.get("type", "Unknown")

            # 최신 퍼블리시 파일 및 썸네일 가져오기
            latest_publish = ShotGridConnector.get_publishes_for_task(task_id)
            latest_file = latest_publish[0] if latest_publish else None

            task_info = {
                "task_id": task_id,
                "task_name": task_name,
                "status": task_status,
                "start_date": start_date,
                "due_date": due_date,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "latest_file_path": latest_file["path"] if latest_file else None,
                "thumbnail": latest_file["thumbnail"] if latest_file else None,
            }

            formatted_tasks.append(task_info)

        return formatted_tasks

    @staticmethod
    def get_my_task_status(user_id):
        """
        현재 로그인한 사용자의 전체 Task 상태를 요약해서 반환해준다
        """
        tasks = LoaderMyTaskManager.get_my_tasks(user_id)
        status_summary = {"PND": 0, "IP": 0, "FIN": 0}

        for task in tasks:
            status = task["status"]
            if status in status_summary:
                status_summary[status] += 1

        return status_summary

    @staticmethod
    def categorize_and_sort_by_dates(items, key_id):
        """Start Date, Due Date 기준으로 정렬"""
        categorized_by_start = sorted(items, key=lambda x: x.get("start_date") or "9999-12-31")
        categorized_by_due = sorted(items, key=lambda x: x.get("due_date") or "9999-12-31")

        return {
            "by_start_date": categorized_by_start,
            "by_due_date": categorized_by_due
        }

    @staticmethod
    def categorize_and_sort_tasks_by_dates(self):
        """Task 목록을 Start Date, Due Date 기준으로 정렬"""

        tasks = LoaderMyTaskManager.get_my_tasks()
        return self.categorize_and_sort_by_dates(tasks, "id")
