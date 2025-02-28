import os
import datetime

class FilePath:
    """Maya Playblast 또는 Alembic 파일 저장 경로를 자동 생성하는 클래스"""

    @staticmethod
    def get_publish_path(project, type_or_seq, name_or_shot, task, file_path, version=1):
        """
        퍼블리싱 경로 반환
        """
        entity = FilePath.get_entity_from_path(file_path) # 파일 경로에서 entity 추출
        dcc, pub_type = FilePath.get_dcc_from_path(file_path) # DCC 및 pub 타입 추출
        base_path = f"/nas/show/{project}/{entity}/{type_or_seq}/{name_or_shot}/{task}/pub/{dcc}/{pub_type}"
        filename = f"{name_or_shot}_{task}_v{version:03d}.mov"
        return os.path.join(base_path, filename)
    
    @staticmethod
    def get_dcc_from_path(file_path):
        # 파일 확장자를 기반으로 퍼블리쉬 타입 판단 (DCC: Maya, Nuke)
    
        if not isinstance(file_path, str): # 주어진 값이 특정 타입인지 검사하는 함수
            raise ValueError("file_path must be a string.")

            if file_path.endswith(".ma"):
                return "maya" 
            elif file_path.endswith(".nk"): # endswith : 문자열이 특정 문자열로 끝나는지 확인하는 메서드 e.g. suffix 접미사, prefix 접두사...syntax 용어 넣어주면 애가 알아서 이해함. 
                return "nuke"
            
        base_path = os.path.dirname(file_path) # 현재 파일이 있는 폴더
        publish_folder = os.path.join(base_path, "pub", "dcc", "pub_type")
        return publish_folder
    
    @staticmethod
    def get_entity_from_path(file_path):
        # 파일 경로를 기반으로 entity (assets, seq, product) 판별
        path_parts = file_path.split(os.sep) # os.sep의 역할 -> 윈도우(\), 맥&리눅스(/) 에 따라 경로 구분되어있는 걸 알아서 자동 맞춤! 

        if "assets" in path_parts:
            return "assets"
        elif "seq" in path_parts:
            return "seq"


    

    