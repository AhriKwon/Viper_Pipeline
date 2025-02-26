



"""
import랑 reference형태로 scene에 들어올 수 있는 기능
- import : 모든 툴, lib에 있는 에셋, 클립 모두 해당
- ref : maya만 한정, lib 에셋에서만 사용될 기능 (+ 에셋을 클릭한 상태에서는 ref 버튼이 뜨게..?)

"""                                
  



# import os
# import time
# import subprocess
# from shotgun_api3 import Shotgun
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
#     sg = Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

#     @staticmethod
#     def get_user_tasks(user_id):
#         """현재 사용자의 Task 목록을 가져옴"""
#         tasks = ShotGridConnector.sg.find(
#             "Task",
#             [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
#             ["id", "content", "sg_status_list", "entity"]
#         )
#         return tasks

#     @staticmethod
#     def get_published_files_for_task(task_id):
#         """특정 Task에 연결된 퍼블리시 파일을 불러옴"""
#         filters = [["task", "is", {"type": "Task", "id": task_id}]]
#         fields = ["id", "code", "path", "description", "image", "created_at"]
#         order = [{"field_name": "created_at", "direction": "desc"}]

#         publishes = ShotGridConnector.sg.find("PublishedFile", filters, fields, order)
#         return [
#             {
#                 'id': p['id'],
#                 'file_name': p['code'],
#                 'file_path': p['path']['local_path'],
#                 'description': p['description'],
#                 'thumbnail': p['image'],
#                 'created_at': p['created_at']
#             } 
#             for p in publishes if 'path' in p and p['path']
#         ]


# class FileLoaderGUI(QtWidgets.QMainWindow):
#     """ShotGrid에서 퍼블리시된 파일을 불러오는 GUI"""

#     def __init__(self, sg_connector, user_id):
#         super().__init__()
#         self.setWindowTitle("ShotGrid File Loader")
#         self.setGeometry(100, 100, 900, 600)
#         self.sg_connector = sg_connector
#         self.user_id = user_id
#         self.initUI()

#     def initUI(self):
#         """GUI 레이아웃 설정"""
#         main_widget = QtWidgets.QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QtWidgets.QVBoxLayout(main_widget)

#         # Task 목록
#         self.task_list = QtWidgets.QListWidget()
#         self.task_list.itemClicked.connect(self.load_published_files)
#         layout.addWidget(self.task_list)

#         # 파일 목록
#         self.file_list = QtWidgets.QListWidget()
#         self.file_list.itemDoubleClicked.connect(self.open_selected_file)
#         layout.addWidget(self.file_list)

#         # 파일 정보 표시
#         self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
#         layout.addWidget(self.file_info_label)

#         # 버튼 영역
#         button_layout = QtWidgets.QHBoxLayout()
#         self.refresh_button = QtWidgets.QPushButton("새로고침")
#         self.refresh_button.clicked.connect(self.load_tasks)
#         button_layout.addWidget(self.refresh_button)

#         self.import_button = QtWidgets.QPushButton("Import 파일")
#         self.import_button.clicked.connect(self.import_selected_file)
#         button_layout.addWidget(self.import_button)

#         self.reference_button = QtWidgets.QPushButton("Reference 파일")
#         self.reference_button.clicked.connect(self.reference_selected_file)
#         button_layout.addWidget(self.reference_button)

#         layout.addLayout(button_layout)

#         # Task 로드
#         self.load_tasks()

#     def load_tasks(self):
#         """사용자의 Task 목록을 불러와 리스트에 표시"""
#         self.task_list.clear()
#         tasks = self.sg_connector.get_user_tasks(self.user_id)

#         if not tasks:
#             self.task_list.addItem("불러올 Task가 없습니다.")
#             return

#         for task in tasks:
#             item = QtWidgets.QListWidgetItem(f"{task['content']} (ID: {task['id']})")
#             item.setData(QtCore.Qt.UserRole, task['id'])
#             self.task_list.addItem(item)

#     def load_published_files(self, item):
#         """선택한 Task의 퍼블리시된 파일을 불러옴"""
#         task_id = item.data(QtCore.Qt.UserRole)
#         self.file_list.clear()
#         files = self.sg_connector.get_published_files_for_task(task_id)

#         if not files:
#             self.file_info_label.setText("퍼블리시된 파일이 없습니다.")
#             return

#         for file in files:
#             list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
#             list_item.setData(QtCore.Qt.UserRole, file)
#             self.file_list.addItem(list_item)

#     def open_selected_file(self, item):
#         """리스트에서 선택한 파일을 실행"""
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
#         if file_path.endswith((".ma", ".mb")):
#             self.open_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.open_nuke(file_path)
#         else:
#             print(f"지원되지 않는 파일 형식: {file_path}")

#     def open_maya(self, file_path):
#         """Maya에서 파일 열기"""
#         import maya.cmds as cmds
#         cmds.file(file_path, open=True, force=True)
#         print(f"Maya에서 파일을 실행합니다: {file_path}")

