


# import os
# import time
# import subprocess
# import platform
# from PySide6 import QtWidgets, QtGui, QtCore


# class FileLoader:
#     """Maya, Nuke에서 생성된 파일을 불러오고 정보를 표시하는 클래스"""

#     def __init__(self, project_directory):
#         """
#         프로젝트 폴더 경로 설정
#         :param project_directory: 파일이 저장된 프로젝트 디렉토리
#         """
#         self.project_directory = project_directory

#     def get_file_info(self, file_path):
#         """
#         파일의 정보를 가져오는 함수
#         :param file_path: 파일 경로
#         :return: 파일 정보 (딕셔너리)
#         """
#         try:
#             file_stats = os.stat(file_path)
#             return {
#                 "file_name": os.path.basename(file_path),
#                 "file_size_kb": round(file_stats.st_size / 1024, 2),  # KB 단위 변환
#                 "created_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_ctime)),
#                 "modified_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime)),
#                 "file_path": file_path
#             }
#         except Exception as e:
#             print(f"파일 정보를 가져오는 중 오류 발생: {e}")
#             return None

#     def get_maya_nuke_files(self, sort_by="created_at"):
#         """
#         Maya (`.ma`, `.mb`), Nuke (`.nk`) 파일을 불러와 정렬
#         :param sort_by: 정렬 기준 (created_at, modified_at, file_size_kb)
#         :return: 파일 목록 (리스트)
#         """
#         if not os.path.exists(self.project_directory):
#             print("프로젝트 디렉토리가 존재하지 않습니다!")
#             return []

#         maya_nuke_files = []

#         for root, _, files in os.walk(self.project_directory):
#             for file_name in files:
#                 if file_name.endswith((".ma", ".mb", ".nk")):  # Maya, Nuke 파일 필터링
#                     file_path = os.path.join(root, file_name)
#                     file_info = self.get_file_info(file_path)
#                     if file_info:
#                         maya_nuke_files.append(file_info)

#         sorted_files = sorted(maya_nuke_files, key=lambda x: x.get(sort_by, ""), reverse=False)

#         return sorted_files

#     def open_file(self, file_path):
#         """
#         파일을 실행하는 함수 (Maya/Nuke 연동)
#         :param file_path: 실행할 파일 경로
#         """
#         if not os.path.exists(file_path):
#             print(f"파일이 존재하지 않습니다: {file_path}")
#             return

#         if file_path.endswith(".ma") or file_path.endswith(".mb"):
#             self.open_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.open_nuke(file_path)
#         else:
#             print(f"지원되지 않는 파일 형식: {file_path}")

#     def open_maya(self, file_path):
#         """Maya에서 파일 열기"""
#         try:
#             subprocess.Popen(["maya", "-file", file_path], shell=True)
#             print(f"Maya에서 파일을 실행합니다: {file_path}")
#         except Exception as e:
#             print(f"Maya 실행 오류: {e}")

#     def open_nuke(self, file_path):
#         """Nuke에서 파일 열기"""
#         try:
#             subprocess.Popen(["nuke", file_path], shell=True)
#             print(f"Nuke에서 파일을 실행합니다: {file_path}")
#         except Exception as e:
#             print(f"Nuke 실행 오류: {e}")


# class FileLoaderGUI(QtWidgets.QMainWindow):
#     """Maya, Nuke 파일을 불러오는 GUI"""

#     def __init__(self, project_directory):
#         super().__init__()
#         self.setWindowTitle("Maya & Nuke File Loader")
#         self.setGeometry(100, 100, 900, 600)
#         self.project_directory = project_directory
#         self.file_loader = FileLoader(project_directory)
#         self.initUI()

#     def initUI(self):
#         """GUI 레이아웃 설정"""
#         main_widget = QtWidgets.QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QtWidgets.QVBoxLayout(main_widget)

#         # 파일 리스트
#         self.file_list = QtWidgets.QListWidget()
#         self.file_list.itemDoubleClicked.connect(self.open_selected_file)
#         layout.addWidget(self.file_list)

#         # 파일 정보 표시
#         self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
#         layout.addWidget(self.file_info_label)

#         # 버튼 영역
#         button_layout = QtWidgets.QHBoxLayout()
#         self.refresh_button = QtWidgets.QPushButton("새로고침")
#         self.refresh_button.clicked.connect(self.load_files)
#         button_layout.addWidget(self.refresh_button)

