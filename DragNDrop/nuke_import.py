import nuke

def import_to_nuke(file_path):
    """Nuke에서 파일 Import"""
    if file_path.endswith(".exr") or file_path.endswith(".mov"):
        nuke.createNode("Read", f"file {file_path}")  # Nuke Read Node 생성
    print(f"✅ Nuke에서 {file_path} Import 완료!")

def handle_nuke_drop(mime_data: QMimeData):
    """Nuke에서 파일 드롭을 감지하고 Import"""
    if mime_data.hasText():
        file_paths = mime_data.text().split("\n")
        for file_path in file_paths:
            import_to_nuke(file_path)
