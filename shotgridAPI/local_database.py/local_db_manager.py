import json
import os

DATA_FILE = "/nas/Viper/DB/local_work_files.json"

class LocalDatabaseManager:
    """
    로컬 JSON 데이터베이스 관리
    """

    def __init__(self, file_path=DATA_FILE):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        """
        JSON 데이터 불러오기
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_data(self):
        """
        데이터를 JSON 파일에 저장
        """
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)

    def update_work_file_data(self, work_files):
        """
        Work 파일 데이터를 JSON에 저장
        """
        self.data["work_files"] = work_files
        self.save_data()