#         layout.addLayout(button_layout)

#         # 파일 로드
#         self.load_files()

#     def load_files(self):
#         """Maya, Nuke 파일 목록을 가져와 리스트에 표시"""
#         self.file_list.clear()
#         files = self.file_loader.get_maya_nuke_files()

#         if not files:
#             self.file_info_label.setText("불러올 파일이 없습니다.")
#             return

#         for file in files:
#             item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
#             item.setData(QtCore.Qt.UserRole, file)
#             self.file_list.addItem(item)

#     def open_selected_file(self, item):
#         """리스트에서 선택한 파일을 열기"""
#         file_info = item.data(QtCore.Qt.UserRole)
#         if file_info:
#             self.file_info_label.setText(
#                 f" {file_info['file_name']}\n"
#                 f" 위치: {file_info['file_path']}\n"
#                 f" 크기: {file_info['file_size_kb']} KB\n"
#                 f" 생성: {file_info['created_at']}\n"
#                 f" 수정: {file_info['modified_at']}"
#             )
#             self.file_loader.open_file(file_info["file_path"])


# # 실행
# def run_gui():
#     """파일 로더 GUI 실행"""
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     window = FileLoaderGUI("/home/rapa/test_maya")  # 프로젝트 경로 변경 필요
#     window.show()
#     sys.exit(app.exec())


# # GUI 실행
# if __name__ == "__main__":
#     run_gui()


"""
import랑 reference형태로 scene에 들어올 수 있는 기능
- import : 모든 툴, lib에 있는 에셋, 클립 모두 해당
- ref : maya만 한정, lib 에셋에서만 사용될 기능 (+ 에셋을 클릭한 상태에서는 ref 버튼이 뜨게..?)

"""                                
  


# import os
# import time
# import subprocess
# from PySide6 import QtWidgets, QtGui, QtCore


# class FileLoader:
#     """Maya, Nuke에서 생성된 파일을 불러오고 정보를 표시하는 클래스"""

#     def __init__(self, project_directory):
#         """
#         프로젝트 폴더 경로 설정
#         :param project_directory: 파일이 저장된 프로젝트 디렉토리
#         """
#         self.project_directory = project_directory

#     def get_file_info(self, file_path):
#         """
#         파일의 정보를 가져오는 함수
#         :param file_path: 파일 경로
#         :return: 파일 정보 (딕셔너리)
#         """
#         try:
#             file_stats = os.stat(file_path)
#             return {
#                 "file_name": os.path.basename(file_path),
#                 "file_size_kb": round(file_stats.st_size / 1024, 2),
#                 "created_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_ctime)),
#                 "modified_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime)),
#                 "file_path": file_path
#             }
#         except Exception as e:
#             print(f"⚠️ 파일 정보를 가져오는 중 오류 발생: {e}")
#             return None

#     def get_maya_nuke_files(self, sort_by="created_at"):
#         """
#         Maya (`.ma`, `.mb`), Nuke (`.nk`) 파일을 불러와 정렬
#         :param sort_by: 정렬 기준 (created_at, modified_at, file_size_kb)
#         :return: 파일 목록 (리스트)
#         """
#         if not os.path.exists(self.project_directory):
#             print(" 프로젝트 디렉토리가 존재하지 않습니다!")
#             return []

#         maya_nuke_files = []

#         for root, _, files in os.walk(self.project_directory):
#             for file_name in files:
#                 if file_name.endswith((".ma", ".mb", ".nk")):
#                     file_path = os.path.join(root, file_name)
#                     file_info = self.get_file_info(file_path)
#                     if file_info:
#                         maya_nuke_files.append(file_info)

#         sorted_files = sorted(maya_nuke_files, key=lambda x: x.get(sort_by, ""), reverse=False)

#         return sorted_files

#     def open_file(self, file_path):
#         """
#         Maya 또는 Nuke에서 파일을 열기
#         :param file_path: 실행할 파일 경로
#         """
#         if not os.path.exists(file_path):
#             print(f" 파일이 존재하지 않습니다: {file_path}")
#             return

#         if file_path.endswith((".ma", ".mb")):
#             self.open_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.open_nuke(file_path)
#         else:
#             print(f"⚠️ 지원되지 않는 파일 형식: {file_path}")