#     def open_nuke(self, file_path):
#         """Nuke에서 파일 열기"""
#         import nuke
#         nuke.scriptOpen(file_path)
#         print(f"Nuke에서 파일을 실행합니다: {file_path}")

#     def import_selected_file(self):
#         """선택한 파일을 Import"""
#         selected_item = self.file_list.currentItem()
#         if selected_item:
#             file_info = selected_item.data(QtCore.Qt.UserRole)
#             self.import_file(file_info["file_path"])

#     def import_file(self, file_path):
#         """Maya 또는 Nuke에서 파일을 Import"""
#         if file_path.endswith((".ma", ".mb")):
#             import maya.cmds as cmds
#             cmds.file(file_path, i=True)
#             print(f"Maya에서 파일을 Import 완료: {file_path}")
#         elif file_path.endswith(".nk"):
#             import nuke
#             nuke.nodePaste(file_path)
#             print(f"Nuke에서 파일을 Import 완료: {file_path}")

#     def reference_selected_file(self):
#         """선택한 파일을 Reference"""
#         selected_item = self.file_list.currentItem()
#         if selected_item:
#             file_info = selected_item.data(QtCore.Qt.UserRole)
#             self.reference_maya(file_info["file_path"])

#     def reference_maya(self, file_path):
#         """Maya에서 파일을 Reference 형태로 추가"""
#         import maya.cmds as cmds
#         cmds.file(file_path, reference=True)
#         print(f"Maya에서 파일을 Reference로 추가 완료: {file_path}")


# # 실행
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     sg_connector = ShotGridConnector()
#     user_id = 121  # 실제 사용자 ID로 변경 필요
#     window = FileLoaderGUI(sg_connector, user_id)
#     window.show()
#     sys.exit(app.exec())
    


# ######################################################################################################################################################


import os
import subprocess
import sys
from shotgun_api3 import Shotgun
from PySide6 import QtWidgets, QtGui, QtCore

#  Maya 환경 변수 설정
# if "MAYA_LOCATION" not in os.environ:
#     os.environ["MAYA_LOCATION"] = "/usr/autodesk/maya2023"  # Maya 설치 경로
#     sys.path.append("/usr/autodesk/maya2023/bin")
#     sys.path.append("/usr/autodesk/maya2023/lib/python3.9/site-packages")

# try:
#     import maya.cmds as cmds
#     import maya.standalone
#     maya.standalone.initialize(name="python")  #  Maya 환경 초기화
# except ImportError:
#     print("Maya 모듈을 찾을 수 없습니다. Maya에서 실행해야 합니다.")

