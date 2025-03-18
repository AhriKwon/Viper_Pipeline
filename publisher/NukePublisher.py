import os
import nuke
import importlib
import subprocess
from GeneratingPath import FilePath
from convert_to_mov import FileConverter

class NukePublisher:


    def __init__(self, shot_data):
        """ NukePublisher 초기화 함수.
        :param output_mov_path: 최종mov 파일이 저장될 경로"""

        """기본 shot_data 설정"""
        # 기본값 설정
        default_data = {
            "project": "Viper",
            "task_type": "LGT",
            "seq": None,
            "shot": None,
            "version": 1,
            "start_frame": 1001,
            "last_frame": 1099
        }

        
        # 전달된 shot_data를 기본값에 병합
        default_data.update(shot_data)  # 전달된 shot_data를 덮어씁니다.
        self.shot_data = default_data  # 기본값을 포함한 shot_data 설정

        # 기본값을 포함한 shot_data에서 필요한 항목 추출
        self.project = self.shot_data["project"]
        self.task_type = self.shot_data["task_type"]
        self.seq = self.shot_data["seq"]
        self.shot = self.shot_data["shot"]
        self.version = self.shot_data["version"]
        if default_data["start_frame"] == None:
            self.start_frame = 1001
        else:
            self.start_frame = default_data["start_frame"]
        if default_data["last_frame"] == None:
            self.last_frame = 1099
        else:
            self.last_frame = default_data["last_frame"]

        self.publish_data = {
            "project_name": self.project,
            "shot_name": self.shot,
            "task_name": self.task_type,
            "version": self.version,
            "start_frame": self.start_frame,
            "last_frame": self.last_frame
        }

        # 퍼블리싱 경로 생성
        publish_paths = FilePath.generate_paths(
            self.project, "seq", 
            self.seq, self.shot, self.task_type, self.version
        )
        
        # 각 퍼블리쉬 관련 경로 설정
        self.scene_path = publish_paths["nuke"]["pub_scene"]
        self.mov_path = publish_paths["nuke"]["mov_comp"]
        self.prod_path = publish_paths["nuke"]["mov_product"]

    def publish(self):
        """Nuke Publishing 실행 (씬 렌더링/ MOV 출력)"""
        nuke.scriptSaveAs(self.scene_path)

        publish_paths = [self.mov_path, self.prod_path]

        temp_in_path = publish_paths[0]+".mov"  # 임시 저장 경로
        out_name = f"_v{self.version:03d}.mov" # 출력 파일 이름

        # 영상 렌더 한 번만 실행
        self.export_nukefile(temp_in_path)  # self.prod_path를 두 번째 인자로 전달      

        for publish_path in publish_paths:
            out_path = publish_path+out_name

            # MOV 변환 (레터박스 & 오버레이 적용)
            FileConverter.convert_with_overlay_and_letterbox(temp_in_path, out_path, self.publish_data)

            print(f"Final MOV 생성 완료: {out_path}")

        # 임시 MOV 파일 삭제
        if os.path.exists(temp_in_path):
            os.remove(temp_in_path)

        publish_pathes = {
            "scene path": self.scene_path,
            "playblast path": out_path}
        
        return publish_pathes

    def export_nukefile(self, output_path):
        """Nuke에서 유저가 선택한 Write 노드를 Apple ProRes MOV 파일로 렌더링"""
        selected_write_nodes = [node for node in nuke.selectedNodes() if node.Class() == "Write"]
        if not selected_write_nodes:
            raise RuntimeError("선택한 Write 노드가 없습니다. 렌더링을 중단합니다.")

        for write_node in selected_write_nodes:
            # 출력 경로 설정
            write_node["file"].setValue(output_path)  # 파일 저장 경로 설정

            # MOV 포맷과 Apple ProRes 코덱 설정
            write_node["file_type"].setValue("mov")  # MOV 포맷 설정
            write_node["codec"].setValue("prores")  # ProRes 코덱 설정 (필요한 경우)

            # 렌더 실행
            nuke.execute(write_node, self.shot_data["start_frame"], self.shot_data["last_frame"])
            print(f"렌더링 완료: {write_node['file'].value()}")
