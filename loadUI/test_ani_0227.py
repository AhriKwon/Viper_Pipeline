from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QGroupBox, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QWidget, QScrollArea, 
    QTabWidget, QPushButton, QLineEdit, QGraphicsOpacityEffect
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QPropertyAnimation, QRect, QTimer
from PySide6.QtGui import QPixmap, QColor
import sys, os
from shotgun_api3 import Shotgun

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_connector import ShotGridConnector

from drag_drop_handler import DragDropHandler


 #============================================================================================
 #================================로그인 창 : LoginWindow==============================================


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
    
    def load_ui(self):
        ui_file_path = "/home/rapa/teamwork/viper/loadUI/login.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        # 로그인 창 크기 조정 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(600, 700)

        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")

        self.pushButton_login.clicked.connect(self.attempt_login)

    # 만약 email이 맞다면 mainwindow(loadui)가 실행되도록
    def attempt_login(self):
        email = self.lineEdit_id.text().strip()
        if email:
            self.accept()
            self.main_window = LoadUI(email)
            self.main_window.show()


 #============================================================================================
 #====================loader ui class : LoadUI==============================================


class LoadUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.animations = []
        self.effects = []
        self.load_ui()
        self.animate_list_widgets() 
        self.login_and_load_tasks()


  #====================================loadui 로드=======================================
  #================================(loginui가 성공할 시에)=================================


    def load_ui(self):
        ui_file_path = "/home/rapa/teamwork/viper/loadUI/load.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()

        # load.ui 사이즈 조절 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(900, 500)

        # tableWidget_2의 스크롤 설정 
        self.main_layout = self.ui.findChild(QWidget, "tableWidget_2")
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_widget)
        
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_layout.setLayout(QVBoxLayout())
        self.main_layout.layout().addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_widget)

        self.tab_widget = self.ui.findChild(QTabWidget, "tabWidget_2")
        self.label_filename = self.ui.findChild(QLabel, "label_filename")
        self.tab_widget.hide()

        # listwidget의 색깔 설정 
        self.list_widgets = []
        row_colors = ["#012E40", "#03A696", "#024149", "#F28705"]

        for i in range(4):
            list_widget = QListWidget()
            list_widget.setFixedWidth(220)
            list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            list_widget.setStyleSheet(f"background-color: {row_colors[i]}; border-radius: 15px; margin-right: 20px;")
            list_widget.setSpacing(10)
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

    #=============================ListWidget 애니메이션 추가====================================

    def animate_list_widgets(self):
        delay = 400  # 0.4초 간격으로 순차적 애니메이션 실행 

        for index, list_widget in enumerate(self.list_widgets):
            QTimer.singleShot(index * delay, lambda lw=list_widget: self.animate_widget(lw, duration=600))

    #=============================애니메이션 적용=============================================

    def animate_widget(self, widget, duration=600):
        start_y = widget.y() + 40
        end_y = widget.y()  

        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)  
        anim.setStartValue(QRect(widget.x(), start_y, widget.width(), widget.height()))
        anim.setEndValue(QRect(widget.x(), end_y, widget.width(), widget.height()))
        self.animations.append(anim)  
        anim.start()

        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        self.effects.append(effect)  
        self.animations.append(fade_anim)  
        fade_anim.start()

    #=============================GroupBox를 ListWidget에 추가====================================

    def populate_table(self, tasks):
        if not tasks:
            return

        index = 0
        delay = 400  # GroupBox도 0.4초 간격으로 등장하도록 설정 

        for task in tasks:
            task_id = task["id"] 
            task_name = task["content"] 
            versions = ShotGridConnector.get_publishes_for_task(task_id)

            for version in versions:
                thumbnail_url = version.get("thumbnail", None)

                file_box = QGroupBox()
                file_box.setStyleSheet("background-color: white; border-radius: 10px; padding: 5px;")
                layout = QVBoxLayout()

                label_thumbnail = QLabel()
                if thumbnail_url:
                    pixmap = QPixmap(thumbnail_url)
                    label_thumbnail.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
                layout.addWidget(label_thumbnail, alignment=Qt.AlignCenter)

                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_task_name)
                
                file_box.setLayout(layout)
                file_box.mousePressEvent = lambda event, t=task_name: self.show_task_details(t)

                list_item = QListWidgetItem()
                list_item.setSizeHint(file_box.sizeHint())

                target_list = self.list_widgets[index % 4]
                target_list.addItem(list_item)
                target_list.setItemWidget(list_item, file_box)

                QTimer.singleShot(index * delay, lambda fb=file_box: self.animate_widget(fb, duration=1800))

                index += 1

    #=============================파일 정보 표시====================================

    def show_task_details(self, task_name):
        self.label_filename.setText(task_name)
        self.tab_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())
