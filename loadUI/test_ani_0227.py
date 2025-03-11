from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QGroupBox, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QWidget, QScrollArea, QMessageBox,
    QTabWidget, QPushButton, QLineEdit, QGraphicsOpacityEffect, QGridLayout,QTableWidget, QTableWidgetItem
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QPropertyAnimation, QRect, QTimer, QMimeData, QUrl
from PySide6.QtGui import QPixmap, QColor, QDrag, QIcon
import sys, os, glob
from shotgun_api3 import Shotgun
from functools import partial 
from PySide6.QtCore import Qt


# 샷그리드 API
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loader')))
from MayaLoader import MayaLoader
from NukeLoader import NukeLoader

import popup




 #============================================================================================
 #================================로그인 창 : LoginWindow==============================================


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()

    
    def load_ui(self):
        current_directory = os.path.dirname(__file__)
        ui_file_path = f"{current_directory}/login.ui"

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        # 로그인 창 크기 조정 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(734, 491)
        # # 창 프레임 제거
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        # 창 배경을 검정색으로 설정하여 투명도 문제 해결
        self.setStyleSheet("background-color: black; border: none;")

        
                        

        self.label_background = self.ui.findChild(QLabel, "label_background")
        self.label_id = self.ui.findChild(QLabel, "label_id")
        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")
        self.pushButton_help = self.ui.findChild(QPushButton, "pushButton_help")

        image_path = f"{current_directory}/forui/login.png"  # 배경 이미지 경로 확인
        self.label_background.setPixmap(QPixmap(image_path))
        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        image_path = f"{current_directory}/forui/Group 3995.png"  # 배경 이미지 경로 확인
        self.label_id.setPixmap(QPixmap(image_path))
        self.label_id.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정


        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

       
        self.pushButton_login.clicked.connect(self.attempt_login)

    def resizeEvent(self, event):
   
        self.label_background.setGeometry(0, 0, self.width(), self.height())
        current_directory = os.path.dirname(__file__)

        # 원본 이미지를 직접 가져와서 크기 조정 (고화질 유지)
        pixmap = QPixmap(f"{current_directory}/forui/Group 3994.png")

        # QLabel 크기에 맞게 고품질 리사이징 적용
        self.label_background.setPixmap(
            pixmap.scaled(
                self.label_background.size(),  
                Qt.KeepAspectRatioByExpanding,  # 원본 비율 유지하면서 확장
                Qt.SmoothTransformation  # 고품질 스케일링 적용
            )
        )

        super().resizeEvent(event)
        


    # 만약 email이 맞다면 mainwindow(loadui)가 실행되도록
    def attempt_login(self):
        email = self.lineEdit_id.text().strip()

        if not email:
            popup.show_message("error", "오류", "이메일을 입력해주세요")
            return
        
        user_data = UserAuthenticator.login(email)

        if user_data:
            self.accept()
            self.main_window = LoadUI(email)
            self.main_window.show()
        else:
            popup.show_message("error", "오류", "등록되지 않은 사용자입니다")
            return

class ImageListWidget(QListWidget):
        def __init__(self, parent=None, image_paths=[]):
            super().__init__(parent)

            # 리스트 배경을 투명하게 설정
            self.setStyleSheet("""
                QListWidget {
                    background: transparent;
                    border: none;
                }
                QListWidget::item {
                    background: transparent;
                    border: none;
                }
            """)

            # 리스트 아이템을 PNG 이미지로 추가
            for image_path in image_paths:
                self.add_image_item(image_path)

        def add_image_item(self, image_path):
            """QListWidgetItem을 PNG 이미지로 대체"""
            item = QListWidgetItem(self)  # 리스트 아이템 생성
            item_widget = QWidget()  # 아이템을 담을 위젯 생성
            layout = QVBoxLayout()

            # QLabel을 사용하여 이미지 표시
            label = QLabel()
            pixmap = QPixmap(image_path)
            label.setPixmap(pixmap)
            label.setScaledContents(True)  # 크기 조정 가능하도록 설정

            layout.addWidget(label)
            item_widget.setLayout(layout)

            item.setSizeHint(pixmap.size())  # 아이템 크기 설정
            self.addItem(item)
            self.setItemWidget(item, item_widget)  # 아이템을 이미지 위젯으로 대체


 #============================================================================================
 #====================loader ui class : LoadUI==============================================


class LoadUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.animations = []
        self.effects = []
        self.load_ui()
        
        # self.animate_list_widgets() 
        self.login_and_load_tasks()

        self.setGeometry(100, 100, 1800, 1000)
        self.resize(1000, 650)

        self.pushButton_open = self.ui.findChild(QPushButton, "pushButton_open")
        self.ui.pushButton_open.clicked.connect(self.loadmayanuke) # open 버튼을 누르면 마야와 누크 파일이 열리도록 

        # my task ///////////////////뒷배경 이미지 설정 /////////////////////////////////
        self.label = self.ui.findChild(QLabel, "label")
        self.label_bar = self.ui.findChild(QLabel,"label_bar")
        self.listWidget_wtg = self.ui.findChild(QListWidget, "listWidget_wtg")
        self.listWidget_ip = self.ui.findChild(QListWidget, "listWidget_ip")
        self.listWidget_fin = self.ui.findChild(QListWidget, "listWidget_fin")

        current_directory = os.path.dirname(__file__)
        image_path = f"{current_directory}/forui/verbig.png"
      
        self.label.setPixmap(QPixmap(image_path))
        self.label.setScaledContents(True)  

        image_path_2 = f"{current_directory}/forui/barui.png" 
        self.label_bar.setPixmap(QPixmap(image_path_2))
        self.label_bar.setScaledContents(True) 

        image_path_3 = f"{current_directory}/forui/list1.png"
        self.listWidget_wtg = ImageListWidget(self, [
            image_path_3
        ])
        # ✅ listWidget_wtg가 QTabWidget 내부의 특정 탭에서만 존재하도록 설정
        tab_1 = self.ui.tabWidget.widget(0)  # 첫 번째 탭 가져오기
        self.listWidget_wtg.setParent(tab_1)  # 탭 내부로 이동

        # ✅ 위치 조정: 탭 내부에서 보이게 설정
        self.listWidget_wtg.setGeometry(20, 50, 270, 500)

        # ✅ 탭이 변경될 때 listWidget_wtg를 자동으로 보이거나 숨기도록 설정
        self.ui.tabWidget.currentChanged.connect(self.update_listwidget_visibility)

    def update_listwidget_visibility(self, index):
            """탭이 변경될 때 listWidget_wtg를 현재 탭에서만 보이도록 설정"""
            if index == 0:  # 첫 번째 탭일 때만 보이게
                self.listWidget_wtg.show()
            else:
                self.listWidget_wtg.hide()  # 다른 탭에서는 숨김
            






  #====================================loadui 로드=======================================
  #================================(loginui가 성공할 시에)=================================


    def load_ui(self):
        current_directory = os.path.dirname(__file__)
        ui_file_path = f"{current_directory}/load.ui"

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()
        

        # # 배경 색상 변경 (기본 검정 계열, 명도 차이를 둠)
        # self.setStyleSheet("background-color: #101010;")  

        # load.ui 사이즈 조절 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(900, 500)
        self.label_filename_2 = self.ui.findChild(QLabel, "label_filename_2")
        self.label_filetype_2 = self.ui.findChild(QLabel, "label_filetype_2")

        # 클릭 이벤트 전에는 숨기기 
        self.ui.tabWidget_info.hide()
    

        # listwidget의 색깔 설정 
        self.list_widgets = [self.ui.listWidget_wtg, self.ui.listWidget_ip, self.ui.listWidget_fin]
        list_labels = [self.ui.label_wtg, self.ui.label_ip, self.ui.label_fin]
        # row_colors = ["#012E40", "#03A696", "#024149", "#F28705"]

       

        """
        리스트 위젯에 디자인이나 애니메이션 넣는게 필요하면 여기에 추가할 수 있을 것 같아요~!
        리스트라 그런건지는 모르겠는데 누르면 구멍 뚤리는? 배경 사라지는? 현상이 생김
        디자인작업 할 때 고려하면서 문제 해결해줄 수 있으면 좋을 것 같아욥
        """
    

        # 리스트 위젯 드래그 및 드랍 활성화 설정
        self.ui.listWidget_wtg.setDragEnabled(True)    # 0번 리스트에서 드래그 가능
        self.ui.listWidget_ip.setAcceptDrops(True)     # 1번 리스트에서만 드랍 가능

        # 이벤트 필터 추가
        self.ui.listWidget_wtg.startDrag = self.startDrag
        self.ui.listWidget_ip.dragEnterEvent = self.dragEnterEvent
        self.ui.listWidget_ip.dragMoveEvent = self.dragMoveEvent
        self.ui.listWidget_ip.dropEvent = self.dropEvent


    #==========================wtg->ip 리스트 드래그 앤 드랍 이벤트=================================

    # wtg 리스트에서 드래그 시작
    def startDrag(self, supportedActions):
        item = self.ui.listWidget_ip.currentItem()
        if not item:
            return

        mime_data = QMimeData()
        mime_data.setText(item.text())

        drag = QDrag(self.listWidget_ip)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    # ip 리스트에서 드랍 이벤트 처리
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        ip 리스트에 드랍할 때 실행
        """
        if event.mimeData().hasText():
            text = event.mimeData().text()
            new_item = QListWidgetItem(text)
            self.ui.listWidget_fin.addItem(new_item)  # 1번 리스트에 추가
            event.acceptProposedAction()


    #=============================로그인, task 목록을 가져오는====================================


    def login_and_load_tasks(self):
        user_data = UserAuthenticator.login(self.username)

        if user_data:
            user_id = user_data["id"]
            user_tasks = manager.get_tasks_by_user(user_id) 
            self.populate_table(user_tasks)
        else:
            popup.show_message("error", "오류", "부여받은 Task가 없습니다")



    #=============================GroupBox를 ListWidget에 추가======================================

    def populate_table(self, tasks):
        if not tasks:
            popup.show_message("error", "오류", "Task를 찾을 수 없습니다.")
            return

        index = 0
        # delay = 400

        status_list = ["wtg", "ip", "fin"]

        for status in status_list:
            filtered_tasks = manager.filter_tasks_by_status(tasks, status)

            for task in filtered_tasks:
                task_id = task["id"] 
                task_name = task["content"] 
                versions = manager.get_works_for_task(task_id)

                # for version in versions:
                #     thumbnail_url = version.get("thumbnail", None)

                file_box = QGroupBox()
                # file_box.setStyleSheet("""
                #     background-color: #F5F5F5; 
                #     border: 2px solid #333333; 
                #     border-radius: 10px;
                #     padding: 10px;
                # """)

                layout = QVBoxLayout()

                label_thumbnail = QLabel()
            

                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_task_name)
                
                file_box.setLayout(layout)

                # QListWidgetItem 생성
                list_item = QListWidgetItem()
                list_item.setSizeHint(file_box.sizeHint())
                list_item.setData(Qt.UserRole, {"id": task_id, "name": task_name})  # Task 데이터 저장

                # QListWidget에 추가
                target_list = self.list_widgets[index]
                target_list.addItem(list_item)
                target_list.setItemWidget(list_item, file_box)

                # 리스트 아이템 클릭 시 show_task_details 실행
                target_list.itemClicked.connect(self.on_item_clicked)

                # QTimer.singleShot(index * delay, lambda fb=file_box: self.animate_widget(fb, duration=1800))
            index += 1
    
    def on_item_clicked(self, item):
        """
        리스트 아이템 클릭 시 해당 Task ID를 show_task_details로 전달
        """
        task_data = item.data(Qt.UserRole)
        if task_data:
            task_id = task_data["id"]
            self.show_task_details(task_id)

    def get_filetype(self, file_name):
        if file_name == None:
            return "work file 없음"
        elif file_name.endswith((".ma", ".mb")):
            return "Maya 파일"
        elif file_name.endswith(".nk"):
            return "Nuke 파일"
        elif file_name.endswith(".hip"):
            return "Houdini 파일"
        else:
            return "알 수 없는 파일 형식"

    def show_task_details(self, task_id, event=None):
        task = manager.get_task_by_id(task_id)
        works = manager.get_works_for_task(task_id)
        if works:
            file_name = works[-1]['path']
        else:
            file_name = None

        self.ui.label_filename.setText(task['content'])
        self.ui.label_startdate.setText(task["start_date"])
        self.ui.label_duedate.setText(task["due_date"])

        file_type = self.get_filetype(file_name)
        self.ui.label_type.setText(file_type)  

        self.ui.tabWidget_info.show()

    def loadmayanuke(self):
        """
        선택된 Task의 파일을 열기
        """
        selected_items = [widget.currentItem() for widget in self.list_widgets if widget.currentItem()]

        for selected_item in selected_items:
            task_data = selected_item.data(Qt.UserRole)
            if not task_data:
                print("Task 데이터를 찾을 수 없습니다.")
                continue

            task_id = task_data["id"]
            file_paths = manager.get_works_for_task(task_id)
            count = len(file_paths)-1

            if not file_paths:
                print(f"Task {task_id}에 연결된 파일이 없습니다.")
                continue

            file_path = file_paths[count]["path"]
            if not file_path:
                print(f"Task {task_id}의 파일 경로를 찾을 수 없습니다.")
                continue

            # 파일 확장자에 따라 Maya 또는 Nuke 실행
            if file_path.endswith((".ma", ".mb")):
                print(f"Maya에서 열기: {file_path}")
                MayaLoader.launch_maya(file_path)  

            elif file_path.endswith(".nk"):
                print(f"Nuke에서 열기: {file_path}")
                NukeLoader.launch_nuke(file_path)  

            else:
                print(f"지원되지 않는 파일 유형: {file_path}")

 #//////////////////////////////////////listwidget ui 설정용 ////////////////

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())