#     def open_maya(self, file_path):
#         """Maya에서 파일 열기"""
#         try:
#             subprocess.Popen(["maya", "-file", file_path], shell=True)
#             print(f" Maya에서 파일을 실행합니다: {file_path}")
#         except Exception as e:
#             print(f" Maya 실행 오류: {e}")

#     def open_nuke(self, file_path):
#         """Nuke에서 파일 열기"""
#         try:
#             subprocess.Popen(["nuke", file_path], shell=True)
#             print(f" Nuke에서 파일을 실행합니다: {file_path}")
#         except Exception as e:
#             print(f" Nuke 실행 오류: {e}")

#     def import_file(self, file_path):
#         """
#         Maya 또는 Nuke에서 파일을 Import
#         :param file_path: Import할 파일 경로
#         """
#         if not os.path.exists(file_path):
#             print(f" 파일이 존재하지 않습니다: {file_path}")
#             return

#         if file_path.endswith((".ma", ".mb")):
#             self.import_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.import_nuke(file_path)
#         else:
#             print(f"⚠️ 지원되지 않는 파일 형식: {file_path}")

#     def import_maya(self, file_path):
#         """Maya에서 파일 Import"""
#         try:
#             import maya.cmds as cmds
#             cmds.file(file_path, i=True)  # Import 옵션 사용
#             print(f" Maya에서 파일을 Import 완료: {file_path}")
#         except Exception as e:
#             print(f" Maya Import 오류: {e}")

#     def import_nuke(self, file_path):
#         """Nuke에서 파일 Import"""
#         try:
#             import nuke
#             nuke.scriptReadFile(file_path)
#             print(f" Nuke에서 파일을 Import 완료: {file_path}")
#         except Exception as e:
#             print(f" Nuke Import 오류: {e}")


# class FileLoaderGUI(QtWidgets.QMainWindow):
#     """Maya, Nuke 파일을 불러오는 GUI"""

#     def __init__(self, project_directory):
#         super().__init__()
#         self.setWindowTitle("Maya & Nuke File Loader")
#         self.setGeometry(100, 100, 900, 600)
#         self.project_directory = project_directory
#         self.file_loader = FileLoader(project_directory)
#         self.initUI()

#     def initUI(self):
#         """GUI 레이아웃 설정"""
#         main_widget = QtWidgets.QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QtWidgets.QVBoxLayout(main_widget)

#         # 파일 리스트
#         self.file_list = QtWidgets.QListWidget()
#         self.file_list.itemDoubleClicked.connect(self.open_selected_file)
#         layout.addWidget(self.file_list)

#         # 파일 정보 표시
#         self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
#         layout.addWidget(self.file_info_label)

#         # 버튼 영역
#         button_layout = QtWidgets.QHBoxLayout()
#         self.refresh_button = QtWidgets.QPushButton(" 새로고침")
#         self.refresh_button.clicked.connect(self.load_files)
#         button_layout.addWidget(self.refresh_button)

#         self.import_button = QtWidgets.QPushButton(" Import 파일")
#         self.import_button.clicked.connect(self.import_selected_file)
#         button_layout.addWidget(self.import_button)

#         layout.addLayout(button_layout)

#         # 파일 로드
#         self.load_files()

#     def load_files(self):
#         """Maya, Nuke 파일 목록을 가져와 리스트에 표시"""
#         self.file_list.clear()
#         files = self.file_loader.get_maya_nuke_files()

#         if not files:
#             self.file_info_label.setText(" 불러올 파일이 없습니다.")
#             return

#         for file in files:
#             item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
#             item.setData(QtCore.Qt.UserRole, file)
#             self.file_list.addItem(item)

#     def open_selected_file(self, item):
#         """리스트에서 선택한 파일을 열기"""
#         file_info = item.data(QtCore.Qt.UserRole)
#         if file_info:
#             self.file_info_label.setText(
#                 f" {file_info['file_name']}\n"
#                 f" 위치: {file_info['file_path']}\n"
#                 f" 크기: {file_info['file_size_kb']} KB\n"
#                 f" 생성: {file_info['created_at']}\n"
#                 f" 수정: {file_info['modified_at']}"
#             )
#             self.file_loader.open_file(file_info["file_path"])

#     def import_selected_file(self):
#         """리스트에서 선택한 파일을 Import"""
#         selected_item = self.file_list.currentItem()
#         if selected_item:
#             file_info = selected_item.data(QtCore.Qt.UserRole)
#             if file_info:
#                 self.file_loader.import_file(file_info["file_path"])


