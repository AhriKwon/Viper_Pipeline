import os
import sys
import maya.cmds as cmds

# PublishPath 모듈을 찾을 수 있도록 경로 추가
PUBLISH_PATH = "C:/pipeline"

class MayaPublish:
    """Maya에서 Playblast 또는 Alembic을 저장하고 Mp4 또는 Mov로 변환하는 클래스"""
    
    def __init__(self, project, asset_type, asset_name, task, version=1):
        self.project = project
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.task = task
        self.version = version

        # 저장 경로 자동 생성
        self.publish_path = MayaFilePath.get_publish_path(project, asset_type, asset_name, task, version, "mov")
        self.alembic_path = MayaFilePath.get_publish_path(project, asset_type, asset_name, task, version, "abc")

        os.makedirs(os.path.dirname(self.publish_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.alembic_path), exist_ok=True)

        # Alembic 플러그인 로드 확인 및 로드
        if not cmds.pluginInfo("AbcExport", query=True, loaded=True):
            cmds.loadPlugin("AbcExport")
            print("Alembic 플러그인이 로드되었습니다.")

    def save_alembic(self):
        """선택된 오브젝트만 Alembic(.abc) 파일로 저장하는 함수"""
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
                print(" Error: 선택된 오브젝트가 없습니다.")
                return
            
            # objects_str : 선택된 오브젝트들을 Alembic 내보내기 명령어에 맞게 변환
            objects_str = " ".join([f"-root {obj}" for obj in selected_objects])

        alembic_command = f"{objects_str} -file {self.alembic_path}" 

        try:
            cmds.AbcExport(j=alembic_command)
            print(f"Alembic 저장 완료: {self.alembic_path}")
        except Exception as e:
            print(f" Error: Alembic 내보내기 실패 - {str(e)}")

    def make_turntable(self, cam_name="turntable_cam", start_frame=1, end_frame=100):
        # Turntable 카메라 생성 및 애니메이션 적용
        cam, cam_shape = cmds.camera()
        cam = cmds.rename(cam, cam_name)
        cam_grp = cmds.group(cam, name=f"{cam_name}_grp")
        cmds.xform(cam, rotation=(-30, -45, 0))

        cmds.setKeyframe(cam_grp, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(cam_grp, attribute="rotateY", value=360, time=end_frame)
        cmds.keyTangent(cam_grp, attribute="rotateY", inTangentType="linear", outTangentType="linear")

        print(f"Turntable Camera '{cam_name}' 생성 완료 (프레임 {start_frame} ~ {end_frame})")

    def save_playblast(self):
        """Playblast 실행 후 저장"""
        try:
            cmds.playblast(
                format="qt", # quick time 
                filename=self.publish_path,
                sequenceTime=False,
                clearCache=True,
                viewer=False, # 리눅스 os 에서는 False로 해야 오류 최소화
                showOrnaments=False,
                framePadding=4,
                percent=100,
                compression="jpeg", # fpg로 포맷 선택하면 오류나니 정확히 기입할 것!!
                quality=100,
                forceOverwrite=True,
                widthHeight=(1920, 1080),
                startTime=1,
                endTime=99
            )
            print(f"Playblast 저장 완료: {self.publish_path}")
        except Exception as e:
            print(f" Error: Playblast 저장 실패 - {str(e)}")

    def set_viewport_option(self, option):
        """뷰포트 설정 변경"""
        panel = "modelPanel4"
        settings = {
            "shaded": {"displayAppearance": "smoothShaded", "wireframeOnShaded": False, "displayTextures": False},
            "wireframe on shaded": {"displayAppearance": "smoothShaded", "wireframeOnShaded": True, "displayTextures": False},
            "textured": {"displayAppearance": "smoothShaded", "wireframeOnShaded": False, "displayTextures": True},
            "wireframe on textured": {"displayAppearance": "smoothShaded", "wireframeOnShaded": True, "displayTextures": True}
        }
        if option in settings:
            cmds.modelEditor(panel, edit=True, **settings[option]) # 언 패킹으로 위의 딕셔너리 풀러서 값을 바로 보내줍니다.
            print(f"뷰포트 설정 변경: {option}")

    def export_playblast(self):
        """턴테이블 카메라를 생성하고 Playblast 실행"""
        self.make_turntable()

        cmds.lookThru("modelPanel4", "turntable_cam")
        self.save_playblast()
        print(f"Playblast 저장 완료: {self.publish_path}")

    def playblast_publish(self, options):
        """UI 옵션 리스트에 따라 Playblast 실행"""
        for option in options:
            self.set_viewport_option(option)
        self.export_playblast()

if __name__ == "__main__":
    maya_pub = MayaPublish(
        project="Viper", # 프로젝트 이름
        asset_type="prop", # 경로 파일
        asset_name="robot_arm", # 경로 파일
        task="animation", # 작업 분류
        version=2 # 작업물 넘버링
    )

    selected_options = ["shaded", "wireframe on shaded"]
    maya_pub.playblast_publish(selected_options)

    maya_pub.save_alembic(start_frame=1, end_frame=100, selection=True)
