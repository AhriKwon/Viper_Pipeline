import hou
import os
import subprocess
from convert_to_mov_mp4 import FileConverter  # FileConverter class import

class HoudiniPublisher:
    """Houdini에서 ROP 노드를 실행하고, MP4 또는 MOV로 변환하는 클래스"""

    def __init__(self, output_dir="/nas/Viper/hyerin/Publisher"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_all_rop_nodes(self):
        """현재 씬에서 모든 ROP 노드를 가져옴"""
        return [node for node in hou.node("/out").children() if node.type().name() in ["ifd", "karma", "opengl"]]

    def set_output_paths(self, rop_nodes):
        """ROP 노드의 출력 경로를 EXR로 설정"""
        for i, node in enumerate(rop_nodes):
            image_path = os.path.join(self.output_dir, f"render_{i+1}.####.exr")  # Houdini 프레임 패턴 사용
            
            if node.type().name() == "ifd":  # Mantra
                node.parm("vm_picture").set(image_path)
            elif node.type().name() == "karma":  # Karma
                node.parm("picture").set(image_path)
            elif node.type().name() == "opengl":  # OpenGL
                node.parm("output").set(image_path)

            print(f"✅ {node.name()} 경로 설정 완료: {image_path}")

    def execute_rop_nodes(self, rop_nodes):
        """ROP 노드를 실행하여 렌더링"""
        for node in rop_nodes:
            node.render(frame_range=(1, 100), verbose=True)
            print(f"✅ {node.name()} 렌더링 완료!")

    def publish_video(self, format_type="mp4"):
        """Houdini에서 렌더링한 EXR을 MP4 또는 MOV로 변환"""
        rop_nodes = self.get_all_rop_nodes()
        if not rop_nodes:
            print("⚠ Rop 노드가 없습니다.")
            return

        self.set_output_paths(rop_nodes)
        self.execute_rop_nodes(rop_nodes)

        # 변환할 모든 EXR 파일 찾기
        for i in range(len(rop_nodes)):
            input_path = os.path.join(self.output_dir, f"render_{i+1}.%04d.exr")
            output_path = os.path.join(self.output_dir, f"output_{i+1}.{format_type}")
            
            # EXR → MOV 변환 실행
            FileConverter.convert_to_video(input_path, output_path, format_type)
            print(f"✅ {output_path} 변환 완료!")

if __name__ == "__main__":
    houdini_pub = HoudiniPublisher()
    selected_format = "mp4"  # UI에서 선택한 포맷 (mp4 or mov)
    houdini_pub.publish_video(selected_format)

class UIPublisher:
    """UI를 통해 Houdini와 Maya에서 MP4 또는 MOV 변환을 실행하는 클래스"""

    @staticmethod
    def export_from_houdini(format_type):
        houdini_pub = HoudiniPublisher()
        houdini_pub.publish_video(format_type)
