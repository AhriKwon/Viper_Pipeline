import os
import sys
import json
from pathlib import Path   
import maya.cmds as cmds
from GeneratingPath import FilePath
from convert_to_mov import FileConverter

class MayaPublisher():
    """
    Maya Publishing Process Managing Class
    씬 저장, Alembic 내보내기, Playblast 생성, 그리고 FFmpeg을 통한 mov 컨버팅 포함(객체 파일로 수행) 
    """
    def __init__(self, shot_data): 
        # 기본 데이터 설정
        default_data = {
        "project": "Viper",
        "entity_type": "assets",
        "task_type": "MDL",
        "options": ["shaded", "wireframe"],
        "asset_type": None,
        "name": None,
        "seq": None,
        "shot": None,
        "version": 1,
        "start_frame" : 1001,
        "last_frame" : 1099
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
        self.start_frame = default_data["start_fram"]
        self.last_frame = default_data["last_fram"]
        
        shot_name = self.name if self.name else self.shot
        self.publish_data = {
            "shot_name" : shot_name,
            "project_name" : self.project,
            "task_name" : self.task_type, 
            "version" : self.version,
            "start_num" : self.start_frame,
            "last_num" : self.last_frame
            }
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
        # 각 퍼블리쉬 관련 경로 설정
        self.scene_path = publish_paths["maya"]["pub_scene"]
        self.plb_path = publish_paths["maya"]["mov_plb"]
        self.prod_path = publish_paths["maya"]["mov_product"]
        self.abc_path = publish_paths["maya"]["abc_cache"]
        
        # LDV 작업일 경우에만 쉐이더 파일 경로 추가
        if self.task_type == "LDV":
            if "shader_ma" in publish_paths["maya"] and "shader_json" in publish_paths["maya"]:
                self.shader_ma_path = publish_paths["maya"]["shader_ma"]
                self.shader_json_path = publish_paths["maya"]["shader_json"]
            else:
                print("Warning: Shader export paths are not defined in the publishing paths.")
                self.shader_ma_path = None
                self.shader_json_path = None
        
        self.publish()
        
    def publish(self): # Task 유형에 맞는 퍼블리쉬 실행
        if self.task_type in ["MDL", "RIG", "LDV"]: 
            # Asset 퍼블리쉬 실행
            self._publish_asset()

            # LDV 작업일 경우 쉐이더 퍼블리쉬 실행
            if self.task_type == "LDV":
                self._publish_shader()

        elif self.task_type in ["MM", "LAY", "ANM"]:
            # Shot 퍼블리쉬 작업
            self._publish_shot()
        
        elif self.task_type in ["LGT"]:
            # 라이팅 렌더 작업
            self._publish_light()

    def get_shaders(self):
        shading_groups = cmds.ls(type="shadingEngine")
        
        shader_dict = {}
        shaders = []

        for sg in shading_groups:
            shader = cmds.listConnections(f"{sg}.surfaceShader", source=True, destination=False) or []
            if shader:
                shaders.append(shader[0])  # 쉐이더 이름 리스트 저장

        return shaders      

    def export_shader(self, ma_output_path):   
        """
        현재 선택된 오브젝트에 연결된 쉐이더를 포함한 .ma 파일로 저장
        """
        shader_info = self.get_shaders()
        if not shader_info:
            raise ValueError("Error: No shader to export.") # 쉐이더 정보가 없을 경우 예외 처리
        cmds.select(shader_info)
        # 경로가 없으면 생성
        os.makedirs(os.path.dirname(ma_output_path), exist_ok=True)
        # 쉐이더만 포함하여 내보내기
        cmds.file(ma_output_path, force=True, exportSelected=True, type="mayaAscii")
        # 선택 해제
        cmds.select(clear=True)
        print(f"Shader exported to : {ma_output_path}") # 저장 완료 메세지 출력
    
    def save_shader_info_json(self, json_output_path):
        """선택된 오브젝트의 쉐이더 정보를 JSON 파일로 저장"""
        shader_info = self.get_shaders()  # 이미 선택된 쉐이더 정보를 가져옴
        if not shader_info:
            raise ValueError("Error: No shaders to save.")  # 쉐이더 정보가 없을 경우 예외 처리
        os.makedirs(os.path.dirname(json_output_path), exist_ok=True)  # 경로가 존재하지 않으면 생성

        # JSON 파일로 저장
        with open(json_output_path, "w") as f:
            json.dump(shader_info, f, indent=4)  # JSON 파일로 저장 (indent : 들여쓰기 값 지정)
        print(f"Shader information saved to: {json_output_path}")  # 저장 완료 메시지 출력

    def _publish_shader(self): # LDV에서 하나의 오브제에 연결된 쉐이더 값 받아와서 퍼블리쉬
        """LDV 퍼블리쉬 : 쉐이더를 .ma & .json 파일로 저장"""
        os.makedirs(os.path.dirname(self.shader_ma_path), exist_ok=True) # 폴더가 없으면 자동으로 생성
        self.export_shader(self.shader_ma_path) # 쉐이더를 .ma 파일로 저장
        self.save_shader_info_json(self.shader_json_path) # 쉐이더 정보를 Json 파일로 저장
        
        print(f"Shader Publishing completed: {self.shader_ma_path}, {self.shader_json_path}")
    
    def check_valid_path(path):
        if path is None or not isinstance(path, str) or path.strip() == "":
            raise ValueError(f"유효하지 않은 경로입니다: {path}")
        return path
        
    def _publish_asset(self): # MDL, RIG, TXT 퍼블리쉬 실행

        # Maya 씬 저장 (.ma)
        if not os.path.exists(self.scene_path): # 경로가 없으면 생성
            os.makedirs(self.scene_path) # 경로 생성
        cmds.file(rename=self.scene_path) # 파일 이름 변경
        cmds.file(save=True, type="mayaAscii") # ASCII 파일 형식으로 저장

        # Alembic Cache 만들기
        self.save_alembic()

        # Playblast 만들기
        self.make_turntable()
        self.playblast_publish(self.options, [self.plb_path, self.prod_path])
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
        self.playblast_publish(self.options, [self.plb_path, self.prod_path])
        print(f"{self.task_type} Publishing is completed!!")
    
    def _publish_light(self):
        
        if not os.path.exists(self.scene_path):
            os.makedirs(self.scene_path)
            # Maya 씬 저장 (.ma)
        cmds.file(rename=self.scene_path)
        cmds.file(save=True, type="mayaAscii")

        # 씬 렌더링
        self.publish_lighting()

    def publish_lighting(self):
        """
        라이팅 퍼블리쉬 자동화 ㅣ render presets + batch render execution
        """
        output_dir = f"/nas/show/{self.project}/seq/{self.seq}/{self.shot}/{self.task_type}/pub/maya/images/v{self.version:03d}/"
        self.apply_render_settings()
        self.start_batch_render(output_dir)

    def get_renderable_camera(self):
        """
        씬 내부에서 렌더링 가능한 카메라를 찾아 반환
        기본 persp 카메라는 제외하고, 사용자 지정 카메라를 반환
        """
        cameras = cmds.ls(type="camera")  # 씬의 모든 카메라 가져오기
        render_cameras = [cam for cam in cameras if not cmds.camera(cam, query=True, startupCamera=True)]

        if not render_cameras:
            raise ValueError("Error: No renderable camera found in the scene. 카메라를 지정하세요.")

        return render_cameras[0]  # 첫 번째 렌더 카메라 반환

    def update_frame_range(self, start, end):
        """샷그리드에서 받아온 프레임 범위를 업데이트하는 자리"""
        self.render_settings["start_frame"] = start
        self.render_settings["end_frame"] = end

    def apply_render_settings(self):
        """
        렌더링 세팅을 자동으로 적용
        """
        self.render_settings = {
            "resolution": (1920, 1080),  # HD_1080 preset
            "camera": self.get_renderable_camera(),
            "start_frame": self.start_frame,
            "end_frame": self.last_frame 
        }

        cmds.setAttr("defaultRenderGlobals.imageFormat", 51)  # 51은 -> EXR 렌더 포맷 지시  (image format)
        cmds.setAttr("defaultRenderGlobals.animation", 1)  # Animation 활성화
        cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)  # name.#.ext 설정

        cmds.setAttr("defaultResolution.width", self.render_settings["resolution"][0])
        cmds.setAttr("defaultResolution.height", self.render_settings["resolution"][1])

        cmds.setAttr("defaultRenderGlobals.startFrame", self.render_settings["start_frame"])
        cmds.setAttr("defaultRenderGlobals.endFrame", self.render_settings["end_frame"])

        # 렌더 카메라 설정
        render_cam = self.render_settings["camera"]
        cmds.setAttr(f"{render_cam}.renderable", 1)

        # 기본 persp 카메라는 렌더링 제외
        if cmds.objExists("persp"):
            cmds.setAttr("persp.renderable", 0)

        # 파일 이름 프리픽스 설정
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "<Scene>", type="string")

        print(" Render settings applied successfully.")

    def start_batch_render(self, output_dir):
        """
        배치 렌더 실행
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 렌더 엔진 확인 (Arnold)
        current_renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")
        if current_renderer not in ["arnold", "mayaSoftware", "redshift"]:
            raise ValueError(f"Unsupported renderer: {current_renderer}")
        
        cmds.setAttr("defaultArnoldRenderOptions.skipLicenseCheck", 1)
        cmds.setAttr("defaultArnoldRenderOptions.ignoreLights", 0)
        
        # 배치 렌더 실행 명령 (Arnold)
        cmds.arnoldRender(batch=True)

        print(f"Batch render started. Output: {output_dir}")

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

    def playblast_publish(self, options, publish_paths):
        """UI 옵션 리스트에 따라 Playblast 실행 및 최적화"""
        
        for option in options:
            self.set_viewport_option(option)
            type_name = option.replace(" ", "")
            in_name = f"_{type_name}.mov"
            temp_in_path = publish_paths[0]+in_name  # 임시 저장 경로
            self.out_name = f"_{type_name}_v{self.version:03d}.mov"

            # Playblast 한 번만 실행
            self.export_playblast(temp_in_path)

            for publish_path in publish_paths:
                out_path = publish_path+self.out_name

                # FFmpeg 변환 (레터박스 & 오버레이 적용)
                FileConverter.convert_with_overlay_and_letterbox(temp_in_path, out_path, self.publish_data)

                print(f"Final MOV 생성 완료: {out_path}")

            # 원본 Playblast 파일 삭제
            if os.path.exists(temp_in_path):
                os.remove(temp_in_path)

    def make_turntable(self, cam_name="turntable_cam", start_frame=1001, end_frame=1100):
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

    def save_playblast(self, output_path):
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
            startTime=self.start_frame, # 시작 프레임 설정
            endTime=self.last_frame # 종료 프레임 설정
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
        
    