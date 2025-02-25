import os
import maya.cmds as cmds

class MayaPublish():
    """Maya에서 Playblast 또는 Alembic을 저장하고 Mp4 또는 Mov로 변환하는 클래스"""
    def __init__(self, output_dir="/nas/Viper/hyerin/Publisher"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def save_playblast(output_path):
        
        cmds.playblast(format="qt", filename=output_path, forceOverwrite=True, viewer=True)
        print(f"Playblast 저장 완료: {output_path}")

    def publish_video(self, format_type="mp4"):
        output_path = os.path.join(self.output_dir, f"output.{format_type}")
        self.save_playblast(output_path)
    def save_maya_file_with_format(self, file_path): 
        # 현재 file_path에 작업 중인 scene 저장하는 함수
        # 새로운 파일 경로에 저장
        cmds.file(rename=file_path)
        cmds.file(save=True, type="mayaAscii")
        print(f"saved Maya File: {file_path}")
        
    def save_alembic(self, file_path, start_frame=1, end_frame=100, selection=True):
        # Alembic(.abc) 파일을 저장하는 함수.
        # : param file_path: 저장할  Alembic file path
        # : param end_frame: 익스포트 종료 프레임
        # : param selection: 현재 선택된 오브젝트만 익스포트할 지 여부

        if selection:
            selected_objects = cmds.ls(selection=True)
            if not selected_objects:
                print("Error: 선택된 오브젝트가 없습니다.")
                return
                objects_str = " ".join([f"-root{obj}" for obj in selected_objects])
            else:
                objects_str = "-wholeScene" # 씬 전체를 추출
        # Alembic Export 명령어 실행, frameRange 'start() to end().'
        alembic_command = f"=frameRange {start_frame} {end_frame} {objects_str} -file {file_path}" 
        cmds.AbcExport(j=alembic_command) 
        print(f"Alembic")

        cmds.file(name=file_path)
        cmds.file(save=True, type="Alembic Cache")
        print(f"saved .abc File: {file_path}")

    def get_file_format(self):
        # 현재 열려있는 Maya file format return 하는 함수
        # if file did not be saved, then -> None
        file_path = cmds.file(query=True, sceneName=True)

        if not file_path:
            print ("No file is currently saved.")
            return None # file 저장 안 된 경우
        file_ext = os.path.splitext(file_path)[-1] # 확장자 추출

        if file_ext == ".ma":
            return "mayaAscii"
        elif file_ext == ".mb":
            return "mayaBinary"
        else:
            print(f"Unknown file format: {file_ext}")
            return None # 알 수 없는 포맷일 경우
    
    def playblast_with_options(self):
        """선택된 옵션에 따라 Playblast 실행"""
        wireframe = cmds.checkBox("wireCheck", query=True, value=True)
        shader = cmds.checkBox("shaderCheck", query=True, value=True)
        # Note 선택시 모든 옵션 비활성화
        if cmds.checkBox("noneCheck", query=True, value=True):
            wireframe = False
            shader = False
        # Both 선택 시 Wireframe + Shader 활성화
        if cmds.checkBox("bothCheck", query=True, value=True):
            wireframe = True
            shader = True
        # Playblast 실행
        if wireframe and shader:
            cmds.modelEditor('test_maya', edit=True, wireframeOnShaded=True)
        elif wireframe:
            cmds.modelEditor('test_maya', edit=True, displayAppearance='wireframe')
        elif shader:
            cmds.modelEditor('test_maya', edit=True, displayAppearance='smoothShadered')
        else:
            cmds.modelEditor('test_maya', edit=True, displayAppearance='flatShaded')
        cmds.playblast(format="qt", filename="/home/rapa/test_maya/playblast.mov", forceOverwrite=False, viewer=True)
        print(f"Playblast Completed - Wireframe: {wireframe}, Shader: {shader}")

    def maeke_turntable(self, cam_name="turntable_cam", start_frame=1, end_frame=100, radius=10):
        """
        Maya에서 Turntable camera 생성 후 애니메이션을 적용하는 함수
        :param cam_name: 생성할 카메라 이름
        :param start_frame: 애니메이션 시작 프레임
        :param end_frame: 애니메이션 종료 프레임
        :param radius: 카메라의 원형 회전 반경
        """
        # 카메라 생성
        cam, cam_shape = cmds.camera()
        cam = cmds.rename(cam, cam_name)

        # 그룹 생성 후 회전 적용
        cam_grp = cmds.group(cam, name=f"{cam_name}_grp")
        cmds.xform(cam, translation=(0, 0, radius)) # 반경만큼 이동

        # 애니메이션 키 설정
        cmds.setKeyframe(cam_grp, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(cam_grp, attribute="rotateY", value=360, time=end_frame)

        # Animation Curve 설정 (smooth rounding)
        cmds.bakeResults(cam_grp, simulation=True)  # 텍스쳐 내보낼 때 bake 씀, 오븐에 넣듯이:)
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")

        print(f"Turntable Camera '{cam_name }' created from frame {start_frame} to {end_frame}.")

    def make_truntable_with_xyz_constranints(self, cam_name="turntable_cam", start_frame=1, end_frame=100, radius=-1, lock_axes=["x", "z"]):
     # Maya에서 turntable camera 만들고 특정 축을 고정하는 함수.
     # :param cam_name: 생성할 카메라 이름
     # :param start_frame: 애니메이션 시작 프레임
     # :param end_frame: 애니메이션 종료 프레임
     # :param radius: 카메라의 원형 회전 반경
     # :param lock_axes: 고정할 회전 축 리스트 (예: ["x", "z"])
        cam, cam_shape = cmds.camera()
        cam = cmds.rename(cam, cam_name)
        cam_grp = cmds.group(cam, name=f"{cam_name}_grp")
        cmds.xform(cam, translation=(0, 0, radius))

        cmds.setKeyframe(cam_grp, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(cam_grp, attribute="rotateY", value=360, time=end_frame)

        cmds.bakeResults(cam_grp, simulation=True) 
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")
    
     # 특정 축을 회전 고정
        for axis in lock_axes:
            cmds.setAttr(f"{cam_grp}.rotate{axis.upper()}", lock=True)
        print(f" Turntable Camera '{cam_name}' created with locked axes: {lock_axes}")

class UIPublisher:
    """UI를 통해 Houdini와 Maya에서 mp4 또는 mov 변환을 실행하는 클래스"""

    @staticmethod
    def export_from_maya(format_type):
        maya_pub = MayaPublish()
        maya_pub.publish_video(format_type)

