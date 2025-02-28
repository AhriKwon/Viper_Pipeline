



"""
user가 마야나 누크에서 작업중인 상태에서 loader를 실행하고 loader의 import 버튼을 누르면 user가 선택한 파일을 불러와서 
현재 작업하고 있는 마야나 누크 창에 파일이 열리도록 하는 함수 


로그인 task id해도 work path로 연결되도록 하는 함수

"""

"""
경로 : /nas/show/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/{TASK}/work/maya/scenes/{ASSET_NAME}_{TASK}_v001.{EXT}
      /nas/show/Viper/assets/Character/Hero_Character/MDL/work/maya/scenes/Hero_Character_MDL_v001.ma
    
    
    
    
경로 : /nas/show/{PROJECT}/seq/{SEQ}/{SHOT}/{TASK}/work/maya/scenes/{SHOT}_{TASK}_v001.{EXT}
      /nas/show/Viper/seq/SEQ001/SH010/ANM/work/maya/scenes/SEQ001_SH010_Animation_v001.mov
    
    
"""

            
##########################################################################################################################
   
# import os
# import sys
# import subprocess
# from PySide6 import QtWidgets, QtGui, QtCore

# #  ShotGrid API 파일 가져오기
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
# from shotgrid_connector import ShotGridConnector


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
#         self.user_label = QtWidgets.QLabel(f" 사용자 ID: {self.user_id}")
#         layout.addWidget(self.user_label)

#         # 파일 경로 입력창
#         self.file_path_input = QtWidgets.QLineEdit()
#         self.file_path_input.setPlaceholderText(" 파일 경로를 입력하세요.")
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

#         self.import_button = QtWidgets.QPushButton("파일 Import")
#         self.import_button.clicked.connect(self.import_file)
#         button_layout.addWidget(self.import_button)

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

#         # 경로를 절대 경로로 변환
#         file_path = os.path.abspath(file_path)

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
#             maya_command = f'"{maya_executable}" -command "file -o \\"{file_path}\\";"'
#             subprocess.Popen(maya_command, shell=True)
#             print(f" Maya에서 파일을 불러왔습니다: {file_path}")
#         else:
#             QtWidgets.QMessageBox.warning(self, "오류", "Maya 실행 파일을 찾을 수 없습니다.")

#     def launch_nuke(self, file_path):
#         """Nuke 실행 후 파일 열기"""
#         nuke_executable = self.find_nuke_path()
#         if nuke_executable:
#                # 3가지 실행 방식 시도
#             try:
#                 print("실행 방식 1: Nuke 실행 후 파일 전달")
#                 subprocess.run([nuke_executable, file_path], check=True)
#             except:
#                 # try:
#                 #     print("실행 방식 2: Python 스크립트 실행 방식")
#                 #     subprocess.run([nuke_executable, "-t", "-c", f'import nuke; nuke.scriptOpen("{file_path}")'], check=True)
#                 # except:
#                     # try:
#                     #     print("실행 방식 3: GUI 실행 후 파일 열기")
#                     #     subprocess.run([nuke_executable, "-i", file_path], check=True)
#                     # except:
#                         QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행에 실패했습니다.")
            
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
#         possible_paths = ["/usr/local/Nuke15.1v5/Nuke15.1"]
#         for path in possible_paths:
#             if os.path.exists(path):
#                 return path
#         return None


#     def import_file(self):
#         """현재 실행 중인 Maya 또는 Nuke에서 선택한 파일을 Import"""
#         file_path = self.file_path_input.text().strip()

#         if not file_path or not os.path.exists(file_path):
#             QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
#             return

#         if file_path.endswith((".ma", ".mb", ".abc", ".obj")):
#             self.import_maya(file_path)
#         elif file_path.endswith(".nk"):
#             self.import_nuke(file_path)
#         else:
#             QtWidgets.QMessageBox.warning(self, "오류", "지원되지 않는 파일 형식입니다.")

#     def import_maya(self, file_path):
#         """현재 실행 중인 Maya에서 파일 Import"""
#         if self.is_maya_running():
#             try:
#                 import maya.cmds as cmds
#                 cmds.file(file_path, i=True)
#                 print(f"✅ 현재 실행 중인 Maya에서 파일을 Import 했습니다: {file_path}")
#             except ImportError:
#                 print("⚠ Maya 실행 중이지만 Python 환경 오류 발생! `cmdPort`로 Import 시도.")
#                 self.import_with_cmdport(file_path)
#         else:
#             print("⚠ Maya가 실행 중이 아님. mayapy를 사용하여 Import 진행합니다.")
#             self.import_with_mayapy(file_path)

#     def is_maya_running(self):
#         """현재 Maya가 실행 중인지 확인"""
#         try:
#             result = subprocess.run(["pgrep", "-f", "maya"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#             return bool(result.stdout.strip())
#         except Exception as e:
#             print(f"⚠ Maya 실행 여부 확인 중 오류 발생: {e}")
#             return False

#     def import_with_cmdport(self, file_path):
#         """Maya가 실행 중일 때 `cmdPort`를 이용하여 Import"""
#         try:
#             import socket
#             maya_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             maya_socket.connect(("127.0.0.1", 2222))  # Maya에서 `cmdPort` 활성화 필요
#             command = f'file -import "{file_path}";\n'
#             maya_socket.send(command.encode())
#             maya_socket.close()
#             print(f"✅ Maya `cmdPort`를 통해 파일을 Import 했습니다: {file_path}")
#         except Exception as e:
#             print(f"❌ `cmdPort` Import 실패: {e}")

