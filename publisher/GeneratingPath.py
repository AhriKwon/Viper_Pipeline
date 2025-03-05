import os
import datetime

class FilePath:
    """Maya ,Nuke 파일의 경로를 자동 생성"""

    @staticmethod
    def get_timestamp():
        """현재 날짜(년-월일) 문자열 반환"""
        return datetime.datetime.now().strftime("%Y-%m%d")

    @staticmethod
    def generate_paths(project, entity_type, seq_or_type, shot_or_name, task, version=1):
        """에셋 또는 샷의 경로를 반환"""
        timestamp = FilePath.get_timestamp()
        base_paths = {
            "maya": {
                "work_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/work/maya/scenes/{shot_or_name}_{task}_v{version:03d}.ma",
                "pub_scene": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/scenes/{shot_or_name}_{task}_v{version:03d}.ma",
                "mov_plb": f"/nas/show/{project}/{entity_type}/{seq_or_type}/{shot_or_name}/{task}/pub/maya/data/{shot_or_name}_{task}_v{version:03d}.mov",
                "mov_product": f"/nas/show/{project}/product/{timestamp}/seq/{shot_or_name}_{task}_v{version:03d}.mov",
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
    
    @staticmethod
    def get_next_version(folder_path, asset_name): # e.g. v001, v002, ... 순서대로 카운팅되게 만드는 함수
        if folder_path:
            existing_files = [f for f in os.listdir(folder_path) if f.startswith(asset_name) and f.endswith(".abc")]
            versions = [int(f.split("_v")[1].split(".")[0]) for f in existing_files if "_v" in f]
            return max(versions, default=0) + 1
    

    



    

    