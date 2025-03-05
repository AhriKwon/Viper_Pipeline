import os
import datetime

class FilePath:
    """Maya ,Nuke 파일의 경로를 자동 생성"""

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
                "abc_cache": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/alembic/"
            },
            "nuke": {
                "work_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/work/nuke/comps/{shot_or_name}_{task}_v{version:03d}.nk",
                "pub_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/nuke/comps/{shot_or_name}_{task}_v{version:03d}.nk",
                "mov_comp": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/nuke/data/{shot_or_name}_{task}_v{version:03d}.mov",
                "mov_product": f"/nas/show/{project}/product/{timestamp}/seq/{shot_or_name}_{task}_v{version:03d}.mov"
            }
        }
        return base_paths