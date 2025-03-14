import os
import sys
import nuke
import subprocess
from convert_to_mov import FileConverter
from GeneratingPath import FilePath

class NukePublisher:
    # def __init__(self, output_dir):
    #     self.output_dir = output_dir
    #     os.makedirs(self.output_dir, exist_ok=True)  # 디렉토리 존재 여부 확인 후 생성
    def __init__(self, shot_data): 
        # 기본 데이터 설정
        default_data = {
        "project": "Viper",
        "entity_type": "seq",
        "task_type": "LGT",
        "seq": None,
        "shot": None,
        "version": 1,
        "start_num" : 1,
        "last_num" : 99
        }

        # shot_data가 전달되면 기존 default_data를 업데이트
        default_data.update(shot_data)

        self.project = default_data["project"]
        self.entity_type = default_data["entity_type"]
        self.task_type = default_data["task_type"]
        self.seq = default_data["seq"]
        self.shot = default_data["shot"]
        self.version = default_data.get("version", 1)

        # 퍼블리쉬 데이터 설정 (프로젝트명, 샷명, 작업명, 버전 등)
        self.publish_data = {
            "project_name" : self.project,
            "shot_name" : self.shot,
            "task_name" : self.task_type, 
            "version" : self.version,
            "start_num" : 1,
            "last_num" : 99
            }

        # 경로 생성 함수(객체파일) 호출하여 퍼블리쉬 경로 설정
        publish_paths = FilePath.generate_paths(
            shot_data["project"], shot_data["entity_type"], 
            self.seq, self.shot, self.task_type, self.version
            )
        
        # 각 퍼블리쉬 관련 경로 설정
        self.scene_path = publish_paths["nuke"]["pub_scene"]
        self.plb_path = publish_paths["nuke"]["mov_comp"]
        self.prod_path = publish_paths["nuke"]["mov_product"]

        # Nuke 퍼블리쉬 함수 호출
        self.nuke_publish([self.plb_path, self.prod_path])

    def nuke_publish(self, publish_paths):
        """Nuke Publishing 실행 (씬 렌더링/ MOV 출력)"""
        temp_in_path = publish_paths[0]+".mov"  # 임시 저장 경로
        out_name = f"_v{self.version:03d}.mov" # 출력 파일 이름

        # 영상 렌더 한 번만 실행
        self.export_nukefile(temp_in_path) # Nuke 파일 write 노드 받아서 영상 출력

        # Write 노드 설정 및 렌더링
        write_nodes = self.get_all_write_nodes()
        if not write_nodes:
            print("Write 노드가 없습니다.")
            return        
        
        # MOV 파일 출력 경로 설정 및 렌더링
        for write_node in write_nodes:
            node_name = write_node.name()
            mov_path = os.path.join(self.prod_path, f"{node_name}{out_name}")
            write_node["file"].setValue(mov_path) # mov 파일 경로 설정
            write_node["file_type"].setValue("QuickTime") # QuickTime 포맷 설정

        # Write 노드 실행 (렌더링)
        self.execute_write_nodes(write_nodes)

        # MOV 변환 (레터박스 & 오버레이 적용)
        FileConverter.convert_with_overlay_and_letterbox(temp_in_path, publish_paths, out_name)

        # 원본 Playblast 파일 삭제
        if os.path.exists(temp_in_path):
            os.remove(temp_in_path)

    def save_nuke_and_set_paths(self, nuke_file_name):
        """Nuke 파일 저장 및 Write 노드의 경로 설정"""
        nuke_file_path = os.path.join(self.output_dir, nuke_file_name)
        nuke.scriptSaveAs(nuke_file_path)  # Nuke 파일 저장
        print(f"Nuke 파일 저장 완료: {nuke_file_path}")

        write_nodes = self.get_all_write_nodes()
        if not write_nodes:
            print("Write 노드가 없습니다.")
            return

        for write_node in write_nodes:
            node_name = write_node.name()
            exr_path = os.path.join(self.output_dir, f"{os.path.splitext(nuke_file_name)[0]}_{node_name}.####.exr")
            write_node["file"].setValue(exr_path)
            print(f"{write_node.name()} 경로 설정 완료: {exr_path}")
    
    def generate_output_path(self):
        """FilePath의 generate_paths()를 호출하여 output 경로를 생성"""
        paths = FilePath.generate_paths(self.project, "nuke", self.seq, self.shot, self.task)
        # 여기서 "nuke" 카테고리의 mov_product 경로를 output_dir로 설정
        return paths["nuke"]["mov_product"]

    def get_all_write_nodes(self):
        """현재 씬에서 모든 Write 노드 반환"""
        return nuke.allNodes("Write")

    def execute_write_nodes(self, write_nodes, start_frame=1, end_frame=100, step=1):
        """Write 노드를 실행하여 렌더링"""
        for write_node in write_nodes:
            nuke.execute(write_node, start_frame, end_frame, step)
            print(f"{write_node.name()} 렌더링 완료! ({start_frame}-{end_frame})")

    def export_nukefile(self, temp_in_path):
        """ Nuke 파일을 렌더링하여 MOV로 출력"""
        write_nodes = self.get_all_write_nodes()
        if not write_nodes:
            print("Write 노드가 없습니다.")
            return
        
        # 각 Write 노드에 대해 mov 파일 경로 설정 및 렌더링 수행
        for write_node in write_nodes:
            write_node["file"].setValue(temp_in_path) # 임시 mov 파일 경로 설정
            self.execute_write_nodes([write_node]) # write 노드 실행

