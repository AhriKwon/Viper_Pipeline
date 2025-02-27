from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QWidget, QScrollArea, QTabWidget, QPushButton, QLineEdit
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QPixmap, QColor
import sys, os
from shotgun_api3 import Shotgun

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_connector import ShotGridConnector 

#============================================================================================
#====================로그인 창 : LoginWindow==============================================
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
    
    def load_ui(self):
        ui_file_path = "/home/rapa/teamwork/viper/loadUI/login.ui"  # 서브창 UI 경로
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        # UI 요소 찾기
        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")

        # 로그인 버튼 클릭 시 이벤트 연결
        self.pushButton_login.clicked.connect(self.attempt_login)
    
    def attempt_login(self):
        email = self.lineEdit_id.text().strip()
        if email:
            self.accept()  # 로그인 성공 시 다이얼로그 닫기
            self.main_window = LoadUI(email)  # LoadUI 실행
            self.main_window.show()

#============================================================================================
#====================loader ui class : LoadUI==============================================

class LoadUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.load_ui()
        self.login_and_load_tasks()

    #====================================qt designer 로드=======================================

    def load_ui(self):
    
        ui_file_path = "/home/rapa/teamwork/viper/loadUI/load.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()

        # UI 설정하기
        self.main_layout = self.ui.findChild(QWidget, "tableWidget_2")
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_widget)

        # tableWidget_2에 스크롤바 추가
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_layout.setLayout(QVBoxLayout())
        self.main_layout.layout().addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_widget)

        # Tab Widget 가져오기 (초기에는 숨김)
        self.tab_widget = self.ui.findChild(QTabWidget, "tabWidget_2")
        self.label_filename = self.ui.findChild(QLabel, "label_filename")
        self.tab_widget.hide()

        # 행 역할을 하는 ListWidget 4개 생성 (가로 크기 축소, 세로 스크롤 추가, 색상 변경)
        self.list_widgets = []
        row_colors = ["#012E40", "#03A696", "#024149", "#F28705"]

        for i in range(4):
            list_widget = QListWidget()
            list_widget.setFixedWidth(220)  # 리스트 위젯 가로 크기 2/3로 축소
            list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 세로 스크롤 추가
            list_widget.setStyleSheet(f"background-color: {row_colors[i]}; border-radius: 15px; margin-right: 20px;")
            list_widget.setSpacing(10)  # 리스트 간격 조정
            self.scroll_layout.addWidget(list_widget)
            self.list_widgets.append(list_widget)
    
    #=============================로그인, task 목록을 가져오는====================================

    def login_and_load_tasks(self):
        user_data = UserAuthenticator.login(self.username)

        if "error" not in user_data:
            user_id = user_data["id"]
            user_tasks = ShotGridConnector.get_user_tasks(user_id) 
            self.populate_table(user_tasks)
        else:
            print("Error")

    #=======================================================================================

    def populate_table(self, tasks):
        if not tasks:
            return

        index = 0
        for task in tasks:
            task_id = task["id"] 
            task_name = task["content"] 
            versions = ShotGridConnector.get_publishes_for_task(task_id)

            for version in versions:
                thumbnail_url = version.get("thumbnail", None)

                # 파일을 감싸는 GroupBox 생성
                file_box = QGroupBox()
                file_box.setStyleSheet("background-color: white; border-radius: 10px; padding: 5px;")
                layout = QVBoxLayout()

                label_thumbnail = QLabel()
                if thumbnail_url:
                    pixmap = QPixmap(thumbnail_url)
                    label_thumbnail.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                layout.addWidget(label_thumbnail, alignment=Qt.AlignCenter)

                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_task_name)
                
                file_box.setLayout(layout)
                file_box.mousePressEvent = lambda event, t=task_name: self.show_task_details(t)
                
                list_item = QListWidgetItem()
                list_item.setSizeHint(file_box.sizeHint())
                self.list_widgets[index % 4].addItem(list_item)
                self.list_widgets[index % 4].setItemWidget(list_item, file_box)
                
                index += 1
    
    def show_task_details(self, task_name):
        self.label_filename.setText(task_name)
        self.tab_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())

