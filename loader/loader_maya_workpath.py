# import os
# import shotgun_api3
# import sys
# import subprocess
# from PySide6 import QtWidgets, QtGui, QtCore

# class ShotGridConnector:
#     """
#     ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스
#     """
#     # ShotGrid 서버 정보 설정
#     SG_URL = "https://minseo.shotgrid.autodesk.com"
#     SCRIPT_NAME = "Viper"
#     API_KEY = "jvceqpsfqvbl1azzcns?haksI"

#     # ShotGrid API 연결
#     sg = shotgun_api3.Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

#     @staticmethod
#     def get_user_tasks(user_id):
#         """
#         현재 사용자의 Task 목록을 가져옴
#         """
#         tasks = ShotGridConnector.sg.find(
#             "Task",
#             [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
#             ["id", "content", "sg_status_list", "start_date", "due_date", "entity"]
#         )
#         return tasks
    
#     @staticmethod
#     def get_publishes_for_task(task_id):
#         """
#         특정 Task에 연결된 PublishedFile을 조회
#         """
#         # PublishedFile 엔티티에서 Task ID를 기준으로 검색
#         filters = [["task", "is", {"type": "Task", "id": task_id}]]
#         fields = ["id", "code", "path", "description", "image", "created_at"]
#         order = [{"field_name": "created_at", "direction": "desc"}]  # 최신순 정렬

#         publishes = ShotGridConnector.sg.find("PublishedFile", filters, fields, order)
#         publish_files = []
        
#         # 퍼블리시 된 파일을 리스트로 리턴
#         if publishes:
#             print(f"Task {task_id}에 연결된 퍼블리시 파일 목록:")
#             for publish in publishes:
#                 publish_dict = {
#                     'id' : publish['id'],
#                     'file_name' : publish['code'],
#                     'path' : publish['path']['local_path'],
#                     'description' : publish['description'],
#                     'thumbnail' : publish['image'],
#                     'created_at' : publish['created_at']
#                 }
#                 publish_files.append(publish_dict)
#             return publish_files
        
#         # 테스크 안에 퍼블리시 된 파일이 없는 경우
#         else:
#             print(f"⚠ Task {task_id}에 연결된 퍼블리시 파일이 없습니다.")
#             return []

#     @staticmethod
#     def get_task_status(task_id):
#         """
#         특정 Task의 상태(PND, IP, FIN)를 가져옴
#         """
#         task = ShotGridConnector.sg.find_one(
#             "Task",
#             [["id", "is", task_id]],
#             ["sg_status_list"]
#         )
#         if task:
#             return task["sg_status_list"]
#         else:
#             None

#     @staticmethod
#     def filter_tasks_by_status(tasks, status):
#         """
#         특정 상태(PND, IP, FIN)에 해당하는 Task만 필터링
#         """
#         if task["sg_status_list"] == status : 
#             for task in tasks:
#                 return task

#     @staticmethod
#     def update_task_status(task_id, new_status):
#         """
#         Task 상태를 업데이트 (예: PND → IP)
#         """
#         ShotGridConnector.sg.update(
#             "Task", task_id, {"sg_status_list": new_status}
#         )

#     @staticmethod
#     def sync_task_status(user_id):
#         """
#         ShotGrid의 최신 Task 상태를 로더 UI와 동기화
#         (특정 사용자의 테스크 상태만 불러옴)
#         """
#         tasks = ShotGridConnector.get_user_tasks(user_id)
#         updated_tasks = {task["id"]: task["sg_status_list"] for task in tasks}
        
#         return updated_tasks

#     @staticmethod
#     def create_pub_file(task_id, file_path, thumbnail_path, description):
#         """
#         새로운 퍼블리시 파일을 Task에 등록
#         """
#         file_name = os.path.basename(file_path)
#         data = {
#             "code": file_name,
#             "image": thumbnail_path,
#             "description": description,
#             "task": {"type": "Task", "id": task_id},
#             "path": {"local_path": file_path}
#         }
#         return ShotGridConnector.sg.create("PublishedFile", data)

#     @staticmethod
#     def update_entity(entity_type, entity_id, description, thumbnail_path):
#         """
#         특정 엔티티의 설명 또는 썸네일 업데이트
#         """
#         if description:
#             ShotGridConnector.sg.update(
#                 entity_type, entity_id, {"description": description}
#                 )
#         if thumbnail_path:
#             ShotGridConnector.sg.upload_thumbnail(
#                 entity_type, entity_id, thumbnail_path
#                 )

#     @staticmethod
#     def delete_published_file(publish_id):
#         """
#         특정 퍼블리시 파일 삭제
#         """
#         ShotGridConnector.sg.delete("PublishedFile", publish_id)

#     @staticmethod
#     def update_task_thumbnail(task_id):
#         """
#         특정 Task의 썸네일을 최신 퍼블리시된 파일의 썸네일로 업데이트
#         """
#         publish_files = ShotGridConnector.get_publishes_for_task(task_id)

