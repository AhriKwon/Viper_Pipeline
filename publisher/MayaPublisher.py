import os
import sys
import shutil
from pathlib import Path
import maya.cmds as cmds
from GeneratingPath import FilePath
from convert_to_mov import FileConverter

sys.path.append("nas/Viper/hyerin/Publisher") # Linux os

class MayaPublisher():

    def __init__(self, project, entity_type, task_type, asset_type=None, name=None, seq=None, shot=None, version=1):
        self.task_type = task_type
        self.asset_type = asset_type
        self.name = name
        self.seq = seq
        self.shot = shot
        self.version = version
        self.publish_data = {} 
        
        if asset_type:
            publish_paths = FilePath.generate_paths(project, entity_type, asset_type, name, task_type, version)
        elif seq:
            publish_paths = FilePath.generate_paths(project, entity_type, seq, shot, task_type, version)

        self.scene_path = publish_paths["maya"]["pub_scene"]
        self.plb_path = publish_paths["maya"]["mov_plb"]
        self.prod_path = publish_paths["maya"]["mov_product"]
        self.abc_path = publish_paths["maya"]["abc_cache"]
        
    def publish(self):
     # Task 유형에 맞는 퍼블리쉬 실행
        if self.task_type in ["MDL", "RIG", "TXT"]:
            self._publish_asset()
        elif self.task_type in ["MM", "LAY", "ANM"]:
            self._publish_shot()

    def _publish_asset(self): # MDL, RIG, TXT 퍼블리쉬 실행

        # Maya 씬 저장 (.ma)
        cmds.file(rename=self.scene_path)
        cmds.file(save=True, type="mayaAscii")

        # Alembic Cache 만들기
        self.save_alembic(self.abc_path)

        # Playblast 만들기
        self.make_turntable()
        self.export_playblast(self.plb_path)
        self.export_playblast(self.prod_path)
        print(f"{self.task_type} Publishing is completed!!")
        
    def _publish_shot(self):        
        # MM, LAY, ANM 퍼블리쉬 실행

        # Maya 씬 저장 (.ma)
        cmds.file(rename=self.scene_path)
        cmds.file(save=True, type="mayaAscii")

        # Alembic Cache 만들기
        self.save_alembic(self.abc_path)

        # Playblast 만들기

        self.export_playblast(self.plb_path)
        self.export_playblast(self.prod_path)
        print(f"{self.task_type} Publishing is completed!!")

    def save_alembic(self):

        # 다중선택된 오브젝트들을 개별적으로 Alembic(.abc) 파일저장
        # 자동으로 그룹 전체를 선택, for 문으로 save alembic을 실행해주는 함수
        
        # 씬 내 모든 transform 노드 검색 (최상위 그룹 포함)
        all_transforms = cmds.ls(type="transform", long=True)

        # Alembic 내보낼 그룹 필터링 (자식이 있는 transform만 선택)
        groups = list(set(cmds.listRelatives(all_transforms, parent=True)))
        if not groups:
            print("Error: Alembic 내보낼 그룹이 없습니다.")
            return

        for grp in groups:
            cmds.select(grp, replace=True)
            asset_name = grp.split("_")[0] # split()을 사용하여 문자열을 분리하고 첫 번째 요소만 반환
            file_name = f"{asset_name}_{self.task_type}_v{self.version:03d}.abc"
            full_path = Path(self.abc_path) / file_name

            # Alembic Export 실행
            alembic_command = f"{grp} -file {full_path}"
        
        try:
            # Alembic 내보내기 명령어 실행
            cmds.AbcExport(j=alembic_command)
            print(f"Alembic 저장되었습니다: {full_path}")
            
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
            format="qt", #QuickTime(.mov)형식 "image"를 사용하면 프레임 이미지 시퀀스로 저장할 수도 있음
            filename=output_path, # .mov 확장자를 붙이면 QuickTime 동영상 파일로 저장됨
            sequenceTime=False, # True: 씬 타임라인 기준으로 시퀀스 출력, False: 현재 프레임 번호 기준 출력(일반적인playblast)
            clearCache=True, # playblast 실행 전 cache 비움 True: 메모리 캐시 지우고, 새롭게 실행, False: 캐시 유지, 반복실행시 속도 빠름
            viewer=False, # True: 파일 생성시 뷰어에서 자동 재생, False: 자동 실행 -> x (파일저장만)
            showOrnaments=False, # 뷰포트 내 오버레이 UI(타임코드, 그리드 등) 표시 여부, True: 타임코드, FPS, HUD, False: Clean ver. Render
            framePadding=4, # 파일명에 붙는 프레임 넘버의 자리수 지정
            percent=100, # 출력 해상도 비율 조정
            compression="jpeg", # 비디오 압축 방식 선택
            quality=100, # 비디오 품질 설정 (0~100)
            forceOverwrite=True, # 같은 이름 파일 덮어쓰기, False -> 오류 가능성 높아짐
            widthHeight=(1920, 1080), # 출력 해상도 FHD, 3840x2160 -> 4K
            startTime=1, # 시작 프레임 설정
            endTime=99 # 종료 프레임 설정
        )
        print(f"Playblast 저장 완료: {output_path}")

    def set_viewport_option(self, option):
        # 현재 활성화된 모델 패널을 가져옴
        # panel = cmds.getPanel(withFocus=True)
        panel = "modelPanel4" # <-- linux 에서 test용
        if option == "shaded":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=False, displayTextures=False)
        elif option == "wireframe on shaded":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=True, displayTextures=False)
        elif option == "textured":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=False, displayTextures=True)
        elif option == "wireframe on textured":
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded", wireframeOnShaded=True, displayTextures=True)

        print(f"뷰포트 설정 변경: {option}")

    def export_playblast(self, publish_paths):
        
        """씬안에 새로 생성된 카메라를 사용하여 Playblast 실행"""
        all_cameras = cmds.ls(type="camera", long=True)
        scene_cameras = [cam for cam in all_cameras if "persp" not in cam and "top" not in cam and "side" not in cam and "front" not in cam]

        if not scene_cameras:
            self.make_turntable()
            all_cameras = cmds.ls(type="camera", long=True)
            scene_cameras = [cam for cam in all_cameras if "persp" not in cam and "top" not in cam and "side" not in cam and "front" not in cam]

        camera_to_use = scene_cameras[0]
        # panel = cmds.getPanel(withFocus=True)
        panel = "modelPanel4" # <-- 이거 테스트용
        cmds.lookThru(panel, camera_to_use) # lookThru() 특정 뷰패널을 특정 카메라로 전환하는 명령어!
        cmds.viewFit(all=True) # 씬 전체에 맞게 뷰 핏

        print(f"뷰포트 카메라 설정 완료: {camera_to_use}") 
        
        self.save_playblast(publish_paths)

    def playblast_publish(self, options):
        """UI 옵션 리스트에 따라 Playblast 실행"""
        for option in options:
            self.set_viewport_option(option)
            self.export_playblast()
   
if __name__ == "__main__":
    maya_pub = MayaPublisher()
    selected_options = ["shaded", "wireframe on shaded"]
    maya_pub.playblast_publish(selected_options)
    maya_pub.save_alembic()
    