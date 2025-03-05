import os
import subprocess
import glob

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
    @staticmethod
    def convert_to_mov(output_dir, output_file):
        """
        jpg 이미지 시퀀스를 mov(ProRes)로 변환 후 원본 이미지 삭제
        :param output_dir: 이미지 시퀀스가 저장된 디렉토리
        :param output_file: 변환된 mov 파일 경로
        """
        input_pattern = os.path.join(output_dir, "frame.%04d.jpg") # jpg 시퀀스 패턴

        # FFmpeg 명령어 실행
        ffmpeg_cmd = [
            "ffmpeg",
            "-r", "24", # 프레임 속도 설정
            "-i", input_pattern, # 입력 이미지 시퀀스
            "-c:v", "prores_ks", # ProRes 코덱
            "-pix_fmt", "yuv422p10le", # 10bit ProRes 설정
            output_file # 출력 파일 경로
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"mov 변환 완료:{output_file}")

        # 변환 후 이미지 파일 삭제
        FileConverter.delete_frames(output_dir)

        @staticmethod
        def delete_frames(output_dir):
            """
            변환 후 이미시 시퀀스 (.jpg) 파일 삭제
            :param output_dir: 이미지 시퀀스가 저장된 디렉토리 
            """
            image_files = glob.glob(os.path.join(output_dir, "frame.*.jpg")) # frame.0001.jpg 등 찾기
            for file in image_files:
                os.remove(file)
            print(f"프레임 이미지 {len(image_files)}개 삭제 완료.")
