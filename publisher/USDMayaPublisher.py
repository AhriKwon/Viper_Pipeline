import os
import re
import datetime
import maya.cmds as cmds
import maya.mel as mel

class USDPublisher:
    # Maya에서 Arnold-USD 및 일반 USD를 publishing하는 클라스

    @staticmethod
    def get_timestamp():
        # 현재 날짜(YYYY-MMDD) 반환
        return datetime.datetime.now().strftime("%Y-%m%d")
    @staticmethod
    def get_publish_paths(project, entity_type, name, task, version=None):
        # Arnold-USD와 USD Export의 퍼블리시 경로 반환
        timestamp = USDPublisher.get_timestamp()
        version = version or "v001" #v001, usd 파일 레이어 자동 증가 +1
        base_paths = {
            "arnold_usd":{
                "flow": f"/nas/show/{project}/{entity_type}/{name}/{task}/pub/maya/arnold_usd/{name}_{task}_{version}.usd",
                "product": f"/nas/show/{project}/product/{timestamp}/{name}_{task}_{version}.usd"
            }
        }
        return base_paths
    @staticmethod
    def export_usd(file_path, export_type="usd"):
        # Maya 씬을 USD로 내보내기 (Arnold-USD or 일반 USD)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if export_type == "arnold_usd":
            cmds.loadPlugin("mtoa", quiet=True) # Arnold plugin mode
            cmds.file(file_path, force=True, options=";", type="Arnold USD Export", exportSelected=True)
        else:
            cmds.file(file_path, force=True, options=";", type="USD Export", exportSelected=True)
        print(f"Exported: {file_path}")
    
    @classmethod
    def publish_all(cls, project, entity_type, name, task):
        # Arnold-USD & 일반 USD 파일을 퍼블리쉬하고, Flow 경로와 Product 경로에 저장
        paths = cls.get_publish_paths(project, entity_type, name, task)
        
        for usd_type, locations in paths.items():
            version = cls.get_next_version(locations["flow"]) # Auto version up
            flow_path = locations["flow"].replace("_v001", f"_{version}")
            product_path = locations["product"].replace("_v001", f"_{version}")
            cls.export_usd(flow_path, export_type=usd_type)
            cls.export_usd(product_path, export_type=usd_type)
            print(f"{usd_type.upper()} Publishing is completed!: {flow_path}, {product_path}")


















