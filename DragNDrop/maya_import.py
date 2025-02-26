import maya.cmds as cmds
from PyQt5.QtCore import QMimeData

def import_to_maya(file_path):
    """Maya에서 파일 Import"""
    if file_path.endswith(".ma") or file_path.endswith(".mb"):
        cmds.file(file_path, i=True, force=True)  # Maya Import
    elif file_path.endswith(".abc"):
        cmds.AbcImport(file_path, mode="import")  # Alembic Import
    print(f"✅ Maya에서 {file_path} Import 완료!")

def handle_maya_drop(mime_data: QMimeData):
    """Maya에서 파일 드롭을 감지하고 Import"""
    if mime_data.hasText():
        file_paths = mime_data.text().split("\n")
        for file_path in file_paths:
            import_to_maya(file_path)