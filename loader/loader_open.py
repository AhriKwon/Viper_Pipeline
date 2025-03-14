



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
   
import os
import sys
import subprocess
import socket
from PySide6 import QtWidgets, QtGui, QtCore

#  ShotGrid API 파일 가져오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()


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

        self.reference_button = QtWidgets.QPushButton("파일 Reference")
        self.reference_button.clicked.connect(self.create_reference_file)
        button_layout.addWidget(self.reference_button)

        self.new_scene_button = QtWidgets.QPushButton("새 파일 Open")
        self.new_scene_button.clicked.connect(self.open_new_scene_maya)
        button_layout.addWidget(self.new_scene_button)

        layout.addLayout(button_layout)


        # 퍼블리시된 파일 불러오기
        self.load_published_files()
        

    def load_published_files(self):
        """샷그리드의 user에게 퍼블리시된 파일을 불러옴"""
        self.file_list.clear()
        tasks = manager.get_tasks_by_user(user_id)

        for task in tasks:
            files = manager.get_publishes_for_task(task["id"])
            if not files:
                continue

            for file in files:
                list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
                list_item.setData(QtCore.Qt.UserRole, file)
                self.file_list.addItem(list_item)


    def set_file_path(self):
        """사용자가 파일 경로를 직접 설정"""
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
        """Maya 실행 후 파일 열기 (환경 변수 추가)"""
        maya_executable = self.find_maya_path()
        if maya_executable:                       
            maya_command = f'bash -c "source /home/rapa/env/maya.env && {maya_executable} -command \\"file -o \\\\\\"{file_path}\\\\\\";\\""'
            subprocess.Popen(maya_command, shell=True)
            print(f"Maya에서 파일을 불러왔습니다: {file_path}")
        elif maya_executable:
            subprocess.Popen(["bash", "-c", f"source /home/rapa/env/maya.env && {maya_executable}"], shell=False)
            print(f"Maya 실행됨 (환경 변수 적용됨)")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Maya 실행 파일을 찾을 수 없습니다.")


    def open_new_scene_maya(self):
        """기존 Maya를 종료하지 않고 새로운 Maya 창을 띄움"""
        maya_executable = self.find_maya_path()
        if maya_executable:
            maya_command = f'bash -c "source /home/rapa/env/maya.env && {maya_executable}"'
            subprocess.Popen(maya_command, shell=True)
            QtWidgets.QMessageBox.information(self, "알림", "새로운 Maya 창이 열렸습니다.")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Maya 실행 파일을 찾을 수 없습니다.")




    # def launch_nuke(self, file_path):
    #     """Nuke 실행 후 파일 열기"""
    #     nuke_executable = self.find_nuke_path()
    #     if nuke_executable:
    #            # 3가지 실행 방식 시도
    #         try:
    #             print("실행 방식 1: Nuke 실행 후 파일 전달")
    #             subprocess.run([nuke_executable, file_path], check=True)
    #         except:
    #             # try:
    #             #     print("실행 방식 2: Python 스크립트 실행 방식")
    #             #     subprocess.run([nuke_executable, "-t", "-c", f'import nuke; nuke.scriptOpen("{file_path}")'], check=True)
    #             # except:
    #                 # try:
    #                 #     print("실행 방식 3: GUI 실행 후 파일 열기")
    #                 #     subprocess.run([nuke_executable, "-i", file_path], check=True)
    #                 # except:
    #                     QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행에 실패했습니다.")
            
    #     else:
    #         QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")


    def launch_nuke(self, file_path):
        """Nuke 실행 후 파일 열기"""
        nuke_executable = self.find_nuke_path()
        if nuke_executable:
            try:
                print("Nuke 실행 중...")

                # 기존 방식 → 응답이 멈출 가능성 있음
                # subprocess.run([nuke_executable, file_path], check=True)

                # 해결 방법: subprocess.Popen을 사용하여 비동기 실행
                subprocess.Popen([nuke_executable, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print(f"Nuke에서 파일을 실행했습니다: {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "오류", f"Nuke 실행 실패: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")


    def is_nuke_running(self):
        """현재 Nuke가 실행 중인지 확인"""
        try:
            result = subprocess.run(["pgrep", "-f", "Nuke"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Nuke 실행 확인 오류: {e}")
            return False

    def import_nuke(self, file_path):
        """현재 실행 중인 Nuke에 특정 파일 Import"""
        nuke_executable = "/usr/local/Nuke15.1v5/Nuke15.1"

        if self.is_nuke_running():
            try:
                import_script_path = "/home/rapa/import_nuke_script.py"

                with open(import_script_path, "w") as script_file:
                    script_file.write(f'''
import nuke
nuke.scriptReadFile("{file_path}")
print("Nuke에서 파일을 Import 했습니다: {file_path}")
''')

                env = os.environ.copy()
                env["NUKE_PATH"] = "/usr/local/Nuke15.1v5"
                env["LD_LIBRARY_PATH"] = "/usr/local/Nuke15.1v5/lib:" + env.get("LD_LIBRARY_PATH", "")

                subprocess.run([nuke_executable, "-t", import_script_path], check=True, env=env, capture_output=True, text=True)
                print(f"Nuke에서 파일을 Import 했습니다: {file_path}")

            except subprocess.CalledProcessError as e:
                print(f"Nuke 파일 Import 실패: {e}\n출력: {e.stdout}")
        else:
            print("실행 중인 Nuke가 없습니다. 새로 실행 후 Import 진행.")
            subprocess.Popen([nuke_executable, file_path])


    def find_maya_path(self):
        """Maya 실행 파일 경로 찾기"""
        possible_paths = ["/usr/autodesk/maya2023/bin/maya"]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def find_nuke_path(self):
        """Nuke 실행 파일 경로 찾기"""
        possible_paths = [
            "/usr/local/Nuke15.1v5/Nuke15.1",
            "/opt/Nuke15.1v5/Nuke15.1",
            "/usr/bin/Nuke15.1v5",
            "/usr/local/bin/Nuke15.1",
        ]
    
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        return None


    def import_file(self):
        """Maya에서 파일 Import"""
        file_path = self.file_path_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
            return

        if file_path.endswith((".ma", ".mb", ".abc", ".obj")):
            self.import_maya(file_path)
        elif file_path.endswith((".nk", ".mov")):
            self.import_nuke(file_path)
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "지원되지 않는 파일 형식입니다.")


    def create_reference_file(self):
        """Maya에서 Reference 추가"""
        file_path = self.file_path_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
            return
        self.create_reference_maya(file_path)            

    def is_maya_running(self):
        """Maya 실행 여부 확인"""
        try:
            result = subprocess.run(["pgrep", "-f", "maya"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Maya 실행 확인 오류: {e}")
            return False
        

    def is_cmd_port_open(self, port=7001):
        """cmdPort가 활성화되어 있는지 확인"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        
        if result == 0:
            print("cmdPort가 활성화됨")
            return True
        else:
            print("cmdPort가 비활성화됨")
            return False

    def enable_maya_cmd_port(self):
        """Maya에서 cmdPort 활성화"""
        print("Maya에서 cmdPort 활성화를 시도합니다...")
        mel_command = 'commandPort -name ":7001" -sourceType "python";'
        self.send_maya_command(mel_command)

    def send_maya_command(self, command):
        """Maya cmdPort를 통해 명령어 실행 후 응답 확인"""
        try:
            with socket.create_connection(("localhost", 7001), timeout=2) as sock:
                sock.sendall((command + "\n").encode("utf-8"))  # 문자열을 utf-8 바이트로 변환 후 전송

                # Maya의 응답을 읽어 디버깅 가능하도록 수정
                response = sock.recv(4096).decode("utf-8").strip()
                print(f"Maya 응답: {response}")

                print(f"Maya에서 명령 실행: {command}")
        except Exception as e:
            print(f"`cmdPort` Import 실패: {e}")
            QtWidgets.QMessageBox.warning(self, "오류", f"Maya `cmdPort` 연결 실패: {e}")


    def send_nuke_command(self, command):
        """실행 중인 Nuke에서 Python 명령 실행"""
        if self.is_nuke_running():
            try:
                subprocess.run(["nuke", "-t", "-c", command], check=True)
                print(f"Nuke 명령 실행: {command}")
            except Exception as e:
                print(f"Nuke 명령 실행 실패: {e}")
                QtWidgets.QMessageBox.warning(self, "오류", f"Nuke 명령 실행 실패: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke가 실행 중인지 확인하세요.")



    def import_maya(self, file_path):
        """Maya에서 Import 수행"""
        if self.is_maya_running():
            print("Maya 실행 중! `cmdPort` 방식으로 Import 시도.")
            if not self.is_cmd_port_open():
                print("`cmdPort`가 비활성화됨. MEL을 사용하여 활성화 시도.")
                self.enable_maya_cmd_port()

            if self.is_cmd_port_open():
                print("`cmdPort` 활성화됨! Maya에서 파일 Import 시도.")
                
                self.send_maya_command(f'''
import maya.cmds as cmds
import time
cmds.file("{file_path}", i=True)
cmds.evalDeferred(lambda: cmds.file("{file_path}", i=True))
cmds.file("{file_path}", i=True, namespace="imported")
cmds.evalDeferred(lambda: cmds.refresh())
time.sleep(2)  # Import가 적용될 시간을 줌
cmds.evalDeferred(lambda: cmds.file(q=True, modified=True))
cmds.evalDeferred(lambda: print("Import 완료! 파일이 제대로 로드되었습니다."))
''')
#                 self.send_maya_command(f'''
# import maya.cmds as cmds
# cmds.evalDeferred(lambda: cmds.file("{file_path}", i=True))
# cmds.evalDeferred(lambda: cmds.refresh())
# cmds.evalDeferred(lambda: print("Import 완료!"))
# ''')
#                 self.send_maya_command(f'''
# import maya.cmds as cmds
# cmds.file("{file_path}", i=True, namespace="imported")
# cmds.evalDeferred(lambda: cmds.refresh())
# cmds.evalDeferred(lambda: print("Import 완료!"))
# ''')
#                 self.send_maya_command(f'''
# import maya.cmds as cmds
# import time
# cmds.file("{file_path}", i=True)
# cmds.refresh()
# time.sleep(2)  # Import가 적용될 시간을 줌
# cmds.evalDeferred(lambda: print("Import 완료! 파일이 제대로 로드되었습니다."))
# ''')

                # mel_command = f"file -import -type 'mayaBinary' '{file_path}';"
                # self.send_maya_command(f'import maya.mel as mel; mel.eval("{mel_command}")')
                # self.send_maya_command(f'__import__("maya.cmds").file("{file_path}", i=True)')
            else:
                print("`cmdPort` 활성화 실패. `mayapy`로 Import 시도.")
                self.import_with_mayapy(file_path)
        else:
            print("Maya가 실행 중이 아님. `mayapy`를 사용하여 Import 진행합니다.")
            self.import_with_mayapy(file_path)


    

    def create_reference_maya(self, file_path):
        """Maya에서 Create Reference 수행"""
        if self.is_maya_running():
            if not self.is_cmd_port_open():
                self.enable_maya_cmd_port()

            if self.is_cmd_port_open():
                namespace = f'ref_{os.path.basename(file_path).split(".")[0]}'
                command = (
                    f"import maya.cmds as cmds; "
                    f'cmds.file("{file_path}", reference=True, namespace="{namespace}"); '
                    f"cmds.evalDeferred(lambda: cmds.refresh()); "
                    f'cmds.evalDeferred(lambda: print("Create Reference 완료! 파일이 제대로 로드되었습니다."))'
                )
                self.send_maya_command(command)
            else:
                self.create_reference_with_mayapy(file_path)
        else:
            self.create_reference_with_mayapy(file_path)

        



    def import_with_mayapy(self, file_path):
        """Maya가 실행 중이 아닐 때 `mayapy`를 사용하여 Import"""
        mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"
        if not os.path.exists(mayapy_path):
            QtWidgets.QMessageBox.warning(self, "오류", "Maya Python 실행 파일(mayapy)을 찾을 수 없습니다.")
            return

        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "/usr/autodesk/maya2023/lib:" + env.get("LD_LIBRARY_PATH", "")

        import_script = f'''
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
cmds.file("{file_path}", i=True)
print("Maya에서 파일을 Import 했습니다: {file_path}")
'''

        subprocess.run(["bash", "-c", f"source /home/rapa/env/maya.env && {mayapy_path} -c '{import_script}'"], env=env, check=True)


   

    def create_reference_with_mayapy(self, file_path):
        """Maya가 실행 중이 아닐 때 `mayapy`를 사용하여 Create Reference"""
        mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"
        if not os.path.exists(mayapy_path):
            QtWidgets.QMessageBox.warning(self, "오류", "Maya Python 실행 파일(mayapy)을 찾을 수 없습니다.")
            return

        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "/usr/autodesk/maya2023/lib:" + env.get("LD_LIBRARY_PATH", "")

        import_script = f'''
    import maya.standalone
    maya.standalone.initialize()
    import maya.cmds as cmds
    cmds.file("{file_path}", reference=True, namespace="ref_{os.path.basename(file_path).split('.')[0]}")
    cmds.refresh()
    print("Maya에서 Reference 파일을 불러왔습니다: {file_path}")
    '''

        subprocess.run(["bash", "-c", f"source /home/rapa/env/maya.env && {mayapy_path} -c '{import_script}'"], env=env, check=True)


# 실행
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    user_id = 132  # 실제 사용자 ID
    window = FileLoaderGUI(user_id)
    window.show()
    sys.exit(app.exec())

    