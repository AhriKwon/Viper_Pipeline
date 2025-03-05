
import os
import subprocess



class NukeLoader:
    """Nuke 관련 기능을 제공하는 클래스"""

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
        return None

    @staticmethod
    def launch_nuke(file_path):
        """Nuke 실행 후 파일 열기"""
        nuke_executable = NukeLoader.find_nuke_path()
        if nuke_executable:
            try:
                subprocess.Popen([nuke_executable, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Nuke에서 파일을 실행했습니다: {file_path}")
            except Exception as e:
                print(f"Nuke 실행 실패: {e}")
        else:
            print("오류: Nuke 실행 파일을 찾을 수 없습니다.")

    @staticmethod
    def is_nuke_running():
        """현재 Nuke가 실행 중인지 확인"""
        try:
            result = subprocess.run(["pgrep", "-f", "Nuke"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Nuke 실행 확인 오류: {e}")
            return False

    @staticmethod
    def import_nuke(file_path):
        """현재 실행 중인 Nuke에 특정 파일 Import"""
        nuke_executable = NukeLoader.find_nuke_path()
        if nuke_executable and NukeLoader.is_nuke_running():
            try:
                import_script_path = "/home/rapa/import_nuke_script.py"

                with open(import_script_path, "w") as script_file:
                    script_file.write(f'''
import nuke
nuke.scriptReadFile("{file_path}")
print("Nuke에서 파일을 Import 했습니다: {file_path}")
''')

                subprocess.run([nuke_executable, "-t", import_script_path], check=True, capture_output=True, text=True)
                print(f"Nuke에서 파일을 Import 했습니다: {file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Nuke 파일 Import 실패: {e}\n출력: {e.stdout}")
        else:
            print("실행 중인 Nuke가 없습니다. 새로 실행 후 Import 진행.")
            subprocess.Popen([nuke_executable, file_path])

    @staticmethod
    def send_nuke_command(command):
        """실행 중인 Nuke에서 Python 명령 실행"""
        if NukeLoader.is_nuke_running():
            try:
                subprocess.run(["nuke", "-t", "-c", command], check=True)
                print(f"Nuke 명령 실행: {command}")
            except Exception as e:
                print(f"Nuke 명령 실행 실패: {e}")
        else:
            print("오류: Nuke가 실행 중인지 확인하세요.")
