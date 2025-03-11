import os
import sys
import subprocess
import socket


from PySide6 import QtWidgets, QtGui, QtCore 
from PySide6.QtWidgets import QFileDialog, QMessageBox

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


        self.reference_button = QtWidgets.QPushButton("파일 Reference")
        self.reference_button.clicked.connect(self.create_reference_file)
        button_layout.addWidget(self.reference_button)

        self.new_scene_button = QtWidgets.QPushButton("새 파일 Open")
        self.new_scene_button.clicked.connect(self.open_new_scene_maya)
        button_layout.addWidget(self.new_scene_button)


        self.task_button = QtWidgets.QPushButton("Task 파일 열기")
        self.task_button.clicked.connect(self.open_or_create_task_file)
        button_layout.addWidget(self.task_button)

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
        file_path, _ = file_dialog.getOpenFileName(self, "파일 선택", "", "Maya Files (*.ma *.mb);;Nuke Files (*.nk);;Houdini Files (*.hip *.hiplc);;All Files (*.*)")

        if file_path:
            self.file_path_input.setText(file_path)


    def run_file(self):
        """설정된 파일 경로를 읽고 Maya or Nuke or Houdini에서 실행"""
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
        elif file_path.endswith((".hip", ".hiplc", ".hipnc")):
            self.launch_houdini(file_path)
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



    def open_or_create_task_file(self):
        """할당된 Task 파일을 열거나, 없으면 자동으로 생성"""

        task_info = self.get_task_info()
        if not task_info:
            QtWidgets.QMessageBox.warning(self, "오류", "Task 정보를 가져올 수 없습니다.")
            return

        file_path = self.get_task_file_path(task_info)
    
        # 디버깅 로그 추가
        print(f"생성할 Task 파일 경로: {file_path}")

        # 디렉토리 존재 확인 및 생성
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            print(f"디렉토리가 존재하지 않습니다. 생성 중: {directory}")
            os.makedirs(directory, exist_ok=True)

        # 파일이 존재하면 새로운 버전 파일 생성
        if os.path.exists(file_path):
            print(f"파일이 이미 존재합니다: {file_path}")
            new_file_path = self.get_next_version_file(file_path)
        else:
            print(f"파일이 존재하지 않습니다. 새 파일 생성 예정: {file_path}")
            new_file_path = file_path

        # 빈 파일 생성
        try:
            with open(new_file_path, "w") as f:
                f.write("")  # 빈 파일 생성
            print(f"새로운 Task 파일 생성됨: {new_file_path}")
        except Exception as e:
            print(f"파일 생성 실패: {e}")
            QtWidgets.QMessageBox.warning(self, "오류", f"파일 생성 실패: {e}")
            return

        # 프로그램 실행
        self.launch_program(new_file_path)



    def get_task_info(self):
        """사용자의 Task 정보를 가져오는 함수"""
        tasks = manager.get_tasks_by_user(user_id)
        if not tasks:
            return None
        return tasks[0]  # 첫 번째 Task를 가져옴

    def get_task_file_path(self, task_info):
        """Task 정보를 기반으로 파일 경로 생성"""
        base_path = "/nas/show/Viper/assets"
        asset_type = task_info.get("asset_type", "Unknown")
        asset_name = task_info.get("asset_name", "Unknown")
        task_name = task_info.get("task", "Unknown")
        ext = "ma" if task_name in ["MDL", "ANM"] else "nk"

        # 파일 경로 생성
        file_path = f"{base_path}/{asset_type}/{asset_name}/{task_name}/work/maya/scenes/{asset_name}_{task_name}_v001.{ext}"
    
        # 디버깅 로그 추가
        print(f"생성된 파일 경로: {file_path}")

        return file_path


    def get_next_version_file(self, file_path):
        """파일 버전을 자동으로 업그레이드"""
        base, ext = os.path.splitext(file_path)
        version = 1

        while os.path.exists(file_path):
            version += 1
            file_path = f"{base[:-3]}v{str(version).zfill(3)}{ext}"

        print(f"새로운 버전 파일 경로: {file_path}")
        return file_path


    def launch_program(self, file_path):
        """파일 확장자에 따라 Maya 또는 Nuke 실행"""
        if file_path.endswith(".ma") or file_path.endswith(".mb"):
            self.launch_maya(file_path)
        elif file_path.endswith(".nk"):
            self.launch_nuke(file_path)
        elif file_path.endswith((".hip", ".hiplc", ".hipnc")):
            self.launch_houdini(file_path)


    def launch_nuke(self, file_path):
        """Nuke 실행 후 파일 열기"""
        nuke_executable = self.find_nuke_path()
        if nuke_executable:
            env = os.environ.copy()
            env["FOUNDRY_LICENSE_FILE"] = "/usr/local/foundry/RLM/nuke.lic"
            env["RLM_LICENSE"] = "/usr/local/foundry/RLM"

            try:
                subprocess.Popen([nuke_executable, file_path], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Nuke에서 파일을 실행했습니다: {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "오류", f"Nuke 실행 실패: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")


   

    def import_nuke(self):
        """사용자가 선택한 Nuke(.nk) 파일을 현재 실행 중인 Nuke에 Import"""

        # 파일 선택 대화 상자 열기
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Nuke 파일 선택", "", "Nuke Files (*.nk);;All Files (*.*)")

        if not file_path:
            print("파일 선택 취소됨.")
            return

        if not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(self, "오류", "파일이 존재하지 않습니다.")
            return

        if not file_path.endswith(".nk"):
            QtWidgets.QMessageBox.warning(self, "오류", "올바른 Nuke 파일을 선택하세요.")
            return

        # Nuke 실행 여부 확인 (self.is_nuke_running() 호출)
        if not self.is_nuke_running():
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke가 실행 중이지 않습니다. 먼저 Nuke를 실행하세요.")
            return

        # Nuke에서 실행할 Python 코드
        nuke_script = f'''
    import nuke
    nuke.scriptReadFile("{file_path}")
    print("Nuke에서 파일을 Import 했습니다: {file_path}")
    '''

        try:
            # 실행 중인 Nuke에 명령어 전달
            result = subprocess.run(["/usr/bin/nuke", "-t", "-c", nuke_script], check=True, capture_output=True, text=True)
            print(f"Nuke에서 파일을 Import 했습니다: {file_path}")
            print(f"Nuke 실행 결과: {result.stdout}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "오류", f"Nuke Import 실패: {e}")


    def is_nuke_running(self):
        """현재 실행 중인 Nuke 프로세스를 확인하는 함수 (클래스 메서드로 변경)"""
        try:
            # 실행 중인 모든 프로세스를 검사하여 Nuke가 있는지 확인
            result = subprocess.run(["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return any("Nuke" in line or "nuke" in line for line in result.stdout.split("\n"))
        except Exception as e:
            print(f"Nuke 실행 확인 오류: {e}")
            return False



    

    

        
        
        # if not os.path.exists(file_path):
        #     print(f"오류: 파일이 존재하지 않습니다: {file_path}")
        #     return

        # if not file_path.endswith(".nk", ".mov", ".abc", ".obj"):
        #     print("지원되지 않는 파일 형식입니다. .nk 파일만 Import 가능합니다.")
        #     return

        # try:
        #     nuke.scriptReadFile(file_path)  # Nuke에서 .nk 파일을 불러오기
        #     print(f"Nuke에서 파일을 Import 했습니다: {file_path}")
        # except Exception as e:
        #     print(f"Nuke Import 실패: {e}")

        
#         nuke_executable = "/usr/local/Nuke15.1v5/Nuke15.1"

#         if self.is_nuke_running():
#             try:
#                 import_script_path = "/home/rapa/import_nuke_script.py"

#                 with open(import_script_path, "w") as script_file:
#                     script_file.write(f'''
# import nuke
# nuke.scriptReadFile("{file_path}")
# print("Nuke에서 파일을 Import 했습니다: {file_path}")
# ''')

#                 env = os.environ.copy()
#                 env["NUKE_PATH"] = "/usr/local/Nuke15.1v5"
#                 env["LD_LIBRARY_PATH"] = "/usr/local/Nuke15.1v5/lib:" + env.get("LD_LIBRARY_PATH", "")

#                 subprocess.run([nuke_executable, "-t", import_script_path], check=True, env=env, capture_output=True, text=True)
#                 print(f"Nuke에서 파일을 Import 했습니다: {file_path}")

#             except subprocess.CalledProcessError as e:
#                 print(f"Nuke 파일 Import 실패: {e}\n출력: {e.stdout}")
#         else:
#             print("실행 중인 Nuke가 없습니다. 새로 실행 후 Import 진행.")
#             subprocess.Popen([nuke_executable, file_path])


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
        """파일 Import"""
        file_path = self.file_path_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(self, "오류", "유효한 파일 경로를 입력하세요.")
            return

        # Maya 실행 중인지 확인 후 import
        if self.is_maya_running():
            if file_path.endswith((".ma", ".mb", ".abc", ".obj")):
                self.import_maya(file_path)
                return

        # Nuke 실행 중인지 확인 후 import
        if self.is_nuke_running():
            if file_path.endswith((".nk", ".mov", ".abc", ".obj")):
                self.import_nuke(file_path)
                return

        # Houdini 실행 중인지 확인 후 import
        if self.is_houdini_running():
            if file_path.endswith((".hip", ".hiplc", ".hipnc", ".abc", ".obj")):
                self.import_houdini(file_path)
                return

        # 해당하는 프로그램이 실행 중이지 않을 때 경고 메시지 표시
        QtWidgets.QMessageBox.warning(self, "오류", "파일을 불러올 프로그램이 실행되지 않았습니다.")


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
cmds.evalDeferred(lambda: cmds.file("{file_path}", i=True))
cmds.evalDeferred(lambda: cmds.refresh())
cmds.evalDeferred(lambda: cmds.file(q=True, modified=True))
cmds.evalDeferred(lambda: print("Import 완료! 파일이 제대로 로드되었습니다."))
''')
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



    

    def launch_houdini(self, file_path):
        """Houdini 실행 후 파일 열기"""
        houdini_executable = self.find_houdini_path()
        if houdini_executable:
            subprocess.Popen([houdini_executable, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Houdini에서 파일을 실행했습니다: {file_path}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Houdini 실행 파일을 찾을 수 없습니다.")

    
    

    def import_houdini(self, file_path):
        """Houdini에서 파일을 Import"""
        if not os.path.exists(file_path):
            print(f"파일이 존재하지 않습니다: {file_path}")
            return

        houdini_seup = "/opt/hfs20.5.487/houdini_setup"
        houdini_python = "/opt/hfs20.5.487/bin/hython"

        # Houdini 환경변수 직접 설정
        env = os.environ.copy()
        env["HOUDINI_MAJOR_RELEASE"] = "20"
        env["HOUDINI_VERSION"] = "20.5.487"
        env["HOUDINI_PATH"] = "/opt/hfs20.5.487"
        env["PATH"] = f"/opt/hfs20.5.487/bin:{env['PATH']}"
        env["LD_LIBRARY_PATH"] = f"/opt/hfs20.5.487/dsolib:{env.get('LD_LIBRARY_PATH', '')}"

        script_content = f'''import hou
    hou.hipFile.load("{file_path}", merge=True)
    print("Houdini에서 파일을 import 했습니다: {file_path}")'''

        script_path = "/tmp/import_houdini.py"
        with open(script_path, "w") as script_file:
            script_file.write(script_content)

        try:
            result = subprocess.run(
                [houdini_python, script_path], 
                check=True, 
                capture_output=True, 
                text=True,
                env=env  # Houdini 환경변수 적용
            )
            print(f"Houdini Import 완료\n출력: {result.stdout}")

        except subprocess.CalledProcessError as e:
            print(f"Houdini Import 실패: {e}\n출력: {e.stdout}\n오류 메시지: {e.stderr}")


    def is_houdini_running(self):
        """Houdini 실행 여부 확인"""
        try:
            result = subprocess.run(["pgrep", "-f", "houdini"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Houdini 실행 확인 오류: {e}")
            return False

    def send_houdini_command(self, command):
        """Houdini에서 Python 명령 실행"""
        houdini_executable = self.find_houdini_path()
        if houdini_executable:
            try:
                subprocess.run([houdini_executable, "-c", command], check=True)
                print(f"Houdini 명령 실행: {command}")
            except Exception as e:
                print(f"Houdini 명령 실행 실패: {e}")
                QtWidgets.QMessageBox.warning(None, "오류", f"Houdini 명령 실행 실패: {e}")
        else:
            QtWidgets.QMessageBox.warning(None, "오류", "Houdini 실행 파일을 찾을 수 없습니다.")

    def find_houdini_path(self):
        """Houdini 실행 파일 경로 찾기"""
        possible_paths = [
            "/opt/hfs20.5.487/bin/houdini",
            "/usr/local/bin/houdini",
            "/usr/bin/houdini",
        ]
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        return None


# 실행
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    user_id = 132 # 실제 사용자 ID
    window = FileLoaderGUI(user_id)
    window.show()
    sys.exit(app.exec())