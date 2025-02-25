import os
import subprocess

class FileConverter:
    """공통적인 FFmpeg 변환 기능을 포함하는 클래스"""

    @staticmethod
    def convert_to_video(input_path, output_path, format_type="mp4"):
        """
        FFmpeg를 사용하여 EXR 시퀀스를 비디오 파일로 변환
        :param input_path: 변환할 이미지 시퀀스 경로
        :param output_path: 생성될 비디오 파일 경로
        :param format_type: 변환할 비디오 형식 (mp4 or mov)
        """
        if format_type == "mp4":
            codec = "libx264"
            pix_fmt = "yuv420p"
        elif format_type == "mov":
            codec = "prores_ks"  # 고품질 ProRes 변환을 위해 'prores_ks' 사용
            pix_fmt = "yuv422p10le"
        else:
            raise ValueError("지원하지 않는 형식입니다. 'mp4' 또는 'mov'만 가능합니다.")

        ffmpeg_cmd = [
            "ffmpeg",
            "-framerate", "24",
            "-i", input_path,
            "-c:v", codec,
            "-pix_fmt", pix_fmt,
            output_path
        ]
        subprocess.run(ffmpeg_cmd, shell=True)
        print(f"{format_type.upper()} 변환 완료: {output_path}")
