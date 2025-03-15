try:
    from PySide2.QtWidgets import (
        QMainWindow, QApplication, QCheckBox, QGroupBox, QVBoxLayout,
        QTableWidget, QTableWidgetItem, QLabel, QFileDialog, QLineEdit, QPushButton, QWidget,
        QGridLayout, QAbstractItemView, QListWidget, QLineEdit,QHBoxLayout
    )
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import Qt, QFile, QTimer
    from PySide2.QtGui import QFont, QColor, QBrush, QIcon, QPixmap,QFontDatabase, QFont
except:
    from PySide6.QtWidgets import (
        QMainWindow, QApplication, QCheckBox, QGroupBox, QVBoxLayout,
        QTableWidget, QTableWidgetItem, QLabel, QFileDialog, QLineEdit, QPushButton, QWidget,
        QGridLayout, QAbstractItemView, QListWidget, QLineEdit,QHBoxLayout
    )
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import Qt, QFile, QTimer
    from PySide6.QtGui import QFont, QColor, QBrush, QIcon, QPixmap,QFontDatabase, QFont

import sys, os, time, subprocess

publish_path = os.path.dirname(__file__)
viper_path = os.path.join(publish_path, '..')

# 샷그리드 API
sys.path.append(os.path.abspath(os.path.join(viper_path, 'shotgridAPI')))
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()

# UI 서포터
sys.path.append(os.path.abspath(os.path.join(viper_path, 'loadUI')))
import UI_support

# 마야 publisher 연동
# sys.path.append(os.path.abspath(os.path.join(viper_path, 'Publisher')))
# from MayaPublisher import MayaPublisher
# from Generating import FilePath
# from publisher.convert_to_mov import FileConverter

ICON_PATHS = {
    "maya": "/nas/Viper/minseo/icon/maya.png",
    "nuke": "/nas/Viper/minseo/icon/nuke.png",
}

class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_ui()
        # self.connect_signals()
        self.set_checkbox()
        self.setup_thumbnail_capture()
        self.setup_publish_info()

        # publish 버튼을 누르면 퍼블리쉬되도록 연동
        self.publish_button = self.ui.findChild(QPushButton, "publish_button")
        # if self.publish_button:
        #     self.publish_button.clicked.connect(self.publish_selected_file)


    def set_checkbox(self):
        """
        마야에서 실행될 경우에만 체크박스 표시
        """
        if not self.ui.groupBox_checkbox:
            return
        
        groupBoxLayout = QGridLayout()
        self.checkboxes = []
        options = ["shader", "wireframe on shader", "textured", "wireframe on textured"]

        for i, option in enumerate(options):
            checkbox = QCheckBox(option)
            self.checkboxes.append(checkbox)
            groupBoxLayout.addWidget(checkbox, i // 2, i % 2)

        self.ui.groupBox_checkbox.setLayout(groupBoxLayout)
        self.ui.groupBox_checkbox.setVisible("MAYA_APP_DIR" in os.environ)

    def setup_publish_info(self):
        """
        퍼블리시할 파일 정보를 표시하는 위젯 추가
        """
        self.ui.label_publish_info.setText("퍼블리시 정보 없음")
        self.ui.label_publish_info.setStyleSheet("font-size: 12px; color: white;")
        
    def update_publish_info(self, file_name, file_size, tesk_name):
        """
        선택된 파일의 정보를 업데이트
        """
        info_text = f"파일: {file_name}\n크기: {file_size:.2f} MB\n테스크: {tesk_name}"
        self.ui.label_publish_info.setText(info_text)
    
    def setup_thumbnail_capture(self):
        """
        썸네일 캡처 버튼 설정
        """
        self.ui.label_thumbnail.setText("썸네일 없음")
        self.ui.label_thumbnail.setAlignment(Qt.AlignCenter)
        self.ui.label_thumbnail.setStyleSheet("border: 1px solid gray; background: #222; color: white;")
        
        # QLabel이 마우스 이벤트를 받을 수 있도록 설정
        self.ui.label_thumbnail.setAttribute(Qt.WA_Hover)
        self.ui.label_thumbnail.setMouseTracking(True)

        # 마우스 클릭 이벤트 연결
        self.ui.label_thumbnail.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """
        마우스 클릭 이벤트 필터
        """
        if obj == self.ui.label_thumbnail and event.type() == event.MouseButtonPress:
            self.capture_thumbnail()
            return True
        return super().eventFilter(obj, event)
        
    def capture_thumbnail(self):
        """
        스크린샷 촬영 및 썸네일 업데이트
        """
        save_path = "/nas/show/Viper/test.png"
        
        # gnome-screenshot 실행을 비동기적으로 실행
        process = subprocess.Popen(["gnome-screenshot", "-a", "-f", save_path], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        print(stdout.decode())  # 표준 출력
        print(stderr.decode())  # 표준 에러

        # 스크린샷이 찍힐 시간을 고려하여 딜레이 추가
        QTimer.singleShot(1000, lambda: self.update_thumbnail(save_path))

    def update_thumbnail(self, save_path):
        """
        캡처된 썸네일을 UI에 업데이트
        """
        if os.path.exists(save_path):
            pixmap = QPixmap(save_path).scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.label_thumbnail.setPixmap(pixmap)
            print(f"썸네일 저장 완료: {save_path}")
        else:
            print("썸네일 캡처 실패")

    """
    수정 필요~!
    """
    def get_thumbnail_save_path(self):
        """
        썸네일 저장 경로 생성
        """
        project, entity_type, entity_name, task_name = self.get_publish_metadata()
        base_path = f"/nas/show/{project}/{'assets' if entity_type == 'Asset' else 'seq'}/{entity_name}/{task_name}/pub/thumb"
        return os.path.join(base_path, f"{task_name}.png")

    def get_publish_metadata(self):
        """
        프로젝트, 엔티티 타입, 엔티티 이름, 태스크 이름 가져오기 (샷그리드 연동 필요)
        """
        return "Viper", "Asset", "Hero", "RIG"
    
    def get_selected_task_id(self):
        """
        현재 선택된 태스크의 ID 반환 (샷그리드 연동 필요)
        """
        return 6105


     #===========================================================================================
     #----------------------------------------3-1. 로드 ------------------------------------------

    def load_ui(self):

        ui_file_path = os.path.join( publish_path ,"newpub.ui")

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PublishUI()
    w.ui.show()
    UI_support.center_on_screen(w.ui)
    sys.exit(app.exec())