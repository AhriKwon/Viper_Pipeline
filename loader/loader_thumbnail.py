import os
import json
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui

# 프로젝트 폴더 경로 (실제 경로로 변경 필요)
PROJECT_FOLDER = "/path/to/your/project/files"
USER_DATA_FILE = os.path.join(PROJECT_FOLDER, "user_info.json")

def load_metadata():
    """JSON 파일에서 메타데이터를 로드"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

class MayaFileLoader(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maya File Loader")
        self.setGeometry(100, 100, 900, 600)

        self.metadata = load_metadata()
        self.initUI()
        self.update_file_list()

    def initUI(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        # 탭 위젯
        self.tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_widget)

        self.tasks_tab = QtWidgets.QWidget()
        self.assets_tab = QtWidgets.QWidget()
        self.shots_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tasks_tab, "Tasks")
        self.tab_widget.addTab(self.assets_tab, "Assets")
        self.tab_widget.addTab(self.shots_tab, "Shots")

        # 파일 목록
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemClicked.connect(self.display_file_info)
        layout.addWidget(self.file_list)

        # 파일 정보 및 썸네일 표시
        info_layout = QtWidgets.QHBoxLayout()
        self.thumbnail = QtWidgets.QLabel()
        self.thumbnail.setFixedSize(150, 150)
        self.file_info = QtWidgets.QLabel("File Info: ")
        info_layout.addWidget(self.thumbnail)
        info_layout.addWidget(self.file_info)
        layout.addLayout(info_layout)

        # My Team Status 테이블
        self.team_status = QtWidgets.QTableWidget()
        self.team_status.setColumnCount(5)
        self.team_status.setHorizontalHeaderLabels(["Artist", "Shot", "Task", "Version", "Status"])
        layout.addWidget(self.team_status)

        # 버튼 레이아웃
        button_layout = QtWidgets.QHBoxLayout()
        self.new_button = QtWidgets.QPushButton("NEW")
        self.open_button = QtWidgets.QPushButton("OPEN")
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.open_button)
        layout.addLayout(button_layout)

        # 버튼 기능 연결
        self.new_button.clicked.connect(self.create_new_file)
        self.open_button.clicked.connect(self.open_selected_file)

    def update_file_list(self):
        """파일 목록을 업데이트하는 함수"""
        self.file_list.clear()
        if os.path.exists(PROJECT_FOLDER):
            for file_name in os.listdir(PROJECT_FOLDER):
                if file_name.endswith((".nknc", ".mb", ".ma")):
                    self.file_list.addItem(file_name)

    def display_file_info(self, item):
        """선택한 파일의 정보를 표시"""
        file_name = item.text()
        data = self.metadata.get(file_name, {})
        info_text = f"Name: {file_name}\nFile Type: {data.get('type', 'Unknown')}\nResolution: {data.get('resolution', 'N/A')}\nSaved Time: {data.get('saved_time', 'N/A')}\nFile Size: {data.get('size', 'N/A')} KB"
        self.file_info.setText(info_text)

        # 썸네일 표시
        thumbnail_path = os.path.join(PROJECT_FOLDER, "thumbnails", f"{file_name}.png")
        if os.path.exists(thumbnail_path):
            pixmap = QtGui.QPixmap(thumbnail_path)
            self.thumbnail.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))
        else:
            self.thumbnail.clear()

        # 팀 상태 업데이트
        self.update_team_status(file_name)

    def update_team_status(self, file_name):
        """팀 상태 테이블 업데이트"""
        self.team_status.setRowCount(0)
        team_data = self.metadata.get(file_name, {}).get("team_status", [])
        for row_idx, entry in enumerate(team_data):
            self.team_status.insertRow(row_idx)
            for col_idx, key in enumerate(["artist", "shot", "task", "version", "status"]):
                self.team_status.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(entry.get(key, "N/A")))

    def open_selected_file(self):
        """선택한 파일을 Maya에서 열기"""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_path = os.path.join(PROJECT_FOLDER, selected_item.text())
            if os.path.exists(file_path):
                cmds.file(file_path, open=True, force=True)

    def create_new_file(self):
        """새 파일을 생성하는 기능 (템플릿 파일 생성)"""
        template_file = os.path.join(PROJECT_FOLDER, "template.mb")
        new_file = os.path.join(PROJECT_FOLDER, "new_file.mb")
        if os.path.exists(template_file):
            cmds.sysFile(template_file, copy=new_file)
            self.update_file_list()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "템플릿 파일이 없습니다.")

# 실행
def show_loader():
    global file_loader
    file_loader = MayaFileLoader()
    file_loader.show()

show_loader()