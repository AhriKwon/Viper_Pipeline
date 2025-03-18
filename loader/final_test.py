import os
import sys
import subprocess
import socket
import re
import shutil



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

        #기본 경로
        self.base_dir = "/nas/show/Viper"

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

        

        self.task_button = QtWidgets.QPushButton("Task 파일 생성")
        self.task_button.clicked.connect(self.create_new_file_dialog)
        button_layout.addWidget(self.task_button)

        layout.addLayout(button_layout)


        # 퍼블리시된 파일 불러오기
        self.load_published_files()


    def version_up_selected_file(self):
        """선택된 파일을 Version Up"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "오류", "파일을 선택하세요.")
            return

        old_file_path = selected_items[0].text()
        new_file_path = self.version_up(old_file_path)

        # UI 업데이트
        selected_items[0].setText(new_file_path)


    def version_up(self, file_path):
        """파일의 버전을 자동 증가"""
        version_pattern = re.compile(r"(.*)_v(\d{3})(\..+)$")
        match = version_pattern.match(file_path)

        if match:
            base_name, version_num, extension = match.groups()
            version_num = int(version_num)

            # 가장 높은 버전 찾기
            while True:
                version_num += 1
                new_file_path = f"{base_name}_v{version_num:03d}{extension}"
                if not os.path.exists(new_file_path):
                    return new_file_path
        else:
            base_name, extension = os.path.splitext(file_path)
            return f"{base_name}_v001{extension}"


    def create_new_file_dialog(self):
        """새 파일을 생성하는 대화 상자"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("새 파일 생성")
        layout = QtWidgets.QVBoxLayout(dialog)

        # 프로그램 선택 (Maya, Nuke, Houdini)
        self.program_selector = QtWidgets.QComboBox()
        self.program_selector.addItems(["Maya", "Nuke", "Houdini"])
        layout.addWidget(self.program_selector)

        # 파트 선택 드롭다운
        self.part_selector = QtWidgets.QComboBox()
        self.part_selector.addItems(["MDL", "RIG", "LDV", "LAY", "ANM", "LGT", "FX", "COM"])
        layout.addWidget(self.part_selector)

        # 필수 정보 입력 필드
        self.asset_type_input = QtWidgets.QLineEdit()
        self.asset_type_input.setPlaceholderText("asset_type (MDL, RIG, LDV 전용)")
        layout.addWidget(self.asset_type_input)

        self.asset_name_input = QtWidgets.QLineEdit()
        self.asset_name_input.setPlaceholderText("asset_name")
        layout.addWidget(self.asset_name_input)

        self.seq_input = QtWidgets.QLineEdit()
        self.seq_input.setPlaceholderText("seq (LAY, ANM, LGT, FX, COM 전용)")
        layout.addWidget(self.seq_input)

        self.shot_input = QtWidgets.QLineEdit()
        self.shot_input.setPlaceholderText("shot (LAY, ANM, LGT, FX, COM 전용)")
        layout.addWidget(self.shot_input)

        self.task_input = QtWidgets.QLineEdit()
        self.task_input.setPlaceholderText("task")
        layout.addWidget(self.task_input)

        # 파일 생성 버튼
        create_button = QtWidgets.QPushButton("파일 생성 및 실행")
        create_button.clicked.connect(self.create_and_run_task_file)
        layout.addWidget(create_button)
       
        dialog.setLayout(layout)
        dialog.exec()
        

    def create_file_path(self):
        

        """파일을 생성"""
        program = self.program_selector.currentText()
        part = self.part_selector.currentText()
        asset_type = self.asset_type_input.text()
        asset_name = self.asset_name_input.text()
        seq = self.seq_input.text()
        shot = self.shot_input.text()
        task = self.task_input.text()

        # 경로 템플릿
        file_templates = {
            "MDL": f"{self.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "RIG": f"{self.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "LDV": f"{self.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "LAY": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "ANM": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "LGT": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "FX": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/houdini/scenes/{{shot}}_{{task}}_v001.hip",
            "COM": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/nuke/scenes/{{shot}}_{{task}}_v001.nk",
        }

        if part not in file_templates:
            QtWidgets.QMessageBox.warning(self, "오류", "잘못된 파트를 선택하였습니다.")
            return None

        # 경로 생성
        file_path = file_templates[part].format(
            asset_type=asset_type or "Unknown",
            asset_name=asset_name or "Unknown",
            seq=seq or "Unknown",
            shot=shot or "Unknown",
            task=task or "Unknown"
        )

        # 기존 파일이 있으면 버전 증가
        if os.path.exists(file_path):
            file_path = self.version_up(file_path)


        # 디렉토리 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 파일 생성


        if file_path.endswith(".nk"):
            self.create_nuke_file(file_path)

        elif file_path.endswith(".ma"):
            self.create_maya_file(file_path)


        elif file_path.endswith(".hip"):
            self.create_houdini_file(file_path)
            
            
        print(f"새 파일 생성 완료: {file_path}")
        return file_path


    def create_nuke_file(self, empty_nknc_path):
        """
        뉴크 빈파일 만드는 메서드.
        """

        empty_nknc_content = """# Empty Nuke Non-Commercial Script
        version 15.1 v1
        Root {
        inputs 0
        }
        """
        # 빈 .nknc 파일 생성
        with open(empty_nknc_path, "w") as f:
            f.write(empty_nknc_content)

        print(f"Nuke 임시 파일 생성 완료: {empty_nknc_path}")


    def create_maya_file(self, file_path):
        """
        빈 마야 파일을 복사해오는 메서드
        """
        empty_maya_file = "/home/rapa/Viper/loader_test_createfile/test_v001.ma"
        shutil.copy(empty_maya_file, file_path)        
        print(f"Maya 파일 생성 완료: {file_path}")

        maya_project_folder = os.path.dirname(os.path.dirname(file_path))
        self.create_workspace_mel(maya_project_folder)

    
    def create_workspace_mel(self, project_path):
        """
        Maya 프로젝트 폴더 내 workspace.mel 파일을 자동 생성
        """
        workspace_mel_path = os.path.join(project_path, "workspace.mel")

        if not os.path.exists(workspace_mel_path):
            workspace_mel_content = """//Maya 2023 Project Definition

    workspace -fr "fluidCache" "cache/nCache/fluid";
    workspace -fr "DXF_FBX" "data";
    workspace -fr "images" "images";
    workspace -fr "offlineEdit" "scenes/edits";
    workspace -fr "furShadowMap" "renderData/fur/furShadowMap";
    workspace -fr "SVG" "data";
    workspace -fr "scripts" "scripts";
    workspace -fr "DAE_FBX" "data";
    workspace -fr "shaders" "renderData/shaders";
    workspace -fr "furFiles" "renderData/fur/furFiles";
    workspace -fr "OBJ" "data";
    workspace -fr "FBX export" "data";
    workspace -fr "furEqualMap" "renderData/fur/furEqualMap";
    workspace -fr "DAE_FBX export" "data";
    workspace -fr "DXF_FBX export" "data";
    workspace -fr "movie" "movies";
    workspace -fr "ASS Export" "data";
    workspace -fr "move" "data";
    workspace -fr "mayaAscii" "scenes";
    workspace -fr "autoSave" "autosave";
    workspace -fr "sound" "sound";
    workspace -fr "mayaBinary" "scenes";
    workspace -fr "timeEditor" "Time Editor";
    workspace -fr "Arnold-USD" "data";
    workspace -fr "iprImages" "renderData/iprImages";
    workspace -fr "FBX" "data";
    workspace -fr "renderData" "renderData";
    workspace -fr "fileCache" "cache/nCache";
    workspace -fr "eps" "data";
    workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";
    workspace -fr "mel" "scripts";
    workspace -fr "translatorData" "data";
    workspace -fr "particles" "cache/particles";
    workspace -fr "scene" "scenes";
    workspace -fr "USD Export" "data";
    workspace -fr "mayaLT" "";
    workspace -fr "sourceImages" "sourceimages";
    workspace -fr "clips" "clips";
    workspace -fr "furImages" "renderData/fur/furImages";
    workspace -fr "depth" "renderData/depth";
    workspace -fr "sceneAssembly" "sceneAssembly";
    workspace -fr "teClipExports" "Time Editor/Clip Exports";
    workspace -fr "ASS" "data";
    workspace -fr "audio" "sound";
    workspace -fr "USD Import" "data";
    workspace -fr "Alembic" "data";
    workspace -fr "illustrator" "data";
    workspace -fr "diskCache" "data";
    workspace -fr "templates" "assets";
    workspace -fr "OBJexport" "data";
    workspace -fr "furAttrMap" "renderData/fur/furAttrMap";
    """

            with open(workspace_mel_path, "w") as workspace_file:
                workspace_file.write(workspace_mel_content)



            

    def create_houdini_file(self, file_path):
        """
        후디니 빈 파일 만드는 메서드.
        """
        empty_hip_file = "/home/rapa/Viper/loader_test_createfile/test_v001.hip"
        shutil.copy(empty_hip_file, file_path)        
        print(f"Houdini 파일 생성 완료: {file_path}")



    def create_and_run_task_file(self):
        """파일 생성 후 실행"""
        file_path = self.create_file_path()
        if file_path:
            self.file_path_input.setText(file_path)
            self.run_file()

           



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
        elif file_path.endswith((".nk", ".nknc")):
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




    def get_next_version_file(self, file_path):
        """파일 버전을 자동으로 업그레이드"""
        base, ext = os.path.splitext(file_path)
        version = 1

        while os.path.exists(file_path):
            version += 1
            file_path = f"{base[:-3]}v{str(version).zfill(3)}{ext}"

        print(f"새로운 버전 파일 경로: {file_path}")
        return file_path



    def launch_nuke(self, file_path):
        """Nuke 실행 후 파일 열기"""
        nuke_executable = self.find_nuke_path()
        if nuke_executable:
            env = os.environ.copy()
            env["FOUNDRY_LICENSE_FILE"] = "/usr/local/foundry/RLM/nuke.lic"
            env["RLM_LICENSE"] = "/usr/local/foundry/RLM"

            try:
                nuke_command = f'source /home/rapa/env/nuke.env && {nuke_executable} "{file_path}"'
                subprocess.Popen(["/bin/bash", "-c", nuke_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Nuke에서 파일을 실행했습니다: {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "오류", f"Nuke 실행 실패: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")


    def send_nuke_command(self, command, host="127.0.0.1", port=7007):
        """Nuke에 Python 명령을 보내고 실행 결과를 받는 정적 메서드"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))
            client.send(command.encode("utf-8"))

            response = client.recv(4096)
            print(response.decode("utf-8"))
        
        except ConnectionRefusedError:
            print("오류: Nuke 서버가 실행되지 않았습니다. 먼저 Nuke를 실행하세요.")
        
        except Exception as e:
            print(f"오류 발생: {e}")
        
        finally:
            client.close()


    def import_nuke(self, file_path):
        """사용자가 직접 Nuke 파일(.nk)을 선택하여 Import하는 기능"""
        self.send_nuke_command(f"nuke.nodePaste(r'{file_path}')")
        

        
        

    def is_nuke_running(self):
        """현재 실행 중인 Nuke 프로세스를 확인하는 함수 (클래스 메서드로 변경)"""
        try:
            # 실행 중인 모든 프로세스를 검사하여 Nuke가 있는지 확인
            result = subprocess.run(["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return any("Nuke" in line or "nuke" in line for line in result.stdout.split("\n"))
        except Exception as e:
            print(f"Nuke 실행 확인 오류: {e}")
            return False

      
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
            "/usr/foundry/Nuke15.1v5/Nuke15.1"
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # `which` 명령어를 사용하여 Nuke 경로 자동 검색
        try:
            result = subprocess.run(["which", "Nuke15.1v5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            nuke_path = result.stdout.strip()
            if os.path.exists(nuke_path):
                return nuke_path
        except Exception as e:
            print(f"Nuke 경로 검색 오류: {e}")

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
            if file_path.endswith((".nk", ".nknc", ".mov", ".abc", ".obj")):
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

        houdini_setup = "/opt/hfs20.5.487/houdini_setup"
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