
import os
import subprocess
import socket


class MayaLoader:
    """
    Maya 관련 유틸리티 함수 클래스
    
    """

    @staticmethod
    def launch_maya(file_path):
        """
        Maya 실행 후  파일 열기 
        maya.env source 후 실행하기
        
        """
        maya_executable = MayaLoader.find_maya_path()
        if maya_executable:
            maya_command = f'bash -c "source /home/rapa/env/maya.env && {maya_executable} -command \\"file -o \\\\\\"{file_path}\\\\\\";\\""'
            subprocess.Popen(maya_command, shell=True)
            print(f"Maya에서 파일을 불러왔습니다: {file_path}")
        # elif maya_executable:
        #         subprocess.Popen(["bash", "-c", f"source /home/rapa/env/maya.env && {maya_executable}"], shell=False)
        #         print(f"Maya 실행됨 (환경 변수 적용됨)")
        else:
            print("Maya 실행 파일을 찾을 수 없습니다.")


    @staticmethod
    def open_new_scene_maya():
        """
        기존 Maya를 종료하지 않고 새로운 Maya 창을 띄움
        
        """
        maya_executable = MayaLoader.find_maya_path()
        if maya_executable:
            maya_command = f'bash -c "source /home/rapa/env/maya.env && {maya_executable}"'
            subprocess.Popen(maya_command, shell=True)
            print(f"알림", "새로운 Maya 창이 열렸습니다.")
        else:
            print(f"오류", "Maya 실행 파일을 찾을 수 없습니다.")

    @staticmethod
    def find_maya_path():
        """
        Maya 실행 파일 경로 찾기
        
        """
        possible_paths = ["/usr/autodesk/maya2023/bin/maya"]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    @staticmethod
    def is_maya_running():
        """
        pgrep -f 명령어로 'maya' 문자열을 검색,
        현재 Maya 프로세스가 동작 중인지 확인
        
        """
        try:
            result = subprocess.run(["pgrep", "-f", "maya"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            print(f"Maya 실행 확인 오류: {e}")
            return False

    @staticmethod
    def is_cmd_port_open(port=7001):
        """
        cmdPort가 활성화되어 있는지 확인
        
        """
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

    @staticmethod
    def enable_maya_cmd_port():
        """
        Maya에서 cmdPort 활성화하는 명령을 보냄
        
        """
        print("Maya에서 cmdPort 활성화를 시도합니다...")
        mel_command = 'commandPort -name ":7001" -sourceType "python";'
        MayaLoader.send_maya_command(mel_command)

    @staticmethod
    def send_maya_command(command):
        """
        Maya cmdPort(7001)를 소켓으로 연결, 
        명령어 실행 후 응답 확인
        
        """
        try:
            with socket.create_connection(("localhost", 7001), timeout=2) as sock:
                sock.sendall((command + "\n").encode("utf-8"))  # 문자열을 utf-8 바이트로 변환 후 전송
                response = sock.recv(4096).decode("utf-8").strip()
                print(f"Maya 응답: {response}")
                print(f"Maya에서 명령 실행: {command}")
        except Exception as e:
            print(f"`cmdPort` Import 실패: {e}")

    @staticmethod
    def import_maya(file_path):
        """
        Maya가 이미 실행 중이라면 cmdPort 방식을 통해 Import,
        실행 중이 아니면 mayapy를 사용하여 Import 시도하기
        
        """
        if MayaLoader.is_maya_running():
            print("Maya 실행 중! `cmdPort` 방식으로 Import 시도.")
            if not MayaLoader.is_cmd_port_open():
                print("`cmdPort`가 비활성화됨. MEL을 사용하여 활성화 시도.")
                MayaLoader.enable_maya_cmd_port()

            if MayaLoader.is_cmd_port_open():
                print("`cmdPort` 활성화됨! Maya에서 파일 Import 시도.")
                
                MayaLoader.send_maya_command(f'''
import maya.cmds as cmds
import time
cmds.file("{file_path}", i=True)
cmds.evalDeferred(lambda: cmds.refresh())
time.sleep(2)
cmds.evalDeferred(lambda: print("Import 완료! 파일이 제대로 로드되었습니다."))
''')
            else:
                print("`cmdPort` 활성화 실패. `mayapy`로 Import 시도.")
                MayaLoader.import_with_mayapy(file_path)
        else:
            print("Maya가 실행 중이 아님. `mayapy`를 사용하여 Import 진행합니다.")
            MayaLoader.import_with_mayapy(file_path)

    @staticmethod
    def create_reference_maya(file_path):
        """
        Maya가 실행 중이면 cmdPort로 Reference 파일 생성,
        실행 중이 아니라면 mayapy로 실행
        
        """
        if MayaLoader.is_maya_running():
            if not MayaLoader.is_cmd_port_open():
                MayaLoader.enable_maya_cmd_port()

            if MayaLoader.is_cmd_port_open():
                namespace = f'ref_{os.path.basename(file_path).split(".")[0]}'
                command = (
                    f"import maya.cmds as cmds; "
                    f'cmds.file("{file_path}", reference=True, namespace="{namespace}"); '
                    f"cmds.evalDeferred(lambda: cmds.refresh()); "
                    f'cmds.evalDeferred(lambda: print("Create Reference 완료! 파일이 제대로 로드되었습니다."))'
                )
                MayaLoader.send_maya_command(command)
            else:
                MayaLoader.create_reference_with_mayapy(file_path)
        else:
            MayaLoader.create_reference_with_mayapy(file_path)

    @staticmethod
    def import_with_mayapy(file_path):
        """
        Maya가 실행 중이 아닐 때 `mayapy`를 사용하여 Import
        
        """
        mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"
        if not os.path.exists(mayapy_path):
            print("Maya Python 실행 파일(mayapy)을 찾을 수 없습니다.")
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

    @staticmethod
    def create_reference_with_mayapy(file_path):
        """
        Maya가 실행 중이 아닐 때 `mayapy`를 사용하여 Create Reference
        
        """
        mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"
        if not os.path.exists(mayapy_path):
            print("Maya Python 실행 파일(mayapy)을 찾을 수 없습니다.")
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




    @staticmethod
    def create_workspace_mel(project_path):
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

            print(f"workspace.mel 파일 생성 완료: {workspace_mel_path}")
        else:
            print(f"workspace.mel 파일이 이미 존재합니다: {workspace_mel_path}")

