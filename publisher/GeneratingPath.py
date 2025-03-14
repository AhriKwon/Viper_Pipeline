import os
import datetime

class FilePath:
    """Maya ,Nuke 파일의 경로를 자동 생성"""
    @staticmethod
    def get_base_path(project, seq, shot):
        base_path = os.path.join("/projects", project, seq, shot)
        if not base_path: # bath_path가 None or 빈 문자열인 경우
            raise ValueError("유효하지 않은 경로입니다: {base_path}")
        return base_path
    @staticmethod
    def get_scene_path(project, seq, shot):
        scene_path = os.path.join(FilePath.get_base_path(project, seq, shot), "scenes")
        if not scene_path:  # scene_path가 None 이거나 빈 문자열인 경우
            raise ValueError(f"유효하지 않은 경로입니다: {scene_path}")
        return scene_path    
    @staticmethod
    def get_output_path(project, seq, shot):
        output_path = os.path.join(FilePath.get_base_path(project, seq, shot), "output")
        if not output_path:  # output_path가 None 이거나 빈 문자열인 경우
            raise ValueError(f"유효하지 않은 경로입니다: {output_path}")
        return output_path
    
    @staticmethod
    def get_timestamp() -> str:
        """현재 날짜(년-월일) 문자열 반환"""
        return datetime.datetime.now().strftime("%Y-%m%d")

    @staticmethod
    def generate_paths(project: str, entity_type: str, seq_or_type: str, shot_or_name: str, task: str, version: int=1):
        version = int(version) # 정수 변환 
        timestamp = FilePath.get_timestamp() # 에셋 또는 샷의 경로를 반환
        base_paths = {
             "maya": {
                "work_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/work/maya/scenes/{shot_or_name}_{task}_v{version:03d}.ma",
                "pub_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/scenes/{shot_or_name}_{task}_v{version:03d}.ma",
                "mov_plb": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/data/{shot_or_name}_{task}",
                "mov_product": f"/nas/show/{project}/product/{timestamp}/{seq_or_type}/{shot_or_name}_{task}",
                "abc_cache": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/alembic/",
                "shader_ma": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/scenes/{shot_or_name}_{task}_v{version:03d}.ma",
                "shader_json": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/scenes/{shot_or_name}_{task}_v{version:03d}.json"
            },
            "nuke": {
                "work_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/work/nuke/scenes/{shot_or_name}_{task}_v{version:03d}.nk",
                "pub_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/nuke/scenes/{shot_or_name}_{task}_v{version:03d}.nk",
                "mov_comp": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/nuke/data/{shot_or_name}_{task}",
                "mov_product": f"/nas/show/{project}/product/{timestamp}/seq/{shot_or_name}_{task}"
            }
        }
        
        # 경로 확인
        for category, paths in base_paths.items():
            for key, path in paths.items():
                if not path:  # 경로가 비어 있거나 None이면 경로 생성
                    path = os.path.join("/default/base/path", key)  # 기본 경로 설정
                    os.makedirs(path, exist_ok=True)  # 경로가 없으면 생성
                    base_paths[category][key] = path  # 새 경로로 업데이트

        return base_paths