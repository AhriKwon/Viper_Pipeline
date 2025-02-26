import hou

def import_to_houdini(file_path):
    """Houdini에서 파일 Import"""
    if file_path.endswith(".bgeo") or file_path.endswith(".abc"):
        geo_node = hou.node("/obj").createNode("geo")
        file_node = geo_node.createNode("file")
        file_node.parm("file").set(file_path)
    print(f"✅ Houdini에서 {file_path} Import 완료!")

def handle_houdini_drop(mime_data: QMimeData):
    """Houdini에서 파일 드롭을 감지하고 Import"""
    if mime_data.hasText():
        file_paths = mime_data.text().split("\n")
        for file_path in file_paths:
            import_to_houdini(file_path)
