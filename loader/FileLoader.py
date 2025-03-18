
import os
import sys
import re
import shutil
from PySide6 import QtWidgets, QtCore

from MayaLoader import MayaLoader
from NukeLoader import NukeLoader
from HoudiniLoader import HoudiniLoader
from FileDialog import FileDialog

# ShotGrid API 파일 가져오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_manager import ShotGridManager


class FileLoader:
    """
    지정된 user_id로부터 퍼블리시된 파일들을 샷그리드에서 가져와
        QListWidget에 표시합니다.
    """
    base_dir = "/nas/show/Viper"

    @staticmethod
    def load_published_files(user_id, file_list_widget):
        """샷그리드의 user에게 퍼블리시된 파일을 불러옴"""
        file_list_widget.clear()
        tasks = ShotGridManager.get_tasks_by_user(user_id)

        for task in tasks:
            files = ShotGridManager.get_publishes_for_task(task['id'])
            if not files:
                continue

            for file in files:
                list_item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
                list_item.setData(QtCore.Qt.UserRole, file)
                file_list_widget.addItem(list_item)

    @staticmethod
    def set_file_path(file_path_input):
        """사용자가 파일 경로를 직접 설정"""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "파일 선택", "", "Maya Files (*.ma *.mb);;Nuke Files (*.nk);;All Files (*.*)")

        if file_path:
            file_path_input.setText(file_path)

    @staticmethod
    def run_file(file_path):
        """설정된 파일 경로를 읽고 Maya 또는 Nuke에서 실행"""

        file_path = os.path.abspath(file_path)

        if file_path.endswith((".ma", ".mb")):
            MayaLoader.launch_maya(file_path)
        elif file_path.endswith((".nk", ".nknc")):
            NukeLoader.launch_nuke(file_path)
        elif file_path.endswith((".hip", ".hiplc", ".hipnc")):
            HoudiniLoader.launch_houdini(file_path)
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
    def import_file(file_path):
        """Maya, Nuke, Houdini에서 파일 Import"""

        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(None, "오류", "유효한 파일 경로를 입력하세요.")
            return

        # Maya 실행 중인지 확인 후 Import
        if MayaLoader.is_maya_running():
            if file_path.endswith((".ma", ".mb", ".abc", ".obj")):
                MayaLoader.import_maya(file_path)
                return

        # Nuke 실행 중인지 확인 후 Import
        if NukeLoader.is_nuke_running():
            if file_path.endswith((".nk", ".nknc", ".mov", ".mp4", ".abc", ".obj")):
                NukeLoader.import_nuke(file_path)
                return

        # Houdini 실행 중인지 확인 후 Import
        if HoudiniLoader.is_houdini_running():
            if file_path.endswith((".hip", ".hiplc", ".hipnc", ".abc", ".obj")):
                HoudiniLoader.import_houdini(file_path)
                return

        # 실행 중인 프로그램이 없을 때 경고 메시지 표시
        QtWidgets.QMessageBox.warning(None, "오류", "파일을 불러올 프로그램이 실행되지 않았습니다.")

    @staticmethod
    def create_reference_file(file_path):
        """Maya에서 Reference 추가"""
        if not file_path or not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(None, "오류", "유효한 파일 경로를 입력하세요.")
            return

        MayaLoader.create_reference_maya(file_path)



    @staticmethod
    def version_up_selected_file(file_list_widget):
        """선택된 파일을 Version Up"""
        selected_items = file_list_widget.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(None, "오류", "파일을 선택하세요.")
            return

        old_file_path = selected_items[0].text()
        new_file_path = FileLoader.version_up(old_file_path)

        # UI 업데이트
        selected_items[0].setText(new_file_path)

    @staticmethod
    def version_up(file_path):
        """파일의 버전을 자동 증가"""
        version_pattern = re.compile(r"(.*)_v(\d{3})(\..+)$")
        match = version_pattern.match(file_path)

        if match:
            base_name, version_num, extension = match.groups()
            version_num = int(version_num)

            # 가장 높은 버전 찾기
            while True:
                version_num += 1
                new_file_path = f"{base_name}_v{version_num:03d}{extension}"
                if not os.path.exists(new_file_path):
                    return new_file_path
        else:
            base_name, extension = os.path.splitext(file_path)
            return f"{base_name}_v001{extension}"

    @staticmethod
    def create_file_path(program, part, asset_type, asset_name, seq, shot, task):
        """파일 생성 경로를 반환"""
        file_templates = {
            "MDL": f"{FileLoader.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "RIG": f"{FileLoader.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "LDV": f"{FileLoader.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "LAY": f"{FileLoader.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "ANM": f"{FileLoader.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "LGT": f"{FileLoader.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "FX": f"{FileLoader.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/houdini/scenes/{{shot}}_{{task}}_v001.hip",
            "COM": f"{FileLoader.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/nuke/scenes/{{shot}}_{{task}}_v001.nk",
        }

        if part not in file_templates:
            QtWidgets.QMessageBox.warning(None, "오류", "잘못된 파트를 선택하였습니다.")
            return None

        file_path = file_templates[part].format(
            asset_type=asset_type or "Unknown",
            asset_name=asset_name or "Unknown",
            seq=seq or "Unknown",
            shot=shot or "Unknown",
            task=task or "Unknown"
        )

        # 기존 파일이 있으면 버전 증가
        if os.path.exists(file_path):
            file_path = FileLoader.version_up(file_path)

        return file_path

    @staticmethod
    def create_nuke_file(empty_nknc_path):
        """Nuke 빈 파일 생성"""
        empty_nknc_content = """# Empty Nuke Non-Commercial Script
        version 15.1 v1
        Root {
        inputs 0
        }
        """
        with open(empty_nknc_path, "w") as f:
            f.write(empty_nknc_content)
        print(f"[INFO] Nuke 임시 파일 생성 완료: {empty_nknc_path}")

    @staticmethod
    def create_maya_file(file_path):
        """빈 Maya 파일 생성"""
        empty_maya_file = "/home/rapa/Viper/loader_test_createfile/test_v001.ma"
        shutil.copy(empty_maya_file, file_path)
        print(f"[INFO] Maya 파일 생성 완료: {file_path}")

    @staticmethod
    def create_houdini_file(file_path):
        """빈 Houdini 파일 생성"""
        empty_hip_file = "/home/rapa/Viper/loader_test_createfile/test_v001.hip"
        shutil.copy(empty_hip_file, file_path)
        print(f"[INFO] Houdini 파일 생성 완료: {file_path}")

    @staticmethod
    def create_and_run_task_file(program, part, asset_type, asset_name, seq, shot, task, file_path_input):
        """파일 생성 후 실행"""
        file_path = FileLoader.create_file_path(program, part, asset_type, asset_name, seq, shot, task)

        if not file_path:
            return

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 파일 생성
        if file_path.endswith(".nk", ".nknc"):
            FileLoader.create_nuke_file(file_path)
        elif file_path.endswith(".ma"):
            FileLoader.create_maya_file(file_path)
        elif file_path.endswith(".hip"):
            FileLoader.create_houdini_file(file_path)

        print(f"[INFO] 새 파일 생성 완료: {file_path}")

        # UI 업데이트 및 실행
        file_path_input.setText(file_path)
        FileLoader.run_file(file_path_input)


    @staticmethod
    def create_new_file_dialog(parent=None):
        """파일 생성 대화 상자를 열고 결과를 반환"""
        dialog = FileDialog(parent)
        if dialog.exec():
            selected_options = dialog.get_selected_options()
            print("[INFO] 선택된 옵션:", selected_options)
            return selected_options
        return None