# # 실행
# def run_gui():
#     """파일 로더 GUI 실행"""
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     window = FileLoaderGUI("/home/rapa/test_maya")  # 프로젝트 경로 변경 필요
#     window.show()
#     sys.exit(app.exec())


# # GUI 실행
# if __name__ == "__main__":
#     run_gui()



#######################################################################################################################################################



# import os
# import time
# import subprocess
# from shotgun_api3 import Shotgun
# from PySide6 import QtWidgets, QtGui, QtCore


# class ShotGridConnector:
#     """ShotGrid API와 연동하여 데이터를 가져오는 클래스"""

#     def __init__(self):
#         """ShotGrid API 연결"""
#         self.SG_URL = "https://minseo.shotgrid.autodesk.com"
#         self.SCRIPT_NAME = "Viper"
#         self.API_KEY = "jvceqpsfqvbl1azzcns?haksI"  # API 키 가져오기
#         self.sg = Shotgun(self.SG_URL, self.SCRIPT_NAME, self.API_KEY)
#         self.user_data = None  # 로그인한 사용자 정보 저장

#     def login_user(self, username):
#         """ShotGrid에서 로그인한 사용자 정보를 가져오기"""
#         filters = [["login", "is", username]]
#         fields = ["id", "name", "email"]
#         user = self.sg.find_one("HumanUser", filters, fields)

#         if user:
#             self.user_data = user
#             return user
#         else:
#             return {"error": "User not found"}

#     def get_user_files(self):
#         """현재 로그인한 사용자에게 할당된 파일 목록을 가져옴"""
#         if not self.user_data:
#             return {"error": "User not authenticated"}

#         user_id = self.user_data["id"]
#         filters = [["created_by", "is", {"type": "HumanUser", "id": user_id}]]
#         fields = ["id", "code", "sg_path", "created_at"]

#         files = self.sg.find("Version", filters, fields) or []
#         file_list = []

#         for file in files:
#             file_path = file.get("sg_path", None)  # ShotGrid에 등록된 파일 경로
#             if file_path and os.path.exists(file_path):
#                 file_list.append({
#                     "file_name": file["code"],
#                     "file_path": file_path,
#                     "created_at": file.get("created_at", "N/A")
#                 })

#         return sorted(file_list, key=lambda x: x["created_at"], reverse=True)


# class FileLoaderGUI(QtWidgets.QMainWindow):
#     """ShotGrid에서 파일을 불러오는 GUI"""

#     def __init__(self, sg_connector):
#         super().__init__()
#         self.setWindowTitle("ShotGrid File Loader")
#         self.setGeometry(100, 100, 900, 600)
#         self.sg_connector = sg_connector
#         self.initUI()

#     def initUI(self):
#         """GUI 레이아웃 설정"""
#         main_widget = QtWidgets.QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QtWidgets.QVBoxLayout(main_widget)

#         # 파일 리스트
#         self.file_list = QtWidgets.QListWidget()
#         self.file_list.itemDoubleClicked.connect(self.open_selected_file)
#         layout.addWidget(self.file_list)

#         # 파일 정보 표시
#         self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
#         layout.addWidget(self.file_info_label)

#         # 버튼 영역
#         button_layout = QtWidgets.QHBoxLayout()
#         self.refresh_button = QtWidgets.QPushButton(" 새로고침")
#         self.refresh_button.clicked.connect(self.load_files)
#         button_layout.addWidget(self.refresh_button)

#         layout.addLayout(button_layout)

#         # 파일 로드
#         self.load_files()

#     def load_files(self):
#         """ShotGrid에서 파일 목록을 가져와 리스트에 표시"""
#         self.file_list.clear()
#         files = self.sg_connector.get_user_files()

#         if not files:
#             self.file_info_label.setText(" 불러올 파일이 없습니다.")
#             return

#         for file in files:
#             item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
#             item.setData(QtCore.Qt.UserRole, file)
#             self.file_list.addItem(item)

#     def open_selected_file(self, item):
#         """리스트에서 선택한 파일을 열기"""
#         file_info = item.data(QtCore.Qt.UserRole)
#         if file_info:
#             self.file_info_label.setText(
#                 f" {file_info['file_name']}\n"
#                 f" 위치: {file_info['file_path']}\n"
#                 f" 생성: {file_info['created_at']}"
#             )
#             self.open_file(file_info["file_path"])

