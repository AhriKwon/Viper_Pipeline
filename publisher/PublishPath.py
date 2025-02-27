import os
import datetime

class FilePath:
    """Maya Playblast 또는 Alembic 파일 저장 경로를 자동 생성하는 클래스"""

    @staticmethod
    def get_publish_path(project, asset_type, asset_name, task, version=1):
        """
        퍼블리싱 경로 반환
        """
        base_path = f"/nas/show/{project}/assets/{asset_type}/{asset_name}/{task}/pub/maya/data"
        filename = f"{asset_name}_{task}_v{version:03d}.mov"
        return os.path.join(base_path, filename)

    

    