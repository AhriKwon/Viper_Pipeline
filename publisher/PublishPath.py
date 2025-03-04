import os
import datetime

class FilePath:
    """Maya 씬, MOV, Alembic 캐시, Nuke 파일을 자동 저장하는 클래스"""

    @staticmethod
    def get_timestamp():
        """현재 날짜(년-월일) 문자열 반환"""
        return datetime.datetime.now().strftime("%Y-%m%d")

    @staticmethod
    def get_publish_paths(project, entity_type, name, task, version=1):
        """에셋 또는 샷의 퍼블리시 경로를 반환"""
        timestamp = FilePath.get_timestamp()
        base_paths = {
            "maya": {
                "work_scene": f"/nas/show/{project}/{entity_type}/{name}/{task}/work/maya/scenes/{name}_{task}_v{version:03d}.ma",
                "pub_scene": f"/nas/show/{project}/{entity_type}/{name}/{task}/pub/maya/scenes/{name}_{task}_v{version:03d}.ma",
                "mov_seq": f"/nas/show/{project}/seq/{name}/{task}/pub/maya/data/{name}_{task}_v{version:03d}.mov",
                "mov_product": f"/nas/show/{project}/product/{timestamp}/seq/{name}_{task}_v{version:03d}.mov",
                "abc_asset": f"/nas/show/{project}/assets/{entity_type}/{name}/{task}/pub/maya/alembic/{name}_{task}_v{version:03d}.abc",
                "abc_shot": f"/nas/show/{project}/seq/{name}/{task}/pub/maya/alembic/{name}_{task}_v{version:03d}.abc",
            },
            "nuke": {
                "work_comp": f"/nas/show/{project}/{entity_type}/{name}/{task}/work/nuke/comps/{name}_{task}_v{version:03d}.nk",
                "pub_comp": f"/nas/show/{project}/{entity_type}/{name}/{task}/pub/nuke/comps/{name}_{task}_v{version:03d}.nk",
            }
        }
        return base_paths

    @staticmethod
    def save_file(path):
        """파일을 실제로 저장 (더미 파일 생성)"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("Dummy file for testing")
        print(f"Saved: {path}")

    @classmethod
    def save_all(cls, project, entity_type, name, task, version=1):
        """필요한 모든 파일 저장"""
        paths = cls.get_publish_paths(project, entity_type, name, task, version)
        for dcc_paths in paths.values():
            for path in dcc_paths.values():
                cls.save_file(path)

# 테스트 실행
FilePath.save_all("my_project", "assets", "hero", "anim", version=1)



    

    