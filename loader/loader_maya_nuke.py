import os
import time
import subprocess
import platform
from PySide6 import QtWidgets, QtGui, QtCore


class FileLoader:
    """Maya, Nuke에서 생성된 파일을 불러오고 정보를 표시하는 클래스"""

    def __init__(self, project_directory):
        """
        프로젝트 폴더 경로 설정
        :param project_directory: 파일이 저장된 프로젝트 디렉토리
        """
        self.project_directory = project_directory

    def get_file_info(self, file_path):
        """
        파일의 정보를 가져오는 함수
        :param file_path: 파일 경로
        :return: 파일 정보 (딕셔너리)
        """
        try:
            file_stats = os.stat(file_path)
            return {
                "file_name": os.path.basename(file_path),
                "file_size_kb": round(file_stats.st_size / 1024, 2),  # KB 단위 변환
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_ctime)),
                "modified_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime)),
                "file_path": file_path
            }
        except Exception as e:
            print(f"⚠️ 파일 정보를 가져오는 중 오류 발생: {e}")
            return None

    def get_maya_nuke_files(self, sort_by="created_at"):
        """
        Maya (`.ma`, `.mb`), Nuke (`.nk`) 파일을 불러와 정렬
        :param sort_by: 정렬 기준 (created_at, modified_at, file_size_kb)
        :return: 파일 목록 (리스트)
        """
        if not os.path.exists(self.project_directory):
            print("프로젝트 디렉토리가 존재하지 않습니다!")
            return []

        maya_nuke_files = []

        for root, _, files in os.walk(self.project_directory):
            for file_name in files:
                if file_name.endswith((".ma", ".mb", ".nk")):  # Maya, Nuke 파일 필터링
                    file_path = os.path.join(root, file_name)
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        maya_nuke_files.append(file_info)

        sorted_files = sorted(maya_nuke_files, key=lambda x: x.get(sort_by, ""), reverse=False)

        return sorted_files

    def open_file(self, file_path):
        """
        파일을 실행하는 함수 (Maya/Nuke 연동)
        :param file_path: 실행할 파일 경로
        """
        if not os.path.exists(file_path):
            print(f"파일이 존재하지 않습니다: {file_path}")
            return

        if file_path.endswith(".ma") or file_path.endswith(".mb"):
            self.open_maya(file_path)
        elif file_path.endswith(".nk"):
            self.open_nuke(file_path)
        else:
            print(f"⚠️ 지원되지 않는 파일 형식: {file_path}")

    def open_maya(self, file_path):
        """Maya에서 파일 열기"""
        try:
            subprocess.Popen(["maya", "-file", file_path], shell=True)
            print(f"Maya에서 파일을 실행합니다: {file_path}")
        except Exception as e:
            print(f"Maya 실행 오류: {e}")

    def open_nuke(self, file_path):
        """Nuke에서 파일 열기"""
        try:
            subprocess.Popen(["nuke", file_path], shell=True)
            print(f"Nuke에서 파일을 실행합니다: {file_path}")
        except Exception as e:
            print(f"Nuke 실행 오류: {e}")


class FileLoaderGUI(QtWidgets.QMainWindow):
    """Maya, Nuke 파일을 불러오는 GUI"""

    def __init__(self, project_directory):
        super().__init__()
        self.setWindowTitle("Maya & Nuke File Loader")
        self.setGeometry(100, 100, 900, 600)
        self.project_directory = project_directory
        self.file_loader = FileLoader(project_directory)
        self.initUI()

    def initUI(self):
        """GUI 레이아웃 설정"""
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        # 파일 리스트
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_selected_file)
        layout.addWidget(self.file_list)

        # 파일 정보 표시
        self.file_info_label = QtWidgets.QLabel("파일 정보를 선택하세요.")
        layout.addWidget(self.file_info_label)

        # 버튼 영역
        button_layout = QtWidgets.QHBoxLayout()
        self.refresh_button = QtWidgets.QPushButton("🔄 새로고침")
        self.refresh_button.clicked.connect(self.load_files)
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)

        # 파일 로드
        self.load_files()

    def load_files(self):
        """Maya, Nuke 파일 목록을 가져와 리스트에 표시"""
        self.file_list.clear()
        files = self.file_loader.get_maya_nuke_files()

        if not files:
            self.file_info_label.setText("불러올 파일이 없습니다.")
            return

        for file in files:
            item = QtWidgets.QListWidgetItem(f"{file['file_name']} ({file['created_at']})")
            item.setData(QtCore.Qt.UserRole, file)
            self.file_list.addItem(item)

    def open_selected_file(self, item):
        """리스트에서 선택한 파일을 열기"""
        file_info = item.data(QtCore.Qt.UserRole)
        if file_info:
            self.file_info_label.setText(
                f" {file_info['file_name']}\n"
                f" 위치: {file_info['file_path']}\n"
                f" 크기: {file_info['file_size_kb']} KB\n"
                f" 생성: {file_info['created_at']}\n"
                f" 수정: {file_info['modified_at']}"
            )
            self.file_loader.open_file(file_info["file_path"])


# 실행
def run_gui():
    """파일 로더 GUI 실행"""
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = FileLoaderGUI("/home/rapa/test_maya")  # 프로젝트 경로 변경 필요
    window.show()
    sys.exit(app.exec())


# GUI 실행
if __name__ == "__main__":
    run_gui()
