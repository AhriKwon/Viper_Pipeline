
import os
import subprocess
import socket
from PySide6.QtWidgets import QMessageBox

class NukeLoader:
    """
    Nuke 실행 및 TCP 명령 전송을 위한 정적 메서드 클래스
    
    """

    @staticmethod
    def launch_nuke(file_path):
        """
        Nuke 실행 후 파일 열기
        nuke.env 먼저 로드 후 Nuke 구동하기
        
        """
        nuke_executable = NukeLoader.find_nuke_path()
        if nuke_executable:
            env = os.environ.copy()
            env["FOUNDRY_LICENSE_FILE"] = "/usr/local/foundry/RLM/nuke.lic"
            env["RLM_LICENSE"] = "/usr/local/foundry/RLM"
            
            try:
                # Bash를 사용하여 환경 파일을 로드한 후 Nuke 실행
                nuke_command = f"source /home/rapa/env/nuke.env && {nuke_executable} {file_path}"
                subprocess.Popen(["/bin/bash", "-c", nuke_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print(f"Nuke에서 파일을 실행했습니다: {file_path}")

            except Exception as e:
                QMessageBox.warning(None, "오류", f"Nuke 실행 실패: {e}")
        else:
            QMessageBox.warning(None, "오류", "Nuke 실행 파일을 찾을 수 없습니다.")

    @staticmethod
    def send_nuke_command(command, host="127.0.0.1", port=7007):
        """
        Nuke에 python 명령어를 보내고 실행 
        
        """
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

    @staticmethod
    def import_nk_file(file_path):
        """
        .nk 파일을 nodePaste로 불러오기
        
        """
        command = f"nuke.nodePaste(r'{file_path}')"
        NukeLoader.send_nuke_command(command)

    @staticmethod
    def import_abc_file(file_path):
        """
        Alembic, .obj 파일은 ReadGeo2로 불러오기
        
        """
        # f-string에서 '{{' => '{' 이스케이프
        command = f"nuke.createNode('ReadGeo2', 'file {{{{ {file_path} }}}}')"
        NukeLoader.send_nuke_command(command)

    @staticmethod
    def import_2d_file(file_path):
        """
        이미지(.exr, .png 등)/영상(.mov, .mp4)은 Read로 불러오기
        
        """
        command = f"nuke.createNode('Read', 'file {{{{ {file_path} }}}}')"
        NukeLoader.send_nuke_command(command)
        
        
    @staticmethod
    def import_nuke(file_path):
        """
        파일 확장자에 따라 각각 다른 방식으로 Import
        
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".nk":
            NukeLoader.import_nk_file(file_path)
        elif ext in [".abc", ".obj"]:
            NukeLoader.import_abc_file(file_path)
        elif ext in [".exr", ".png", ".jpg", ".jpeg", ".mov", ".mp4", ".tif", ".tiff"]:
            NukeLoader.import_2d_file(file_path)
        else:
            print("[오류] 지원하지 않는 확장자:", ext)
        

    @staticmethod
    def find_nuke_path():
        """
        Nuke 실행 파일 경로 찾기
        
        """
        possible_paths = [
            "/usr/local/Nuke15.1v5/Nuke15.1",
            "/opt/Nuke15.1v5/Nuke15.1",
            "/usr/bin/Nuke15.1v5",
            "/usr/local/bin/Nuke15.1",
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

    @staticmethod
    def is_nuke_running():
        """
        ps aux 명령어로 현재 실행 중인 모든 프로세스 정보 받아오고 
        'Nuke', 'nuke', 'Nuke15' 등의 문자열이 있는지 확인해서
        Nuke가 실행 중인지 파악하기
        
        """
        try:
            # 실행 중인 모든 프로세스를 검사하여 Nuke가 있는지 확인
            result = subprocess.run(["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in result.stdout.split("\n"):
                # "Nuke", "nuke", "Nuke15" 등 다양한 키워드가 들어 있는지 확인
                if "Nuke" in line or "nuke" in line or "Nuke15" in line:
                    return True
            return False
        except Exception as e:
            print(f"Nuke 실행 확인 오류: {e}")
            return False

"""
[INFO]

1. ps aux: 시스템에서 현재 동작 중인 거의 모든 프로세스 정보를 나열하는 명령어.
2. stdout=subprocess.PIPE, stderr=subprocess.PIPE: 외부 명령어가 출력한 내용을 
   파이썬에서 프로그래밍적으로 제어하려고 할 때 사용하는 설정.
3. stdout, stderr: 각각 표준 출력과 표준 에러 스트림을 의미.
4. subprocess: 파이썬에서 외부 명령어를 실행하고 입출력을 제어할 수 있는 모듈.
5. PIPE: 파이썬과 외부 프로세스 사이에 “파이프”를 만들어, 
   데이터(출력·에러 등)를 주고받을 수 있게 하는 역할.

"""