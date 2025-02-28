import os
import sys
import nuke
# sys.path.append(os.path.abspath("/nas/Viper/hyerin/Publisher"))
from publisher.convert_to_mov import FileConverter  # import FileConverter class

class NukePublisher:
    def __init__(self, output_dir="/nas/Viper/hyerin/Publisher"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

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
            exr_path = os.path.join(self.output_dir, f"{os.path.splitext(nuke_file_name)[0]}.####.exr")
            write_node["file"].setValue(exr_path)
            print(f"{write_node.name()} 경로 설정 완료: {exr_path}")

    def get_all_write_nodes(self):
        """현재 씬에서 모든 Write 노드 반환"""
        return nuke.allNodes("Write")

    def execute_write_nodes(self, write_nodes, start_frame=None, end_frame=None, step=1):
        """Write 노드를 실행하여 렌더링"""
        if start_frame is None:
            start_frame = int(nuke.root()["first_frame"].value())  # Nuke 기본 설정 값
        if end_frame is None:
            end_frame = int(nuke.root()["last_frame"].value())

        for write_node in write_nodes:
            nuke.execute(write_node, start_frame, end_frame, step)
            print(f"{write_node.name()} 렌더링 완료! ({start_frame}-{end_frame})")

    def information_path(self, write_nodes, dir_path, nuke_file):
        """Write 노드의 경로를 설정"""
        base_name = os.path.splitext(nuke_file)[0]  # 확장자 제거
        for write_node in write_nodes:
            file_path = os.path.join(dir_path, f"{base_name}.####.exr")
            write_node["file"].setValue(file_path)
            print(f"{write_node.name()} 경로 설정 완료: {file_path}")

    def set_write_nodes_mov(self, write_nodes):
        """Write 노드의 파일 경로를 MOV 포맷으로 설정"""
        for i, write_node in enumerate(write_nodes):
            mov_path = os.path.join(self.output_dir, f"output_{i+1}.mov")
            write_node["file"].setValue(mov_path)
            write_node["file_type"].setValue("QuickTime")  # Nuke에서는 "QuickTime"이 올바른 값
            print(f"{write_node.name()} MOV 경로 설정 완료: {mov_path}")

    def publish_mov(self):
        """Nuke Publishing 실행 (MOV 출력)"""
        write_nodes = self.get_all_write_nodes()
        if not write_nodes:
            print("Write 노드가 없습니다.")
            return
        
        self.set_write_nodes_mov(write_nodes)
        self.execute_write_nodes(write_nodes)  # MOV 렌더링 실행

if __name__ == "__main__":
    nuke_pub = NukePublisher()
    nuke_pub.save_nuke_and_set_paths("nuke_api_v001.nk")  # Nuke 파일 저장 및 경로 설정
    nuke_pub.publish_mov()  # MOV 변환 실행

class UIPublisher:
    """UI를 통해 Houdini, Maya, Nuke에서 mov 변환을 실행하는 클래스"""

    @staticmethod
    def export_from_nuke(format_type):
        nuke_pub = NukePublisher()
        nuke_pub.publish_mov()