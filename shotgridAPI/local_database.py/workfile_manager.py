import os
import glob
from local_db_manager import LocalDatabaseManager

# Work 파일이 저장된 NAS 경로
WORK_FILE_PATHS = [
    "/nas/show/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/{TASK}/work/{DCC}/scenes/",
    "/nas/show/{PROJECT}/seq/{SEQ}/{SHOT}/{TASK}/work/{DCC}/scenes/"
]

class LocalWorkFileManager:
    """
    로컬 Work 파일을 자동 검색하고 Task 기준으로 정리
    """

    def __init__(self):
        self.db_manager = LocalDatabaseManager()
        self.work_files = {}

    def scan_work_files(self, project_name):
        """
        NAS 경로에서 Work 파일을 자동 검색하여 저장
        """
        for base_path in WORK_FILE_PATHS:
            path = base_path.replace("{PROJECT}", project_name)
            for file_path in glob.glob(os.path.join(path, "**/*.*"), recursive=True):
                task_name = self.extract_task_name(file_path)
                if task_name:
                    if task_name not in self.work_files:
                        self.work_files[task_name] = []
                    self.work_files[task_name].append(file_path)

        # 데이터베이스에 저장
        self.db_manager.update_work_file_data(self.work_files)
        print(f"Work 파일 검색 완료: {len(self.work_files)}개의 Task에서 파일을 찾음")

    def extract_task_name(self, file_path):
        """
        파일 경로에서 Task 이름을 추출
        예: "/nas/show/Viper/assets/Character/HERO/MDL/work/maya/scenes/HERO_MDL_v001.ma"
        → Task 이름: "MDL"
        """
        parts = file_path.split("/")
        try:
            return parts[-5]  # TASK 부분을 기준으로 추출
        except IndexError:
            return None

    def get_work_files_by_task(self, task_name):
        """
        특정 Task에 해당하는 Work 파일 목록 반환
        """
        return self.db_manager.data.get("work_files", {}).get(task_name, [])