#         if not publish_files:
#             print(f"⚠ Task {task_id}에 연결된 퍼블리시 파일이 없습니다.")
#             return False
        
#         latest_publish = publish_files[0]
#         latest_thumbnail = latest_publish.get("thumbnail")

#         if not latest_thumbnail:
#             print(f"⚠ 최신 퍼블리시 파일(ID {latest_publish['id']})에 썸네일이 없습니다.")
#             return False
        
#         ShotGridConnector.sg.update("Task", task_id, {"image": latest_thumbnail})
#         print(f"Task {task_id}의 썸네일이 최신 퍼블리시 썸네일로 업데이트되었습니다!")
#         return True
    


# class FileLoaderGUI(QtWidgets.QMainWindow):
#     """ShotGrid에서 퍼블리시된 파일을 불러오고 실행하는 GUI"""

#     def __init__(self, user_id):
#         super().__init__()
#         self.setWindowTitle("ShotGrid File Loader")
#         self.setGeometry(100, 100, 900, 600)
#         self.user_id = user_id
#         self.initUI()

#     def initUI(self):
#         """GUI 레이아웃 설정"""
#         main_widget = QtWidgets.QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QtWidgets.QVBoxLayout(main_widget)

#         # 사용자 Task 정보 불러오기
#         self.user_label = QtWidgets.QLabel(f"사용자 ID: {self.user_id}")
#         layout.addWidget(self.user_label)

#         # 파일 경로 입력창
#         self.file_path_input = QtWidgets.QLineEdit()
#         self.file_path_input.setPlaceholderText("파일 경로를 입력하세요.")
#         layout.addWidget(self.file_path_input)

#         # 파일 목록
#         self.file_list = QtWidgets.QListWidget()
#         self.file_list.itemDoubleClicked.connect(self.open_selected_file)
#         layout.addWidget(self.file_list)

#         # 버튼 영역
#         button_layout = QtWidgets.QHBoxLayout()
#         self.set_path_button = QtWidgets.QPushButton("경로 설정")
#         self.set_path_button.clicked.connect(self.set_file_path)
#         button_layout.addWidget(self.set_path_button)

#         self.open_button = QtWidgets.QPushButton("파일 실행")
#         self.open_button.clicked.connect(self.run_file)
#         button_layout.addWidget(self.open_button)

#         layout.addLayout(button_layout)

#         # 퍼블리시된 파일 불러오기
#         self.load_published_files()

#     def load_published_files(self):
#         """퍼블리시된 파일을 불러옴"""
#         self.file_list.clear()
#         tasks = ShotGridConnector.get_user_tasks(self.user_id)

#         for task in tasks:
#             files = ShotGridConnector.get_publishes_for_task(task["id"])
#             if not files:
#                 continue

#             for file in files:
#                 list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
#                 list_item.setData(QtCore.Qt.UserRole, file)
#                 self.file_list.addItem(list_item)

#     def set_file_path(self):
#         """사용자가 파일 경로를 설정"""
#         file_dialog = QtWidgets.QFileDialog()
#         file_path, _ = file_dialog.getOpenFileName(self, "파일 선택", "", "Maya Files (*.ma *.mb);;Nuke Files (*.nk);;All Files (*.*)")

#         if file_path:
#             self.file_path_input.setText(file_path)

#     def run_file(self):
#         """설정된 파일 경로를 읽고 Maya 또는 Nuke에서 실행"""
#         file_path = self.file_path_input.text().strip()
        
#         if not file_path or not os.path.exists(file_path):
#             QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
#             return

#         if file_path.endswith((".ma", ".mb")):
#             self.launch_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.launch_nuke(file_path)
#         else:
#             QtWidgets.QMessageBox.warning(self, "오류", "지원되지 않는 파일 형식입니다.")

#     def open_selected_file(self, item):
#         """리스트에서 선택한 파일을 실행"""
#         file_info = item.data(QtCore.Qt.UserRole)
#         if file_info:
#             self.file_path_input.setText(file_info["path"])
#             self.run_file()

#     def launch_maya(self, file_path):
#         """Maya 실행 후 파일 열기"""
#         maya_executable = self.find_maya_path()
#         if maya_executable:
#             subprocess.Popen([maya_executable, "-file", file_path], shell=True)
#             print(f"Maya 실행 및 파일 열기: {file_path}")
#         else:
#             QtWidgets.QMessageBox.warning(self, "오류", "Maya 실행 파일을 찾을 수 없습니다.")

#     def launch_nuke(self, file_path):
#         """Nuke 실행 후 파일 열기"""
#         nuke_executable = self.find_nuke_path()
#         if nuke_executable:
#             subprocess.Popen([nuke_executable, file_path], shell=True)
#             print(f"Nuke 실행 및 파일 열기: {file_path}")
#         else:
#             QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")

