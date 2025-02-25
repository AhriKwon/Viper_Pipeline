
from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QGroupBox, QLabel, QTableWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QPixmap
import sys
from shotgun_api3 import Shotgun





  # ==================================샷그리드 연동 클래스===========================================

class ShotGridConnector:

    def __init__(self, sg_url, script_name, api_key):
        self.sg = Shotgun(sg_url, script_name, api_key)

    def get_user_tasks(self, user_id):
     # task 목록 가져오기 
        filters = [["task_assignees", "in", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "content", "entity"]
        tasks = self.sg.find("Task", filters, fields)
        return tasks

    def get_task_versions(self, task_id):
       # task에 연결된 정보 가져오기 
        filters = [["sg_task", "is", {"type": "Task", "id": task_id}]]
        fields = ["id", "code", "created_at", "sg_thunbnail"]
        versions = self.sg.find("Version", filters, fields)
        return versions
    




#=================================가져온 파일 정보를 정렬하는 클래스===========================================


class ShotGridFileManager:
   
    def __init__(self, sg_connector):
        self.sg_connector = sg_connector

    def get_sorted_files_for_user(self, user_id, sort_by="created_at"):
        tasks = self.sg_connector.get_user_tasks(user_id)
        if not tasks:
            return []

        file_list = []

        for task in tasks:
            task_id = task["id"]
            versions = self.sg_connector.get_task_versions(task_id)
            
            for version in versions:
                file_list.append({
                    "task_id": task_id,
                    "task_name": task["content"],
                    "version_id": version["id"],
                    "file_name": version["code"],
                    "created_at": version["created_at"]
                  
                })

        sorted_files = sorted(file_list, key=lambda x: x[sort_by])
        return sorted_files


class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.sg_url = "https://minseo.shotgrid.autodesk.com"
        self.script_name = "Viper"
        self.api_key = "jvceqpsfqvbl1azzcns?haksI"
        self.sg_connector = ShotGridConnector(self.sg_url, self.script_name, self.api_key)
        self.file_manager = ShotGridFileManager(self.sg_connector)
        self.populate_table()

    def load_ui(self):
        ui_file_path = "/home/rapa/teamwork/load.ui" 
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()

        # UI 컴포넌트 가져오기
        self.tableWidget_2 = self.ui.findChild(QTableWidget, "tableWidget_2")
        self.groupBox_infor = self.ui.findChild(QGroupBox, "groupBox_infor")
        self.label_file_name = self.ui.findChild(QLabel, "label_filename")
        self.label_task_name = self.ui.findChild(QLabel, "label_task_name")
        self.label_version_id = self.ui.findChild(QLabel, "label_version_id")
        self.label_created_at = self.ui.findChild(QLabel, "label_created_at")

    def populate_table(self):
        user_id = 1234  # 예시 사용자 ID
        sorted_files = self.file_manager.get_sorted_files_for_user(user_id, sort_by="created_at")

        self.tableWidget_2.setRowCount(len(sorted_files))
        self.tableWidget_2.setColumnCount(5)  # 파일명, Task명, 버전 ID, 생성일


        # 행 만들기 
        for row, file in enumerate(sorted_files):
            self.tableWidget_2.setItem(row, 1, QTableWidgetItem(file["file_name"]))
            self.tableWidget_2.setItem(row, 2, QTableWidgetItem(file["task_name"]))
            self.tableWidget_2.setItem(row, 3, QTableWidgetItem(str(file["version_id"])))
            self.tableWidget_2.setItem(row, 4, QTableWidgetItem(str(file["created_at"])))

            if file["thumbnail_url"]:
                pixmap = QPixmap(file["thumbnail_url"])
                label = QLabel()
                label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                self.tableWidget_2.setCellWidget(row, 0, label) 
            
            else:
                self.tableWidget_2.setCellWidget(row, 0, QLabel())

        # 파일 클릭 시 정보를 업데이트할 이벤트 연결
        self.tableWidget_2.cellClicked.connect(self.on_file_click)

    def on_file_click(self, row, column):
        """파일 클릭 시 해당 파일의 정보를 groupBox_infor에 표시"""
        file_name = self.tableWidget_2.item(row, 0).text()
        task_name = self.tableWidget_2.item(row, 1).text()
        version_id = self.tableWidget_2.item(row, 2).text()
        created_at = self.tableWidget_2.item(row, 3).text()

        # groupBox_infor에 파일 정보 표시
        self.label_file_name.setText(f"파일 이름: {file_name}")
        self.label_task_name.setText(f"Task 이름: {task_name}")
        self.label_version_id.setText(f"버전 ID: {version_id}")
        self.label_created_at.setText(f"생성일: {created_at}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PublishUI()
    ex.show()  
    app.exec()
