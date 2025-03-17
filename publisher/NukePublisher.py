import os
import nuke
import subprocess
from convert_to_mov import FileConverter
from GeneratingPath import FilePath

class NukePublisher:
    """Nuke에서 씬을 렌더링하고 MOV 파일을 생성하는 클래스"""
    def __init__(self, shot_data):
        """초기화 및 퍼블리싱 경로 설정"""
        default_data = {
            "project": "Viper",
            "entity_type": "seq",
            "task_type": "LGT",
            "seq": None,
            "shot": None,
            "version": 1,
            "start_num": 1,
            "last_num": 99
        }
        default_data.update(shot_data)

        # 프로젝트 정보 및 경로 설정
        self.project = default_data["project"]
        self.entity_type = default_data["entity_type"]
        self.task_type = default_data["task_type"]
        self.seq = default_data["seq"]
        self.shot = default_data["shot"]
        self.version = default_data.get("version", 1)

        self.publish_data = {
            "project_name": self.project,
            "shot_name": self.shot,
            "task_name": self.task_type,
            "version": self.version,
            "start_num": 1,
            "last_num": 99
        }

        # 퍼블리싱 경로 생성
        publish_paths = FilePath.generate_paths(
            self.project, self.entity_type, self.seq, self.shot, self.task_type, self.version
        )

        self.scene_path = publish_paths["nuke"]["pub_scene"]
        self.plb_path = publish_paths["nuke"]["mov_comp"]
        self.prod_path = publish_paths["nuke"]["mov_product"]

        # Nuke 씬을 렌더링하고 MOV 변환 실행
        self.nuke_publish()

    def nuke_publish(self):
        """Nuke에서 씬을 렌더링하고 MOV 변환을 실행"""
        temp_in_path = os.path.join(self.plb_path, "temp.mov")
        out_name = f"_v{self.version:03d}.mov"

        # Nuke 씬을 렌더링하여 임시 MOV 파일 생성
        self.export_nukefile(temp_in_path)

        # Write 노드 가져오기
        write_nodes = self.get_all_write_nodes()
        if not write_nodes:
            print("Write 노드가 없습니다.")
            return

        # 최종 MOV 파일 경로 설정
        for write_node in write_nodes:
            node_name = write_node.name()
            mov_path = os.path.join(self.prod_path, f"{node_name}{out_name}")
            write_node["file"].setValue(mov_path)
            write_node["file_type"].setValue("QuickTime")

        # Write 노드를 실행하여 MOV 파일 렌더링
        self.execute_write_nodes(write_nodes)

        # FFmpeg을 이용한 레터박스 및 오버레이 적용 후 MOV 변환
        FileConverter.convert_with_overlay_and_letterbox(temp_in_path, [self.prod_path], out_name)

        # 임시 MOV 파일 삭제
        if os.path.exists(temp_in_path):
            os.remove(temp_in_path)

    def get_all_write_nodes(self):
        """현재 씬에서 모든 Write 노드를 가져옴"""
        write_nodes = nuke.allNodes("Write")
        if not write_nodes:
            print("경고: Write 노드가 없습니다.")
        return write_nodes

    def execute_write_nodes(self, write_nodes, start_frame=1, end_frame=100, step=1):
        """Write 노드를 실행하여 렌더링 수행"""
        for write_node in write_nodes:
            nuke.execute(write_node, start_frame, end_frame, step)
            print(f"{write_node.name()} 렌더링 완료! ({start_frame}-{end_frame})")

    def export_nukefile(self, temp_in_path):
        """Nuke 씬을 렌더링하여 임시 MOV 파일 생성"""
        write_nodes = self.get_all_write_nodes()
        if not write_nodes:
            return

        for write_node in write_nodes:
            write_node["file"].setValue(temp_in_path)
            self.execute_write_nodes([write_node])

class RVPublisher:
    """Nuke에서 렌더링된 EXR 파일을 RV에서 실행하는 클래스"""
    def __init__(self, shot_data):
        self.rv_path = os.getenv("RV_PATH", "/usr/local/bin/rv")
        self.nuke_pub = NukePublisher(shot_data)

    def launch_rv(self, filename, start_frame=1, end_frame=100):
        """RV에서 렌더링된 EXR 파일을 실행"""
        if not os.path.exists(filename):
            print(f"파일을 찾을 수 없음: {filename}")
            return

        rv_cmd = [
            self.rv_path,
            filename,
            "-play",
            "-frameRange", f"{start_frame}-{end_frame}",
            "-c"
        ]
        subprocess.Popen(rv_cmd, close_fds=True)
        print("RV 실행 완료!")

    def play_published_exr(self):
        """Nuke에서 렌더링된 EXR 파일을 RV에서 실행"""
        write_nodes = self.nuke_pub.get_all_write_nodes()
        if not write_nodes:
            return

        for node in write_nodes:
            filename = os.path.normpath(node["file"].value())
            self.launch_rv(filename)

class UIPublisher:
    """UI에서 Nuke 퍼블리싱을 실행하는 클래스"""
    @staticmethod
    def export_from_nuke(shot_data):
        """Nuke 씬을 렌더링하고 MOV 변환을 실행"""
        NukePublisher(shot_data)

    @staticmethod
    def play_rv_after_publish(shot_data):
        """퍼블리싱된 EXR 파일을 RV에서 실행"""
        rv_pub = RVPublisher(shot_data)
        rv_pub.play_published_exr()

if __name__ == "__main__":
    shot_data = {"project": "ProjectName", "seq": "Seq01", "shot": "Shot01", "task_type": "compositing", "version": 1}
    UIPublisher.export_from_nuke(shot_data)
    UIPublisher.play_rv_after_publish(shot_data)