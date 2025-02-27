import os
import datetime
import maya.cmds as cmds
from PublishPath import FilePath

class MayaPublish():
    
    """Maya에서 Playblast 또는 Alembic을 저장하고 Mp4 또는 Mov로 변환하는 클래스"""
    def __init__(self, output_dir="/nas/Viper/hyerin/Publisher"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Alembic 플러그인 로드 확인
        if not cmds.pluginInfo("AbcExport", query=True, loaded=True):
            print("Alembic 플러그인이 로드되었습니다.")
            
    def save_alembic(self):
        
        """Alembic(.abc) 파일을 저장하는 함수(프레임 범위 없음)"""
        
        selected_objects = cmds.ls(selection=True)
        alembic_path = "/nas/Viper/hyerin/test.abc"

        if not selected_objects:
            print("Error: 선택된 오브젝트가 없습니다.")
            return

        # 선택된 오브제를 -root 옵션으로 설정
        objects_str = " ".join([f"-root {obj}" for obj in selected_objects])

        # Alembic Export 실행
        alembic_command = f"{objects_str} -file {alembic_path}"
        
        try:
            # Alembic 내보내기 명령어 실행
            cmds.AbcExport(j=alembic_command)
            print(f"Alembic 저장되었습니다: {alembic_path}")
            
        except Exception as e:
            print(f"Error: Alembic 내보내기 실패 - {str(e)}") 

    def make_turntable(self, cam_name="turntable_cam", start_frame=1, end_frame=100):
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
        cmds.xform(cam, rotation=(-30, -45, 0)) # 각도 조정

        # 애니메이션 키 설정
        cmds.setKeyframe(cam_grp, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(cam_grp, attribute="rotateY", value=360, time=end_frame)
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")

        print(f"Turntable Camera '{cam_name }' created from frame {start_frame} to {end_frame}.")

    @staticmethod
    def save_playblast(output_path):
        """Playblast 실행 후 저장"""
        
        # cmds.optionVar(intValue=("playblastFormat", 8))
        
        cmds.playblast(
            format="qt",
            filename=output_path,
            sequenceTime=False,
            clearCache=True,
            viewer=False,
            showOrnaments=False,
            framePadding=4,
            percent=100,
            compression="jpeg",
            quality=100,
            forceOverwrite=True,
            widthHeight=(1920, 1080),
            startTime=1,
            endTime=99
        )
        print(f"Playblast 저장 완료: {output_path}")

    def set_viewport_option(self, option):
        # 현재 활성화된 모델 패널을 가져옵니다
        # panel = cmds.getPanel(withFocus=True) 원래 이건대
        panel = "modelPanel4" # <-- 이거 테스트용
        if option == "shaded":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=False, displayTextures=False)
        elif option == "wireframe on shaded":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=True, displayTextures=False)
        elif option == "textured":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=False, displayTextures=True)
        elif option == "wireframe on textured":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=True, displayTextures=True)

        print(f"뷰포트 설정 변경: {option}")

    def export_playblast(self):
        
        """턴테이블 카메라를 사용하여 Playblast 실행"""
        all_cameras = cmds.ls(type="camera", long=True)
        scene_cameras = [cam for cam in all_cameras if "persp" not in cam and "top" not in cam and "side" not in cam and "front" not in cam]

        if not scene_cameras:
            self.maeke_turntable()
            all_cameras = cmds.ls(type="camera", long=True)
            scene_cameras = [cam for cam in all_cameras if "persp" not in cam and "top" not in cam and "side" not in cam and "front" not in cam]

        camera_to_use = scene_cameras[0]
        # panel = cmds.getPanel(withFocus=True)
        panel = "modelPanel4" # <-- 이거 테스트용
        cmds.lookThru(panel, camera_to_use)
        cmds.viewFit(all=True) # 씬 전체에 맞게 뷰 핏

        print(f"뷰포트 카메라 설정 완료: {camera_to_use}")

        output_path = FilePath.get_publish_path("Viper", "Character", "Hero_Character" , "MDL", version=1)
        
        self.save_playblast(output_path)

    def playblast_publish(self, options):
        """UI 옵션 리스트에 따라 Playblast 실행"""
        for option in options:
            self.set_viewport_option(option)
            self.export_playblast()
   

# class UIPublisher():
#     """UI를 통해 Maya에서 mp4 또는 mov 변환을 실행하는 클래스"""
#     @staticmethod
#     def export_from_maya(format_type):
#         maya_pub = MayaPublish()
#         maya_pub.publish_video(format_type)


if __name__ == "__main__":
    maya_pub = MayaPublish()
    selected_options = ["shaded", "wireframe on shaded"]
    maya_pub.playblast_publish(selected_options)
    maya_pub.save_alembic()