#     def open_file(self, file_path):
#         """Maya 또는 Nuke에서 파일을 열기"""
#         if not os.path.exists(file_path):
#             print(f" 파일이 존재하지 않습니다: {file_path}")
#             return

#         if file_path.endswith((".ma", ".mb")):
#             self.open_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.open_nuke(file_path)
#         else:
#             print(f" 지원되지 않는 파일 형식: {file_path}")

#     def open_maya(self, file_path):
#         """Maya에서 파일 열기"""
#         try:
#             subprocess.Popen(["maya", "-file", file_path], shell=True)
#             print(f" Maya에서 파일을 실행합니다: {file_path}")
#         except Exception as e:
#             print(f" Maya 실행 오류: {e}")

#     def open_nuke(self, file_path):
#         """Nuke에서 파일 열기"""
#         try:
#             subprocess.Popen(["nuke", file_path], shell=True)
#             print(f" Nuke에서 파일을 실행합니다: {file_path}")
#         except Exception as e:
#             print(f" Nuke 실행 오류: {e}")


# # 실행
# def run_gui():
#     """파일 로더 GUI 실행"""
#     import sys
#     app = QtWidgets.QApplication(sys.argv)

#     # ShotGrid 연결
#     sg_connector = ShotGridConnector()
#     username = "owlgrowl0v0@gmail.com"  # 사용자 로그인
#     user_data = sg_connector.login_user(username)

#     if "error" in user_data:
#         print(user_data["error"])
#         return

#     window = FileLoaderGUI(sg_connector)
#     window.show()
#     sys.exit(app.exec())


# # GUI 실행
# if __name__ == "__main__":
#     run_gui()



####################################################################################################################################################



import os
import time
import subprocess
from shotgun_api3 import Shotgun
from PySide6 import QtWidgets, QtGui, QtCore


