import os
import subprocess
import platform
import glob
import maya.cmds as cmds
from PIL import Image, ImageDraw, ImageFont

class FileConverter:
    """
    FFmpeg를 사용하여 동영상 파일 변환 기능 및 레터박스, 슬레이트 정보를 추가하는 클래스.
    이 클래스는 입력 파일을 다양한 형식으로 변환하고, 변환된 영상에 슬레이트와 레터박스를 추가함.
    """

    @staticmethod
    def convert_to_video(input_path, output_path, format_type="mp4"):
        """
        주어진 입력 파일을 비디오 형식으로 변환하는 함수.
        EXR 시퀀스를 비디오 파일로 변환할 때 사용함.

        input_path: 변환할 입력 파일 경로 (예: EXR 이미지 시퀀스)
        output_path: 변환 후 저장할 출력 파일 경로 (예: .mp4, .mov 파일)
        format_type: 변환할 비디오 형식 ('mp4' 또는 'mov'을 선택)
        """
        print("컨버트 실행")
        
        # 지정된 포맷에 맞는 코덱과 픽셀 포맷을 가져옴.
        codec, pix_fmt = FileConverter._get_codec(format_type)  

        # 시스템에 설치된 FFmpeg의 경로를 지정함.
        FFMPEG_PATH = "/usr/bin/ffmpeg"
        
        # FFmpeg 명령어를 구성함.
        ffmpeg_cmd = [
            FFMPEG_PATH,
            "-i", input_path,  # 입력 파일 경로
            "-c:v", codec,  # 비디오 코덱 설정
            "-pix_fmt", pix_fmt,  # 픽셀 포맷 설정
            output_path  # 출력 파일 경로
        ]
        
        try:
            # FFmpeg 명령어 실행
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print("FFmpeg 실행 성공!")
            print(result.stdout)  # 실행 로그 출력
        except subprocess.CalledProcessError as e:
            # FFmpeg 실행 오류가 발생하면 오류 메시지를 출력함.
            print("FFmpeg 실행 오류!")
            print(e.stdout)
            print(e.stderr)  # 오류 메시지 출력
        
    @staticmethod
    def convert_to_mov(output_dir, output_file):
        """
        주어진 이미지 시퀀스를 .mov (ProRes) 비디오 파일로 변환하는 함수.
        EXR 시퀀스를 .mov 형식으로 변환할 때 사용됨.

        output_dir: 이미지 시퀀스가 저장된 폴더 경로
        output_file: 변환 후 저장할 .mov 파일 경로
        """
        # 이미지 시퀀스를 찾기 위한 패턴을 정의함. (예: frame.0001.jpg, frame.0002.jpg ...)
        input_pattern = os.path.join(output_dir, "frame.%04d.jpg")
        
        # FFmpeg 명령어를 사용하여 이미지 시퀀스를 비디오 파일로 변환함.
        ffmpeg_cmd = [
            "ffmpeg",
            "-r", "24",  # 프레임 속도 설정 (초당 24프레임)
            "-i", input_pattern,  # 입력 이미지 시퀀스 경로
            "-c:v", "prores_ks",  # ProRes 코덱 사용
            "-pix_fmt", "yuv422p10le",  # 10bit ProRes 설정
            output_file  # 출력 .mov 파일 경로
        ]
        
        # FFmpeg 명령어 실행
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"mov 변환 완료: {output_file}")

        # 이미지 파일들을 삭제함.
        FileConverter.delete_frames(output_dir)  # 변환 후 이미지 시퀀스를 삭제하는 메서드를 호출함.

    @staticmethod
    def delete_frames(output_dir):
        """
        변환 후 사용된 이미지 시퀀스 파일 (.jpg)을 삭제하는 함수.

        output_dir: 이미지 파일들이 저장된 폴더 경로
        """
        # 주어진 디렉터리에서 .jpg 또는 .jpeg 확장자를 가진 모든 파일을 찾음.
        image_files = glob.glob(os.path.join(output_dir, "frame.*.jpg")) + glob.glob(os.path.join(output_dir, "frame.*.jpeg"))
        
        # 각 이미지를 삭제함.
        for file in image_files:
            os.remove(file)  # 각 이미지 파일을 삭제함.
        print(f"프레임 이미지 {len(image_files)}개 삭제 완료.")

    @staticmethod
    def _get_codec(format_type):
        """
        주어진 형식에 맞는 비디오 코덱과 픽셀 포맷을 반환하는 함수.
        'mp4'일 경우 libx264 코덱, 'mov'일 경우 prores_ks 코덱을 사용함.

        format_type: 변환할 형식 ('mp4' 또는 'mov')
        """
        if format_type == "mp4":
            return "libx264", "yuv420p"  # mp4 형식에 맞는 코덱과 픽셀 포맷
        elif format_type == "mov":
            return "prores_ks", "yuv422p10le"  # mov 형식에 맞는 코덱과 픽셀 포맷
        else:
            # 지원하지 않는 형식일 경우 예외를 발생시킴.
            raise ValueError("지원하지 않는 형식임. 'mp4' 또는 'mov'만 가능함.")

    @staticmethod
    def padding_command():
        """
        비디오의 상단과 하단에 레터박스를 추가하는 FFmpeg 명령어를 생성하는 함수.
        레터박스는 검은색 상자를 화면의 위와 아래에 추가하여, 영상의 비율을 유지하는 데 사용됨.
        """
        return 'drawbox=x=0:y=0:w=iw:h=ih*0.1:color=black@1.0:t=fill,' \
               'drawbox=x=0:y=ih*0.9:w=iw:h=ih*0.1:color=black@1.0:t=fill'
    
    @staticmethod
    def convert_with_overlay_and_letterbox(input_file, output_file, shot_name, project_name, task_name, version, start_num=1, last_num=99):
        """
        FFmpeg를 사용하여 동영상을 변환하고, 레터박스 및 슬레이트 오버레이를 추가하는 함수.

        input_file: 입력 비디오 파일 경로
        output_file: 출력 비디오 파일 경로
        text1, text2, text3, text4: 슬레이트에 표시될 텍스트
        start_num: 시작 프레임 번호
        last_num: 마지막 프레임 번호
        """
        # 기본 FFmpeg 명령어 구성
        # ffmpeg_cmd = [
        #     "ffmpeg",
        #     "-i", input_file,  # 입력 파일 경로
        #     "-c:v", "libx264",  # 비디오 코덱 설정
        #     "-pix_fmt", "yuv420p",  # 픽셀 포맷 설정
        #     "-filter_complex",  # 여러 필터를 결합하기 위해 filter_complex 사용
        #     f"{FileConverter.padding_command()},{FileConverter.slate_command(text1, text2, text3, text4, start_num, last_num)}",  # 레터박스 및 슬레이트 필터 결합
        #     output_file  # 출력 파일 경로
        # ]

        # test 문자값 -> shot_name 받아오기 OPN_0010
        # test1 문자값 -> project_name 받아오기 5th_Academy
        # test2 -> 알아서 날짜 나오고 있음
        # 좌측 하단 -> frame numbering 여기 들어가 있는데 tc 부분으로 취합할 것
        # test4 -> version v003
        # 우측 하단 -> tc
        
        shot_name = "OPN_0010"
        project_name = "5th_Academy"
        version = "v003"
        task_name = "COMP"

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_file,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-filter_complex",
            "drawbox=x=0:y=0:w=iw:h=ih*0.1:color=black@1.0:t=fill,"
            "drawbox=x=0:y=ih*0.9:w=iw:h=ih*0.1:color=black@1.0:t=fill,"
            f"drawtext=text='{shot_name}':fontcolor=white:fontsize=20:x=20:y=(h*0.1-text_h)/2,"
            f"drawtext=text='{project_name}':fontcolor=white:fontsize=20:x=(w-text_w)/2:y=(h*0.1-text_h)/2,"
            f"drawtext=text='%{{localtime\\:%Y-%m-%d}}':fontcolor=white:fontsize=20:x=w-text_w-20:y=(h*0.1-text_h)/2,"
            f"drawtext=text='{task_name}':fontcolor=white:fontsize=20:x=20:y=h*0.9+((h*0.1-text_h)/2),"
            f"drawtext=text='{version}':fontcolor=white:fontsize=20:x=(w-text_w)/2:y=h*0.9+((h*0.1-text_h)/2),"
            f"drawtext=text='TC %{{pts\\:hms}}':fontcolor=white:fontsize=15:x=w-text_w-20:y=h*0.94-text_h,"
            f"drawtext=text=\'%{{eif\\:n+{start_num}\\:d}} / {last_num}\':fontcolor=white:fontsize=15:x=w-text_w-20:y=h*0.96-text_h",
            "-y",
            output_file
        ]
        subprocess.Popen(ffmpeg_cmd)

        try:
            # FFmpeg 명령어 실행
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print("FFmpeg 실행 성공!")
            print(result.stdout)  # 실행 로그 출력
        except subprocess.CalledProcessError as e:
            # FFmpeg 실행 오류가 발생하면 오류 메시지를 출력함.
            print("FFmpeg 실행 오류!")
            print(e.stdout)
            print(e.stderr)  # 오류 메시지 출력

    # @staticmethod
    # def generate_new_filename(original_file): # 같은 확장자 명이 있다면 덮어쓰지 않고, 새로 파일 넘버 생성해주는 함수
    #     base, ext = os.path.splitext(original_file)
    #     timestamp = datetime.now().strftime("_%Y%m%d%H%M%S")
    #     return f"{base}{timestamp}{ext}"

    #     # 사용 예
    #     new_file = FileUtils.generate_new_filename('/nas/show/Viper/assets/Character/Hero/MDL/pub/maya/data/Hero_MDL_shaded.mov')
    #     print(new_file)  # 새로운 파일 이름 출력