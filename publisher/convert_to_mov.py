import os
import subprocess
import glob
import platform # os 확인용

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
    def add_letterbox_with_shotinfo(input_video, output_video, shot_info, letterbox_ratio=10):
        """
        ratio(%) of letterbox -> overlay shot info. (상대적인 비율로 레터박스 추가하고, 샷 정보 오버레이)
        :param input_video : 원본 영상 파일 경로
        :param output_video : 레터박스 및 샷 정보가 적용된 최종 영상 파일 경로
        :param shot_info : 오버레이할 샷 정보 (eg. Shot 001 - Scene 05 )
        :param letterbox_ratio : 상하 레터박스 비율 (default : 10%)
        """

        # bring the original footage's resolution
        probe_cmd = [
            "ffprobe", "-v" , "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0", input_video
        ] 
            # ffprobe(FFmpeg 분석 도구실행), -v error(로그 레벨 설정), -select_streams v:0 (첫 번째 비디오 스트림 선택, -오디오&자막 제외)
            # -show_entries stream=width,height (가로, 세로 값만 출력), -of csv(출력 형식을 csv(쉼표로 지정된 값)로 지정) p=0 (헤더x 순수 데이터만 출력)
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            raise RuntimeError(f"FFprobe 실행 실패: {result.stderr}")
        try:
            width, height = map(int, result.stdout.strip().split(','))
        except ValueError:
            raise ValueError(f"해당 영상에서 유효한 해상도를 가져올 수 없습니다: {result.stdout}")

        # The height of letterbox(ratio)
        letterbox_height = int(height * (letterbox_ratio / 100))
        font_size = int(letterbox_height * 0.5) # Font Size

        # The path of font by systemical diff.
        system_os = platform.system()
        if system_os == "Windows": 
            font_path = "C:/Windows/Fonts/cour/.ttf" # Windows 기본 Courier font
        else:
            font_path = "/usr/share/fonts/truetyipe/msttcorefonts/Courier_New.ttf" # Mac, Linux os

        # FFmpeg filter 명령어 
        ffmpeg_cmd = [
            "ffmpeg", "-i", input_video,
            "-vf",
            f"pad={width}:{height + (letterbox_height * 2)}:{0}:{letterbox_height}:black,"
            f"drawtext=text='{shot_info['up_left']}':x=10:y={letterbox_height - font_size - 5}:"
            f"fontsize={font_size}:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:"
            f"fontfile='{font_path}',"
            f"drawtext=text='{shot_info['up_center']}':x=(w-text_w)/2:y={letterbox_height - font_size - 5}:"
            f"fontsize={font_size}:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:"
            f"fontfile='{font_path}',"
            f"drawtext=text='{shot_info['up_right']}':x=w-text_w-10:y={letterbox_height - font_size - 5}:"
            f"fontsize={font_size}:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:"
            f"fontfile='{font_path}',"
            f"drawtext=text='{shot_info['down_left']}':x=10:y=h-{letterbox_height}-10:"
            f"fontsize={font_size}:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:"
            f"fontfile='{font_path}',"
            f"drawtext=text='{shot_info['down_center']}':x=(w-text_w)/2:y=h-{letterbox_height}-10:"
            f"fontsize={font_size}:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:"
            f"fontfile='{font_path}',"
            f"drawtext=text='{shot_info['down_right']}':x=w-text_w-10:y=h-{letterbox_height}-10:"
            f"fontsize={font_size}:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:"
            f"fontfile='{font_path}'",
            "-c:a", "copy", output_video
        ]
        subprocess.run(ffmpeg_cmd, shell=True)
        print(f"overlay_shot_data is completed!!: {output_video}")
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
    def delete_frames(output_dir): # 변환 후 이미시 시퀀스 (.jpg) 파일 삭제 # :param output_dir: 이미지 시퀀스가 저장된 디렉토리 
        image_files = glob.glob(os.path.join(output_dir, "frame.*.jpg", "frame.*.jpeg")) # frame.0001.jpg 등 찾기
        for file in image_files:
            os.remove(file)
        print(f"프레임 이미지 {len(image_files)}개 삭제 완료.")