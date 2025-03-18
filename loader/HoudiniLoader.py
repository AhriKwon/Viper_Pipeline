import os
import subprocess




class HoudiniLoader:
    """
    Houdini 관련 작업을 처리하는 클래스
    
    """

    @staticmethod
    def launch_houdini(file_path):
        """
        Houdini 실행 후 파일 열기
        
        """
        houdini_executable = HoudiniLoader.find_houdini_path()
        if houdini_executable:
            subprocess.Popen([houdini_executable, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Houdini에서 파일을 실행했습니다: {file_path}")
        else:
            print("오류: Houdini 실행 파일을 찾을 수 없습니다.")

    @staticmethod
    def import_houdini(file_path):
        """
        Houdini에서 파일을 Import
        현재 Houdini 세션에 .hip 또는 기타 확장자를 merge
        hython을 사용하여 스크립트를 실행함
        
        """
        if not os.path.exists(file_path):
            print(f"파일이 존재하지 않습니다: {file_path}")
            return

        houdini_python = "/opt/hfs20.5.487/bin/hython"

        env = os.environ.copy()
        env["HOUDINI_MAJOR_RELEASE"] = "20"
        env["HOUDINI_VERSION"] = "20.5.487"
        env["HOUDINI_PATH"] = "/opt/hfs20.5.487"
        env["PATH"] = f"/opt/hfs20.5.487/bin:{env['PATH']}"
        env["LD_LIBRARY_PATH"] = f"/opt/hfs20.5.487/dsolib:{env.get('LD_LIBRARY_PATH', '')}"

        script_content = f'''import hou
hou.hipFile.merge("{file_path}")
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

    @staticmethod
    def is_houdini_running():
        """
        pgrep -f "houdini"를 통해
        Houdini 실행 여부 확인

        """
        try:
            result = subprocess.run(["pgrep", "-f", "houdini"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Houdini 실행 확인 오류: {e}")
            return False

    @staticmethod
    def send_houdini_command(command):
        """
        Houdini에서 Python 명령 실행
        Houdini 실행 파일에 -c 옵션으로
        지정된 Python 명령어를 전달해 실행

        """
        houdini_executable = HoudiniLoader.find_houdini_path()
        if houdini_executable:
            try:
                subprocess.run([houdini_executable, "-c", command], check=True)
                print(f"Houdini 명령 실행: {command}")
            except Exception as e:
                print(f"Houdini 명령 실행 실패: {e}")
        else:
            print("오류: Houdini 실행 파일을 찾을 수 없습니다.")

    @staticmethod
    def find_houdini_path():
        """
        Houdini 실행 파일 경로 찾기
        
        """
        possible_paths = [
            "/opt/hfs20.5.487/bin/houdini",
            "/usr/local/bin/houdini",
            "/usr/bin/houdini",
        ]
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        return None