class RVPublisher:
    """
    Nuke에서 렌더링된 EXR 파일을 자동으로 RV에서 실행하는 클래스
    """
    def __init__(self, shot_data):
        self.rv_path = os.getenv("RV_PATH", "/usr/local/bin/rv")
        self.nuke_pub = NukePublisher(shot_data) # NukePublisher 객체 생성 시 shot_data 전달

    def launch_rv(self, filename, start_frame=1, end_frame=100):
        """RV에서 렌더링된 EXR 이미지 시퀀스를 불러옴"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"RV를 실행할 수 없습니다. 파일을 찾을 수 없음: {filename}")

        rv_cmd = [
            self.rv_path,
            filename,
            "-play",
            "-frameRange", f"{start_frame}-{end_frame}",
            "-c"
        ]

        try:
            subprocess.Popen(rv_cmd, close_fds=True)
            print("RV 실행 완료!")
        except subprocess.CalledProcessError as e:
            print(f"RV 실행 중 오류 발생: {e}")

    def play_published_exr(self):
        """Nuke에서 렌더링된 EXR 파일을 RV에서 실행"""
        write_nodes = self.nuke_pub.get_all_write_nodes()
        if not write_nodes:
            print("Write 노드가 없습니다.")
            return
        
        for node in write_nodes:
            filename = os.path.normpath(node["file"].value())
            self.launch_rv(filename)

if __name__ == "__main__":

    # shot_data 설정
    shot_data = {"project" : "ProjectName", "seq" : "Seq01", "shot" : "Shot01", "task_type" :"compositing", "version" : 1}
    
    # NukePublisher 객체 생성 시 프로젝트, 시퀀스, 샷 및 작업을 전달
    nuke_pub = NukePublisher(shot_data)

    # 경로 생성 및 Nuke 파일 저장
    nuke_pub.save_nuke_and_set_paths("nuke_api_v001.nk")

    # MOV 퍼블리싱
    nuke_pub.publish_mov([nuke_pub.prod_path])

    # RVPublisher 객체 생성 시 shot_data 전달
    rv_pub = RVPublisher(shot_data)
    
    # 렌더링된 EXR 파일을 RV에서 실행
    rv_pub.play_published_exr()

class UIPublisher:
    """UI를 통해 Houdini, Maya, Nuke에서 mov 변환을 실행하는 클래스"""
    @staticmethod
    def export_from_nuke(shot_data):
        nuke_pub = NukePublisher(shot_data)
        nuke_pub.save_nuke_and_set_paths("nuke_api_v001.nk")
        nuke_pub.publish_mov([nuke_pub.prod_path])

    @staticmethod
    def play_rv_after_publish(shot_data):
        rv_pub = RVPublisher(shot_data)
        rv_pub.play_published_exr()