#     def import_with_mayapy(self, file_path):
#         """Maya가 실행 중이 아닐 때 `mayapy`를 사용하여 Import"""
#         mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"
#         if not os.path.exists(mayapy_path):
#             QtWidgets.QMessageBox.warning(self, "오류", "Maya Python 실행 파일(mayapy)을 찾을 수 없습니다.")
#             return

#         import_script = f'''
# import maya.standalone
# maya.standalone.initialize()
# import maya.cmds as cmds
# cmds.file("{file_path}", i=True)
# print("✅ Maya에서 파일을 Import 했습니다: {file_path}")
# '''
#         subprocess.run([mayapy_path, "-c", import_script], check=True)

#     def import_nuke(self, file_path):
#         """현재 실행 중인 Nuke에서 파일 Import"""
#         try:
#             import nuke
#             nuke.nodePaste(file_path)
#             print(f"✅ Nuke에서 파일을 Import 했습니다: {file_path}")
#         except ImportError:
#             QtWidgets.QMessageBox.warning(self, "오류", "Nuke가 실행 중인지 확인하세요.")

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

        self.import_button = QtWidgets.QPushButton("파일 Import")
        self.import_button.clicked.connect(self.import_file)
        button_layout.addWidget(self.import_button)

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

        # 경로를 절대 경로로 변환
        file_path = os.path.abspath(file_path)

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
            maya_command = f'"{maya_executable}" -command "file -o \\"{file_path}\\";"'
            subprocess.Popen(maya_command, shell=True)
            print(f" Maya에서 파일을 불러왔습니다: {file_path}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Maya 실행 파일을 찾을 수 없습니다.")

    def launch_nuke(self, file_path):
        """Nuke 실행 후 파일 열기"""
        nuke_executable = self.find_nuke_path()
        if nuke_executable:
               # 3가지 실행 방식 시도
            try:
                print("실행 방식 1: Nuke 실행 후 파일 전달")
                subprocess.run([nuke_executable, file_path], check=True)
            except:
                # try:
                #     print("실행 방식 2: Python 스크립트 실행 방식")
                #     subprocess.run([nuke_executable, "-t", "-c", f'import nuke; nuke.scriptOpen("{file_path}")'], check=True)
                # except:
                    # try:
                    #     print("실행 방식 3: GUI 실행 후 파일 열기")
                    #     subprocess.run([nuke_executable, "-i", file_path], check=True)
                    # except:
                        QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행에 실패했습니다.")
            
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
        possible_paths = ["/usr/local/Nuke15.1v5/Nuke15.1"]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None


    def import_file(self):
        """현재 실행 중인 Maya 또는 Nuke에서 선택한 파일을 Import"""
        file_path = self.file_path_input.text().strip()

        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
            return

        if file_path.endswith((".ma", ".mb", ".abc", ".obj")):
            self.import_maya(file_path)
        elif file_path.endswith(".nk"):
            self.import_nuke(file_path)
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "지원되지 않는 파일 형식입니다.")

    def import_maya(self, file_path):
        """현재 실행 중인 Maya에서 파일 Import"""
        if self.is_maya_running():
            try:
                import maya.cmds as cmds
                cmds.file(file_path, i=True)
                print(f"✅ 현재 실행 중인 Maya에서 파일을 Import 했습니다: {file_path}")
            except ImportError:
                print("⚠ Maya 실행 중이지만 Python 환경 오류 발생! `cmdPort`로 Import 시도.")
                self.import_with_cmdport(file_path)
        else:
            print("⚠ Maya가 실행 중이 아님. mayapy를 사용하여 Import 진행합니다.")
            self.import_with_mayapy(file_path)

    def is_maya_running(self):
        """현재 Maya가 실행 중인지 확인"""
        try:
            result = subprocess.run(["pgrep", "-f", "maya"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"⚠ Maya 실행 여부 확인 중 오류 발생: {e}")
            return False

    def import_with_cmdport(self, file_path):
        """Maya가 실행 중일 때 `cmdPort`를 이용하여 Import"""
        try:
            import socket
            maya_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            maya_socket.connect(("127.0.0.1", 2222))  # Maya에서 `cmdPort` 활성화 필요
            command = f'file -import "{file_path}";\n'
            maya_socket.send(command.encode())
            maya_socket.close()
            print(f"✅ Maya `cmdPort`를 통해 파일을 Import 했습니다: {file_path}")
        except Exception as e:
            print(f"❌ `cmdPort` Import 실패: {e}")

    def import_with_mayapy(self, file_path):
        """Maya가 실행 중이 아닐 때 `mayapy`를 사용하여 Import"""
        mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"
        if not os.path.exists(mayapy_path):
            QtWidgets.QMessageBox.warning(self, "오류", "Maya Python 실행 파일(mayapy)을 찾을 수 없습니다.")
            return

        import_script = f'''
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
cmds.file("{file_path}", i=True)
print("✅ Maya에서 파일을 Import 했습니다: {file_path}")
'''
        subprocess.run([mayapy_path, "-c", import_script], check=True)

    def import_nuke(self, file_path):
        """현재 실행 중인 Nuke에서 파일 Import"""
        try:
            import nuke
            nuke.nodePaste(file_path)
            print(f"✅ Nuke에서 파일을 Import 했습니다: {file_path}")
        except ImportError:
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke가 실행 중인지 확인하세요.")

# 실행
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    user_id = 121  # 실제 사용자 ID
    window = FileLoaderGUI(user_id)
    window.show()
    sys.exit(app.exec())

    