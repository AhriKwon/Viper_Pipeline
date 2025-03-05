
import os
import sys
from PySide6 import QtWidgets, QtCore

# ShotGrid API 파일 가져오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_connector import ShotGridConnector
from MayaLoader import MayaLoader
from NukeLoader import NukeLoader


class FileLoader:
    """ShotGrid에서 퍼블리시된 파일을 불러오고 실행하는 유틸리티 클래스"""

    @staticmethod
    def load_published_files(user_id, file_list_widget):
        """샷그리드의 user에게 퍼블리시된 파일을 불러옴"""
        file_list_widget.clear()
        tasks = ShotGridConnector.get_user_tasks(user_id)

        for task in tasks:
            files = ShotGridConnector.get_publishes_for_task(task["id"])
            if not files:
                continue

            for file in files:
                list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
                list_item.setData(QtCore.Qt.UserRole, file)
                file_list_widget.addItem(list_item)

    @staticmethod
    def set_file_path(file_path_input, parent=None):
        """사용자가 파일 경로를 직접 설정"""
        file_dialog = QtWidgets.QFileDialog(parent)
        file_path, _ = file_dialog.getOpenFileName(None, "파일 선택", "", "Maya Files (*.ma *.mb);;Nuke Files (*.nk);;All Files (*.*)")

        if file_path:
            file_path_input.setText(file_path)

    @staticmethod
    def run_file(file_path_input):
        """설정된 파일 경로를 읽고 Maya 또는 Nuke에서 실행"""
        file_path = file_path_input.text().strip()

        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(None, "오류", "유효한 파일 경로를 입력하세요.")
            return

        file_path = os.path.abspath(file_path)

        if file_path.endswith((".ma", ".mb")):
            MayaLoader.launch_maya(file_path)
        elif file_path.endswith(".nk"):
            NukeLoader.launch_nuke(file_path)
        else:
            QtWidgets.QMessageBox.warning(None, "오류", "지원되지 않는 파일 형식입니다.")

    @staticmethod
    def open_selected_file(item, file_path_input):
        """리스트에서 선택한 파일을 실행"""
        file_info = item.data(QtCore.Qt.UserRole)
        if file_info:
            file_path_input.setText(file_info["path"])
            FileLoader.run_file(file_path_input)

    @staticmethod
    def import_file(file_path_input):
        """Maya 또는 Nuke에서 파일 Import"""
        file_path = file_path_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(None, "오류", "유효한 파일 경로를 입력하세요.")
            return

        if file_path.endswith((".ma", ".mb", ".abc", ".obj")):
            MayaLoader.import_maya(file_path)
        elif file_path.endswith((".nk", ".mov")):
            NukeLoader.import_nuke(file_path)
        else:
            QtWidgets.QMessageBox.warning(None, "오류", "지원되지 않는 파일 형식입니다.")

    @staticmethod
    def create_reference_file(file_path_input):
        """Maya에서 Reference 추가"""
        file_path = file_path_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(None, "오류", "유효한 파일 경로를 입력하세요.")
            return

        MayaLoader.create_reference_maya(file_path)