class ShotGridConnector:
    """ShotGrid API와 연동하여 퍼블리시된 파일을 가져오는 클래스"""
    SG_URL = "https://minseo.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper"
    API_KEY = "jvceqpsfqvbl1azzcns?haksI"

    sg = Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

    @staticmethod
    def get_user_tasks(user_id):
        """현재 사용자의 Task 목록을 가져옴"""
        tasks = ShotGridConnector.sg.find(
            "Task",
            [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
            ["id", "content", "sg_status_list", "entity"]
        )
        return tasks

    @staticmethod
    def get_published_files_for_task(task_id):
        """특정 Task에 연결된 퍼블리시 파일을 불러옴"""
        filters = [["task", "is", {"type": "Task", "id": task_id}]]
        fields = ["id", "code", "path", "description", "image", "created_at"]
        order = [{"field_name": "created_at", "direction": "desc"}]

        publishes = ShotGridConnector.sg.find("PublishedFile", filters, fields, order)
        return [
            {
                'id': p['id'],
                'file_name': p['code'],
                'file_path': p['path']['local_path'],
                'description': p['description'],
                'thumbnail': p['image'],
                'created_at': p['created_at']
            }
            for p in publishes if 'path' in p and p['path']
        ]


class FileLoaderGUI(QtWidgets.QMainWindow):
    """ShotGrid에서 퍼블리시된 파일을 불러오는 GUI"""

    def __init__(self, sg_connector, user_id):
        super().__init__()
        self.setWindowTitle("ShotGrid File Loader")
        self.setGeometry(100, 100, 900, 600)
        self.sg_connector = sg_connector
        self.user_id = user_id
        self.initUI()

    def initUI(self):
        """GUI 레이아웃 설정"""
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        # Task 목록
        self.task_list = QtWidgets.QListWidget()
        self.task_list.itemClicked.connect(self.load_published_files)
        layout.addWidget(self.task_list)

        # 파일 목록
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_selected_file)  #  함수가 존재해야 함
        layout.addWidget(self.file_list)

        # 파일 정보 표시
        self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
        layout.addWidget(self.file_info_label)

        # 버튼 영역
        button_layout = QtWidgets.QHBoxLayout()
        self.refresh_button = QtWidgets.QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.load_tasks)
        button_layout.addWidget(self.refresh_button)

        self.import_button = QtWidgets.QPushButton("Import 파일")
        self.import_button.clicked.connect(self.import_selected_file)
        button_layout.addWidget(self.import_button)

        self.reference_button = QtWidgets.QPushButton("Reference 파일")
        self.reference_button.clicked.connect(self.reference_selected_file)
        button_layout.addWidget(self.reference_button)

        layout.addLayout(button_layout)

        
        # Task 로드
        self.load_tasks()
        self.load_published_files()

    def load_tasks(self):
        """사용자의 Task 목록을 불러와 리스트에 표시"""
        self.task_list.clear()
        tasks = self.sg_connector.get_user_tasks(self.user_id)

        if not tasks:
            self.task_list.addItem("불러올 Task가 없습니다.")
            return

        for task in tasks:
            item = QtWidgets.QListWidgetItem(f"{task['content']} (ID: {task['id']})")
            item.setData(QtCore.Qt.UserRole, task['id'])
            self.task_list.addItem(item)

    def load_published_files(self):
        """퍼블리시된 파일을 불러옴"""
        self.file_list.clear()
        files = self.sg_connector.get_published_files_for_task(self.user_id)

        if not files:
            self.file_list.addItem("퍼블리시된 파일이 없습니다.")
            return

        for file in files:
            list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
            list_item.setData(QtCore.Qt.UserRole, file)
            self.file_list.addItem(list_item)

    def open_selected_file(self, item):
        """리스트에서 선택한 파일을 실행"""
        file_info = item.data(QtCore.Qt.UserRole)
        if file_info:
            self.file_info_label.setText(
                f" {file_info['file_name']}\n"
                f" 위치: {file_info['file_path']}\n"
                f" 생성: {file_info['created_at']}"
            )
            self.open_file(file_info["file_path"])

    def open_file(self, file_path):
        """Maya 또는 Nuke에서 파일을 열기"""
        if file_path.endswith((".ma", ".mb")):
            self.open_maya(file_path)
            
        elif file_path.endswith(".nk"):
            self.open_nuke(file_path)
            
        else:
            print(f"지원되지 않는 파일 형식: {file_path}")

    def open_maya(self, file_path):
        """Maya에서 파일 열기"""
        import maya.cmds as cmds
        cmds.file(file_path, open=True, force=True)
        print(f"Maya에서 파일을 실행합니다: {file_path}")

    def open_nuke(self, file_path):
        """Nuke에서 파일 열기"""
        import nuke
        nuke.scriptOpen(file_path)
        print(f"Nuke에서 파일을 실행합니다: {file_path}")

    def import_selected_file(self):
        """선택한 파일을 Import"""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_info = selected_item.data(QtCore.Qt.UserRole)
            self.import_file(file_info["file_path"])

    def import_file(self, file_path):
        """Maya 또는 Nuke에서 파일을 Import"""
        if file_path.endswith((".ma", ".mb")):
            import maya.cmds as cmds
            cmds.file(file_path, i=True)
            print(f"Maya에서 파일을 Import 완료: {file_path}")
        elif file_path.endswith(".abc"):
            cmds.file(file_path, i=True, type="Alembic")
            print(f"Alembic 파일 Import: {file_path}")
        elif file_path.endswith(".nk"):
            import nuke
            nuke.nodePaste(file_path)
            print(f"Nuke에서 파일을 Import 완료: {file_path}")
        else:
            print(f"지원되지 않는 파일 형식: {file_path}")


    def reference_selected_file(self):
        """선택한 파일을 Reference"""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_info = selected_item.data(QtCore.Qt.UserRole)
            self.reference_maya(file_info["file_path"])

    

    def reference_maya(self, file_path):
        """Maya에서 파일을 Reference 형태로 추가"""
        import maya.cmds as cmds
        cmds.file(file_path, reference=True)
        print(f"Maya에서 파일을 Reference로 추가 완료: {file_path}")

        if file_path.endswith(".abc"):
            cmds.AbcImport(file_path, mode="import")
            print(f"Alembic 파일 Reference 추가: {file_path}")
        elif file_path.endswith((".ma", ".mb")):
            cmds.file(file_path, reference=True)
            print(f"Maya 파일 Reference 추가: {file_path}")
        else:
            print(f"지원되지 않는 파일 형식: {file_path}")


# 실행
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sg_connector = ShotGridConnector()
    user_id = 121  # 실제 사용자 ID로 변경 필요
    window = FileLoaderGUI(sg_connector, user_id)
    window.show()
    sys.exit(app.exec())




    """
    경로 : /nas/show/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/{TASK}/work/maya/scenes/{ASSET_NAME}_{TASK}_v001.{EXT}
          /nas/show/Viper/assets/Character/Hero_Character/MDL/work/maya/scenes/Hero_Character_MDL_v001.ma
    
    
    
    
    경로 : /nas/show/{PROJECT}/seq/{SEQ}/{SHOT}/{TASK}/work/maya/scenes/{SHOT}_{TASK}_v001.{EXT}
          /nas/show/Viper/seq/SEQ001/SH010/ANM/work/maya/scenes/SEQ001_SH010_Animation_v001.mov
    
    
    
    """
