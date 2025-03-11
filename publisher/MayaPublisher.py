import os
import sys
import json
from pathlib import Path
import maya.cmds as cmds
from GeneratingPath import FilePath
from convert_to_mov import FileConverter
sys.path.append("nas/Viper/hyerin/Publisher") # Linux os

class MayaPublisher():
    """
    Maya Publishing Process Managing Class
    씬 저장, Alembic 내보내기, Playblast 생성, 그리고 FFmpeg을 통한 mov 컨버팅 포함(객체 파일로 수행) 
    """
    def __init__(self, shot_data):
    # 기본값을 설정한 후 shot_data에서 받은 값으로 덮어쓰기
        default_data = {
        "project": "Viper",
        "entity_type": "assets",
        "task_type": "MDL",
        "options": ["shaded", "wireframe"],
        "asset_type": None,
        "name": None,
        "seq": None,
        "shot": None,
        "version": 1
        }
    
        # shot_data가 전달되면 기존 default_data를 업데이트
        default_data.update(shot_data)

        # 클래스 속성 할당
        self.project = default_data["project"]
        self.entity_type = default_data["entity_type"]
        self.task_type = default_data["task_type"]
        self.options = default_data["options"]
        self.asset_type = default_data["asset_type"]
        self.name = default_data["name"]
        self.seq = default_data["seq"]
        self.shot = default_data["shot"]
        self.version = default_data["version"]
        self.publish_data = {}
        
        # 경로 생성 로직 (seq or asset_type에 따라 다르게 처리)
        if self.asset_type:
            publish_paths = FilePath.generate_paths(
                shot_data["project"], shot_data["entity_type"], 
                self.asset_type, self.name, self.task_type, self.version
                )
        elif self.seq:
            publish_paths = FilePath.generate_paths(
                shot_data["project"], shot_data["entity_type"], 
                self.seq, self.shot, self.task_type, self.version
                )

        self.scene_path = publish_paths["maya"]["pub_scene"]
        self.plb_path = publish_paths["maya"]["mov_plb"]
        self.prod_path = publish_paths["maya"]["mov_product"]
        self.abc_path = publish_paths["maya"]["abc_cache"]
        
        # LDV 작업일 경우에만 쉐이더 파일 경로 추가
        if self.task_type == "LDV":
            self.shader_ma_path = publish_paths["maya"].get("shader_ma", None)
            self.shader_json_path = publish_paths["maya"].get("shader_json", None)

            if not self.shader_ma_path or not self.shader_json_path:
                print("Warning: Shader export paths are not defined in the publishing paths.")
        
    def publish(self): # Task 유형에 맞는 퍼블리쉬 실행
        if self.task_type in ["MDL", "RIG", "LDV"]:
            self._publish_asset()
            if self.task_type == "LDV":
                self._publish_shader()
        elif self.task_type in ["MM", "LAY", "ANM"]:
            self._publish_shot()
    
    def export_shader(ma_output_path):
        """
        현재 선택된 오브젝트에 연결된 쉐이더를 포함한 .ma 파일로 저장
        """
        selection = cmds.ls(selection=True) # 현재 선택된 오브제 목록 가져오기
        
        if not selection: # 선택된 오브제 없으면 오류 메세지 출력
            print("Error: No object selected.")
            return
       
        # 선택된 오브제와 연결된 쉐이딩 엔진(Shading Engine) 찾기
        shading_engines = cmds.listConnections(selection, type="shadingEngine")
        if not shading_engines: # 쉐이딩 엔진 없으면 오류 메세지 출력
            print("Error: No shading engine connected.")
            return
        
        # copy network, and save as new file : 현재 마야 파일을 새 경로에 저장(ASCII)
        cmds.file(rename=ma_output_path) # 파일 이름 변경
        cmds.file(save=True, type="mayaAscii") # ASCII 파일 형식으로 저장
        print(f"Shader exported to : {ma_output_path}") # 저장 완료 메세지 출력
    
    def save_shader_info_json(json_output_path):
        """
        현재 선택된 오브젝트에 연결된 쉐이더 정보를 JSON으로 저장
        """
        selection = cmds.ls(selection=True) # 선택된 오브제 목록 가져오기
        if not selection:
            print("Error: No object selected.") # 선택된 오브제 없으면 오류 메세지 출력
            return
        
        # 선택된 오브제와 연결된 쉐이딩 엔진 찾기
        shading_engines = cmds.listConnections(selection, type="shadingEngine")
        if not shading_engines: # 쉐이딩 엔진이 없으면 오류 메세지 출력
            print("Error: No shading engine connected.")
            return
        
        # 쉐이더 정보 저장할 딕셔너리 생성
        shader_info = {}
        for sg in shading_engines: # 각 쉐이딩 엔진에 대해 반복
            # 쉐디딩 엔진(SG)과 연결된 쉐이더 찾기
            shaders = cmds.listConnections(sg + ".surfaceShader")
            if shaders: # 쉐이더가 존재하면 딕셔너리에 저장
                shader_info[sg] =  shaders[0] # {쉐이딩 엔진 : 쉐이더 이름} 형태로 저장

        # JSON file 로 저장
        with open(json_output_path, "w") as f:
            json.dump(shader_info, f, indent=4) # JSON 파일로 저장 (들여쓰기 포함)

        print(f"Shader information saved to: {json_output_path}") # 저장 완료 메세지 출력

    
    def _publish_shader(self): # LDV에서 하나의 오브제에 연결된 쉐이더 값 받아와서 퍼블리쉬
        """
        LDV 퍼블리쉬 : 쉐이더를 .ma & .json 파일로 저장
        """
        os.makedirs(os.path.dirname(self.shader_ma_path), exist_ok=True) # 폴더가 없으면 자동으로 생성
        
        # 쉐이더를 .ma 파일로 저장
        self.export_shader(self.shader_ma_path)

        # 쉐이더 정보를 Json 파일로 저장
        self.save_shader_info_json(self.shader_json_path)
        print(f"Shader Publishing completed: {self.shader_ma_path}, {self.shader_json_path}")
        
    def _publish_asset(self): # MDL, RIG, TXT 퍼블리쉬 실행

        # Maya 씬 저장 (.ma)
        if not os.path.exists(self.scene_path):
            os.makedirs(self.scene_path)
        cmds.file(rename=self.scene_path)
        cmds.file(save=True, type="mayaAscii")

        print ("publish asset")

        # Alembic Cache 만들기
        self.save_alembic()

        print ("alembic 나옴.")


        print ("턴테이블 만들기 시작")
        # Playblast 만들기
        self.make_turntable()
        self.playblast_publish(self.options, self.plb_path)
        self.playblast_publish(self.options, self.prod_path)
        print(f"{self.task_type} Publishing is completed!!")

        """ playblast 실행 후 사용한 카메라 그룹을 지워주는 코드 하나 추가"""
        cmds.delete("turntable_cam_grp")

    def _publish_shot(self):        
        # MM, LAY, ANM 퍼블리쉬 실행

        if not os.path.exists(self.scene_path):
            os.makedirs(self.scene_path)
        # Maya 씬 저장 (.ma)
        cmds.file(rename=self.scene_path)
        cmds.file(save=True, type="mayaAscii")

        # Alembic Cache 만들기
        self.save_alembic()

        # Playblast 만들기
        self.playblast_publish(self.options, self.plb_path)
        self.playblast_publish(self.options, self.prod_path)
        print(f"{self.task_type} Publishing is completed!!")

    def save_alembic(self):

        # 다중선택된 오브젝트들을 개별적으로 Alembic(.abc) 파일저장
        # 자동으로 그룹 전체를 선택, for 문으로 save alembic을 실행해주는 함수
        
        if not os.path.exists(self.abc_path):
            os.makedirs(self.abc_path)
            print(f"Alembic 경로가 존재하지 않아 생성되었습니다: {self.abc_path}")

        # 씬 내 모든 transform 노드 검색 (최상위 그룹 포함)
        all_transforms = cmds.ls(type="transform", long=True) or []
        
        if not all_transforms:
            print("Error: 씬에 변환 가능한 오브젝트가 없습니다.")
            return

        # Alembic 내보낼 그룹 필터링 (자식이 있는 transform만 선택)
        groups = list(set(cmds.listRelatives(all_transforms, parent=True) or []))
        if not groups:
            print("Error: Alembic 내보낼 그룹이 없습니다.")
            return

        for grp in groups:
            cmds.select(grp, replace=True)
            asset_name = grp.split("_")[0] # split()을 사용하여 문자열을 분리하고 첫 번째 요소만 반환
            file_name = f"{asset_name}_{self.task_type}_v{self.version:03d}.abc"
            full_path = Path(self.abc_path) / file_name

            # Alembic Export 실행
            alembic_command = f"-frameRange 1 100 -root {grp} -file {full_path}"
            cmds.AbcExport(j=alembic_command)

        try:
            # Alembic 내보내기 명령어 실행
            cmds.AbcExport(j=alembic_command)
            print(f"Alembic 저장되었습니다: {full_path}")
            
        except Exception as e:
            print(f"Error: Alembic 내보내기 실패 - {str(e)}")

    def playblast_publish(self, options, publish_path):
        """UI 옵션 리스트에 따라 Playblast 실행"""
        for option in options:
            self.set_viewport_option(option)
            type_name = option.replace(" ", "")
            in_name = f"_{type_name}.mov"
            in_path = publish_path+in_name
            out_name = f"_{type_name}_v{self.version:03d}.mov"
            out_path = publish_path+out_name

            # Playblast 실행
            self.export_playblast(in_path)

            # FFmpeg을 사용한 변환 및 레터박스 + 오버레이 적용

            FileConverter.convert_with_overlay_and_letterbox(in_path, out_path, "test", "test1", "test3", "test4", 1, 100)
            
            # 원본 Playblast 파일 삭제
            if os.path.exists(in_path):
                os.remove(in_path)
            
            print(f"Final MOV 생성 완료: {out_path}")

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

        print(f"Turntable Camera '{cam_name}' created from frame {start_frame} to {end_frame}.")

    @staticmethod
    def save_playblast(output_path):
        """Playblast 실행 후 저장"""
        
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

    def export_playblast(self, publish_path):
        
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
        
        self.save_playblast(publish_path)
    
# if __name__ == "__main__":
#     maya_pub = MayaPublisher()
#     selected_options = ["shaded", "wireframe on shaded"]
#     maya_pub.playblast_publish(selected_options)
#     maya_pub.save_alembic()
    