#     def find_maya_path(self):
#         """Maya 실행 파일 경로 찾기"""
#         possible_paths = ["/usr/autodesk/maya2023/bin/maya"]
#         for path in possible_paths:
#             if os.path.exists(path):
#                 return path
#         return None

#     def find_nuke_path(self):
#         """Nuke 실행 파일 경로 찾기"""
#         possible_paths = ["/usr/local/Nuke13.2v1/Nuke13.2"]
#         for path in possible_paths:
#             if os.path.exists(path):
#                 return path
#         return None


# # 실행
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     user_id = 121  # 실제 사용자 ID
#     window = FileLoaderGUI(user_id)
#     window.show()
#     sys.exit(app.exec())




#################################################################################################################################
import os
import sys
import subprocess
from PySide6 import QtWidgets, QtGui, QtCore

#  ShotGrid API 파일 가져오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_connector import ShotGridConnector


class FileLoaderGUI(QtWidgets.QMainWindow):
    """ShotGrid에서 퍼블리시된 파일을 불러오고 실행하는 GUI"""

    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("ShotGrid File Loader")
        self.setGeometry(100, 100, 900, 600)
        self.user_id = user_id
        self.initUI()

    def initUI(self):
        """GUI 레이아웃 설정"""
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        # 사용자 Task 정보 불러오기
        self.user_label = QtWidgets.QLabel(f" 사용자 ID: {self.user_id}")
        layout.addWidget(self.user_label)

        # 파일 경로 입력창
        self.file_path_input = QtWidgets.QLineEdit()
        self.file_path_input.setPlaceholderText(" 파일 경로를 입력하세요.")
        layout.addWidget(self.file_path_input)

        # 파일 목록
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_selected_file)
        layout.addWidget(self.file_list)

        # 버튼 영역
        button_layout = QtWidgets.QHBoxLayout()
        self.set_path_button = QtWidgets.QPushButton("경로 설정")
        self.set_path_button.clicked.connect(self.set_file_path)
        button_layout.addWidget(self.set_path_button)

        self.open_button = QtWidgets.QPushButton("파일 실행")
        self.open_button.clicked.connect(self.run_file)
        button_layout.addWidget(self.open_button)

        layout.addLayout(button_layout)

        # 퍼블리시된 파일 불러오기
        self.load_published_files()

    def load_published_files(self):
        """퍼블리시된 파일을 불러옴"""
        self.file_list.clear()
        tasks = ShotGridConnector.get_user_tasks(self.user_id)

        for task in tasks:
            files = ShotGridConnector.get_publishes_for_task(task["id"])
            if not files:
                continue

            for file in files:
                list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
                list_item.setData(QtCore.Qt.UserRole, file)
                self.file_list.addItem(list_item)

    def set_file_path(self):
        """사용자가 파일 경로를 설정"""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "파일 선택", "", "Maya Files (*.ma *.mb);;Nuke Files (*.nk);;All Files (*.*)")

        if file_path:
            self.file_path_input.setText(file_path)

    def run_file(self):
        """설정된 파일 경로를 읽고 Maya 또는 Nuke에서 실행"""
        file_path = self.file_path_input.text().strip()
        
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
            return

        if file_path.endswith((".ma", ".mb")):
            self.launch_maya(file_path)
        elif file_path.endswith(".nk"):
            self.launch_nuke(file_path)
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "지원되지 않는 파일 형식입니다.")

    def open_selected_file(self, item):
        """리스트에서 선택한 파일을 실행"""
        file_info = item.data(QtCore.Qt.UserRole)
        if file_info:
            self.file_path_input.setText(file_info["path"])
            self.run_file()

    def launch_maya(self, file_path):
        """Maya 실행 후 파일 열기"""
        maya_executable = self.find_maya_path()
        if maya_executable:
            subprocess.Popen([maya_executable, "-file", file_path], shell=True)
            print(f" Maya 실행 및 파일 열기: {file_path}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Maya 실행 파일을 찾을 수 없습니다.")

    def launch_nuke(self, file_path):
        """Nuke 실행 후 파일 열기"""
        nuke_executable = self.find_nuke_path()
        if nuke_executable:
            subprocess.Popen([nuke_executable, file_path], shell=True)
            print(f" Nuke 실행 및 파일 열기: {file_path}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")

    def find_maya_path(self):
        """Maya 실행 파일 경로 찾기"""
        possible_paths = ["/usr/autodesk/maya2023/bin/maya"]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def find_nuke_path(self):
        """Nuke 실행 파일 경로 찾기"""
        possible_paths = ["/usr/local/Nuke13.2v1/Nuke13.2"]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None


# 실행
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    user_id = 121  # 실제 사용자 ID
    window = FileLoaderGUI(user_id)
    window.show()
    sys.exit(app.exec())
