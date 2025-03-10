import os
import subprocess
import glob
import platform  # os 확인용
from PIL import Image, ImageDraw, ImageFont

class FileConverter:
    """공통적인 FFmpeg 변환 기능을 포함하는 클래스 EXR -> mov"""
    
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
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"{format_type.upper()} 변환 완료: {output_path}")

    @staticmethod
    def add_letterbox_with_shotinfo(input_path, output_path, shot_info, letterbox_ratio=10):
        """
        jpg/jpeg 또는 mov 파일에 레터박스를 추가하고 샷 정보를 삽입하는 함수
        """
        file_ext = os.path.splitext(input_path)[-1].lower()
        if file_ext in [".mov", ".mp4"]:
            FileConverter._add_letterbox_video(input_path, output_path, shot_info, letterbox_ratio)
        elif file_ext in [".jpg", ".jpeg"]:
            FileConverter._add_letterbox_image(input_path, output_path, shot_info, letterbox_ratio)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다.")
    
    @staticmethod
    def _add_letterbox_video(input_video, output_video, shot_info, letterbox_ratio=10):
        """
        FFmpeg을 사용하여 mov/mp4 파일에 레터박스 및 샷 정보 추가
        ratio(%) of letterbox -> overlay shot info. (상대적인 비율로 레터박스 추가하고, 샷 정보 오버레이)
        :param input_video : 원본 영상 파일 경로
        :param output_video : 레터박스 및 샷 정보가 적용된 최종 영상 파일 경로
        :param shot_info : 오버레이할 샷 정보 (eg. Shot 001 - Scene 05 )
        :param letterbox_ratio : 상하 레터박스 비율 (default : 10%)
        """
        # bring the original footage's resolution
        probe_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0", input_video
        ] 
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            raise RuntimeError(f"FFprobe 실행 실패: {result.stderr}")
        try:
            width, height = map(int, result.stdout.strip().split(','))
        except ValueError:
            raise ValueError(f"해당 영상에서 유효한 해상도를 가져올 수 없습니다: {result.stdout}")

        # The height of letterbox(ratio)
        letterbox_height = int(height * (letterbox_ratio / 100))
        font_size = int(letterbox_height * 0.5)  # Font Size

        # The path of font by systemical diff.
        system_os = platform.system()
        font_path = "C:/Windows/Fonts/courier.ttf" if system_os == "Windows" else "/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf"
        
        # 날짜 추가
        timestamp = FileConverter.get_timestamp()
        draw = ImageDraw.Draw(new_image)

        # 날짜 텍스트 길이 계산
        text_width = draw.textbbox((0, 0), timestamp, font=font)[2]

        # 우측 상단에 날짜 텍스트 추가
        draw.text((width - text_width - 10, letterbox_height - font_size - 5), timestamp, font=font, fill="white")

        # FFmpeg filter 생성하는 명령어 
        ffmpeg_cmd = [
            "ffmpeg", "-i", input_video,
            "-vf",
            f"pad={width}:{height + (letterbox_height * 2)}:{0}:{letterbox_height}:black,"
            "-c:a", "copy", output_video
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"overlay_shot_data is completed! 영상 변환 완료!: {output_video}")
    
    @staticmethod
    def convert_to_mov(output_dir, output_file):
        """
        jpg 이미지 시퀀스를 mov(ProRes)로 변환 후 원본 이미지 삭제
        :param output_dir: 이미지 시퀀스가 저장된 디렉토리
        :param output_file: 변환된 mov 파일 경로
        """
        input_pattern = os.path.join(output_dir, "frame.%04d.jpg")  # jpg 시퀀스 패턴

        # FFmpeg 명령어 실행
        ffmpeg_cmd = [
            "ffmpeg",
            "-r", "24",  # 프레임 속도 설정
            "-i", input_pattern,  # 입력 이미지 시퀀스
            "-c:v", "prores_ks",  # ProRes 코덱
            "-pix_fmt", "yuv422p10le",  # 10bit ProRes 설정
            output_file  # 출력 파일 경로
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"mov 변환 완료:{output_file}")

        # 변환 후 이미지 파일 삭제
        FileConverter.delete_frames(output_dir)

    @staticmethod
    def delete_frames(output_dir):
        """변환 후 이미지 시퀀스 (.jpg) 파일 삭제"""
        image_files = glob.glob(os.path.join(output_dir, "frame.*.jpg")) + glob.glob(os.path.join(output_dir, "frame.*.jpeg"))
        for file in image_files:
            os.remove(file)
        print(f"프레임 이미지 {len(image_files)}개 삭제 완료.")

    @staticmethod
    def _add_letterbox_image(input_image, output_image, shot_info, letterbox_ratio=10):
        """
        PIL을 사용하여 JPG/JPEG 파일에 레터박스 및 샷 정보 추가
        """
        image = Image.open(input_image)
        width, height = image.size
        letterbox_height = int(height * (letterbox_ratio / 100))

        new_height = height + (letterbox_height * 2)
        new_image = Image.new("RGB", (width, new_height), "black")
        new_image.paste(image, (0, letterbox_height))

        draw = ImageDraw.Draw(new_image)
        system_os = platform.system()
        font_path = "C:/Windows/Fonts/arial.ttf" if system_os == "Windows" else "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"
        font_size = int(letterbox_height * 0.5)
        font = ImageFont.truetype(font_path, font_size)

        # 텍스트 길이를 구하는 방법을 수정
        text_width_up_left = draw.textbbox((0, 0), shot_info['up_left'], font=font)[2]
        text_width_up_center = draw.textbbox((0, 0), shot_info['up_center'], font=font)[2]
        text_width_up_right = draw.textbbox((0, 0), shot_info['up_right'], font=font)[2]
        text_width_down_left = draw.textbbox((0, 0), shot_info['down_left'], font=font)[2]
        text_width_down_center = draw.textbbox((0, 0), shot_info['down_center'], font=font)[2]
        text_width_down_right = draw.textbbox((0, 0), shot_info['down_right'], font=font)[2]

        # 상단 우측에 날짜 텍스트 추가
        timestamp = FileConverter.get_timestamp()
        text_width = draw.textbbox((0, 0), timestamp, font=font)[2]
        draw.text((width - text_width - 10, letterbox_height - font_size - 5), timestamp, font=font, fill="white")

        draw.text((10, letterbox_height - font_size - 5), shot_info['up_left'], font=font, fill="white")
        draw.text(((width - text_width_up_center) // 2, letterbox_height - font_size - 5), shot_info['up_center'], font=font, fill="white")
        draw.text((width - text_width_up_right - 10, letterbox_height - font_size - 5), shot_info['up_right'], font=font, fill="white")

        draw.text((10, new_height - letterbox_height - 10), shot_info['down_left'], font=font, fill="white")
        draw.text(((width - text_width_down_center) // 2, new_height - letterbox_height - 10), shot_info['down_center'], font=font, fill="white")
        draw.text((width - text_width_down_right - 10, new_height - letterbox_height - 10), shot_info['down_right'], font=font, fill="white")

        new_image.save(output_image)
        print(f"이미지 변환 완료: {output_image}")
