
import os
import subprocess
import socket
from PySide6.QtWidgets import QMessageBox

class NukeLoader:
    """Nuke 실행 및 TCP 명령 전송을 위한 정적 메서드 클래스"""

    @staticmethod
    def launch_nuke(file_path):
        """Nuke 실행 후 파일 열기 (환경 파일 로드 포함)"""
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
        """Nuke에 python 명령을 보내고 실행 결과를 받는 정적 메서드"""
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
        """Nuke 스크립트 .nk 파일을 nodePaste로 불러오기"""
        command = f"nuke.nodePaste(r'{file_path}')"
        NukeLoader.send_nuke_command(command)

    @staticmethod
    def import_abc_file(file_path):
        """Alembic 파일은 ReadGeo2로 로드"""
        command = f"nuke.createNode('ReadGeo2', 'file {{{{ {file_path} }}}}')"
        NukeLoader.send_nuke_command(command)

    @staticmethod
    def import_2d_file(file_path):
        """이미지/영상은 Read 노드 생성"""
        command = f"nuke.createNode('Read', 'file {{{{ {file_path} }}}}')"
        NukeLoader.send_nuke_command(command)
        
        
    @staticmethod
    def import_nuke(file_path):
        """사용자가 직접 Nuke 파일(.nk)을 선택하여 Import하는 기능"""
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
        """현재 실행 중인 Nuke 프로세스를 확인하는 함수"""
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