class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오는 클래스"""

    def __init__(self):
        """ShotGrid API 연결"""
        self.SG_URL = "https://minseo.shotgrid.autodesk.com"
        self.SCRIPT_NAME = "Viper"
        self.API_KEY = "jvceqpsfqvbl1azzcns?haksI"  # API 키 가져오기
        self.sg = Shotgun(self.SG_URL, self.SCRIPT_NAME, self.API_KEY)
        self.user_data = None  # 로그인한 사용자 정보 저장

    def login_user(self, username):
        """ShotGrid에서 로그인한 사용자 정보를 가져오기"""
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = self.sg.find_one("HumanUser", filters, fields)

        if user:
            self.user_data = user
            return user
        else:
            return {"error": "User not found"}

    def get_user_files(self):
        """현재 로그인한 사용자에게 할당된 파일 목록을 가져옴"""
        if not self.user_data:
            return {"error": "User not authenticated"}

        user_id = self.user_data["id"]
        filters = [["created_by", "is", {"type": "HumanUser", "id": user_id}]]
        fields = ["id", "code", "sg_path", "created_at"]

        files = self.sg.find("Version", filters, fields) or []
        file_list = []

        for file in files:
            file_path = file.get("sg_path", None)
            if file_path and os.path.exists(file_path):
                file_list.append({
                    "file_name": file["code"],
                    "file_path": file_path,
                    "created_at": file.get("created_at", "N/A")
                })

        return sorted(file_list, key=lambda x: x["created_at"], reverse=True)


class FileLoaderGUI(QtWidgets.QMainWindow):
    """ShotGrid에서 파일을 불러오는 GUI"""

    def __init__(self, sg_connector):
        super().__init__()
        self.setWindowTitle("ShotGrid File Loader")
        self.setGeometry(100, 100, 900, 600)
        self.sg_connector = sg_connector
        self.initUI()

    def initUI(self):
        """GUI 레이아웃 설정"""
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        # 파일 리스트
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_selected_file)
        layout.addWidget(self.file_list)

        # 파일 정보 표시
        self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
        layout.addWidget(self.file_info_label)

        # 버튼 영역
        button_layout = QtWidgets.QHBoxLayout()
        self.refresh_button = QtWidgets.QPushButton("🔄 새로고침")
        self.refresh_button.clicked.connect(self.load_files)
        button_layout.addWidget(self.refresh_button)

        self.import_button = QtWidgets.QPushButton("📥 Import 파일")
        self.import_button.clicked.connect(self.import_selected_file)
        button_layout.addWidget(self.import_button)

        self.reference_button = QtWidgets.QPushButton("🔗 Reference 파일")
        self.reference_button.clicked.connect(self.reference_selected_file)
        button_layout.addWidget(self.reference_button)

        layout.addLayout(button_layout)

        # 파일 로드
        self.load_files()

    def load_files(self):
        """ShotGrid에서 파일 목록을 가져와 리스트에 표시"""
        self.file_list.clear()
        files = self.sg_connector.get_user_files()

        if not files:
            self.file_info_label.setText("📂 불러올 파일이 없습니다.")
            return

        for file in files:
            item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
            item.setData(QtCore.Qt.UserRole, file)
            self.file_list.addItem(item)

    def open_selected_file(self, item):
        """리스트에서 선택한 파일을 열기"""
        file_info = item.data(QtCore.Qt.UserRole)
        if file_info:
            self.file_info_label.setText(
                f"📄 {file_info['file_name']}\n"
                f"📍 위치: {file_info['file_path']}\n"
                f"📅 생성: {file_info['created_at']}"
            )
            self.open_file(file_info["file_path"])

    def open_file(self, file_path):
        """Maya 또는 Nuke에서 파일을 열기"""
        if not os.path.exists(file_path):
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")
            return

        if file_path.endswith((".ma", ".mb")):
            self.open_maya(file_path)
        elif file_path.endswith(".nk"):
            self.open_nuke(file_path)
        else:
            print(f"⚠️ 지원되지 않는 파일 형식: {file_path}")

    def open_maya(self, file_path):
        """Maya에서 파일 열기"""
        try:
            subprocess.Popen(["maya", "-file", file_path], shell=True)
            print(f"✅ Maya에서 파일을 실행합니다: {file_path}")
        except Exception as e:
            print(f"❌ Maya 실행 오류: {e}")

    def open_nuke(self, file_path):
        """Nuke에서 파일 열기"""
        try:
            subprocess.Popen(["nuke", file_path], shell=True)
            print(f"✅ Nuke에서 파일을 실행합니다: {file_path}")
        except Exception as e:
            print(f"❌ Nuke 실행 오류: {e}")

    def import_selected_file(self):
        """리스트에서 선택한 파일을 Import"""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_info = selected_item.data(QtCore.Qt.UserRole)
            if file_info:
                self.import_file(file_info["file_path"])

    def import_file(self, file_path):
        """Maya 또는 Nuke에서 파일을 Import"""
        if not os.path.exists(file_path):
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")
            return

        if file_path.endswith((".ma", ".mb")):
            self.import_maya(file_path)
        elif file_path.endswith(".nk"):
            self.import_nuke(file_path)
        else:
            print(f"⚠️ 지원되지 않는 파일 형식: {file_path}")

    def import_maya(self, file_path):
        """Maya에서 파일 Import"""
        try:
            import maya.cmds as cmds
            cmds.file(file_path, i=True)  # Import 옵션
            print(f"✅ Maya에서 파일을 Import 완료: {file_path}")
        except Exception as e:
            print(f"❌ Maya Import 오류: {e}")

    def import_nuke(self, file_path):
        """Nuke에서 파일 Import"""
        try:
            import nuke
            nuke.scriptReadFile(file_path)
            print(f"✅ Nuke에서 파일을 Import 완료: {file_path}")
        except Exception as e:
            print(f"❌ Nuke Import 오류: {e}")

    def reference_selected_file(self):
        """리스트에서 선택한 파일을 Reference 형태로 추가"""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_info = selected_item.data(QtCore.Qt.UserRole)
            if file_info:
                self.reference_maya(file_info["file_path"])

    def reference_maya(self, file_path):
        """Maya에서 파일을 Reference 형태로 추가"""
        try:
            import maya.cmds as cmds
            cmds.file(file_path, reference=True)  # Reference 옵션
            print(f"🔗 Maya에서 파일을 Reference로 추가 완료: {file_path}")
        except Exception as e:
            print(f"❌ Maya Reference 오류: {e}")


# 실행
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sg_connector = ShotGridConnector()
    sg_connector.login_user("owlgrowl0v0@gmail.com")
    window = FileLoaderGUI(sg_connector)
    window.show()
    sys.exit(app.exec())
