from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QGroupBox, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QWidget, QScrollArea, 
    QTabWidget, QPushButton, QLineEdit, QGraphicsOpacityEffect, QGridLayout,QTableWidget, QTableWidgetItem
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QPropertyAnimation, QRect, QTimer, QMimeData, QUrl
from PySide6.QtGui import QPixmap, QColor, QDrag
import sys, os, glob
from shotgun_api3 import Shotgun
from functools import partial 


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loader')))
from MayaLoader import MayaLoader
from NukeLoader import NukeLoader

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
        
        # self.animate_list_widgets() 
        self.login_and_load_tasks()

        self.setGeometry(100, 100, 1800, 1000)
        self.resize(1000, 650)


        self.selected_task_ids = []  # 선택된 Task ID 저장
        self.start_pos = None  # 마우스 클릭 시작 위치 저장

        self.pushButton_open = self.ui.findChild(QPushButton, "pushButton_open")
        self.ui.pushButton_open.clicked.connect(self.loadmayanuke) # open 버튼을 누르면 마야와 누크 파일이 열리도록 


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
        self.tableWidget_exr = self.ui.findChild(QTableWidget, "tableWidget_exr")
        self.tab_widget = self.ui.findChild(QTabWidget, "tabWidget_2")
        self.label_filename_2 = self.ui.findChild(QLabel, "label_filename_2")
        self.label_filetype_2 = self.ui.findChild(QLabel, "label_filetype_2")

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)

    

        # ✅ 탭 숨기기
        self.tab_widget.hide()



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

        # # 스크롤 영역과 컨테이너 배경색을 어두운 회색으로 설정
        # self.scroll_area.setStyleSheet("background-color: #181818;")
        # self.scroll_widget.setStyleSheet("background-color: #181818;")

        
        self.label_filename = self.ui.findChild(QLabel, "label_filename")
        self.label_type = self.ui.findChild(QLabel, "label_type")
        self.label_startdate = self.ui.findChild(QLabel, "label_startdate")
        self.label_duedate = self.ui.findChild(QLabel, "label_duedate")

        # 클릭 이벤트 전에는 숨기기 
        self.tab_widget.hide()

        # listwidget의 색깔 설정 
        self.list_widgets = []
        row_colors = ["#012E40", "#03A696", "#024149", "#F28705"]

        # 행이 될 3개의 listwidget (크기, 간격, 색 조정하여 tableWidget_2에 삽입) 
        for i in range(3):
            list_widget = DraggableListWidget()
            list_widget.setFixedWidth(220)
            list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            # list_widget.setStyleSheet(f"background-color: {row_colors[i]}; border-radius: 15px; margin-right: 20px;")
            list_widget.setSpacing(10)

            self.scroll_layout.addWidget(list_widget)
            self.list_widgets.append(list_widget)


    #=============================로그인, task 목록을 가져오는====================================


    def login_and_load_tasks(self):
        user_data = UserAuthenticator.login(self.username)

        if "error" not in user_data:
            user_id = user_data["id"]
            user_tasks = manager.get_tasks_by_user(user_id) 
            self.populate_table(user_tasks)
        else:
            print("Error")

    #=============================ListWidget 애니메이션 추가====================================


    # def animate_list_widgets(self):
    #     delay = 400  # 0.4초 간격으로 순차적 애니메이션 실행 

    #     for index, list_widget in enumerate(self.list_widgets):
    #         QTimer.singleShot(index * delay, lambda lw=list_widget: self.animate_widget(lw, duration=600))


    #=============================애니메이션 적용=============================================


    # def animate_widget(self, widget, duration=600):
    #     start_y = widget.y() + 40
    #     end_y = widget.y()  

    #     anim = QPropertyAnimation(widget, b"geometry")
    #     anim.setDuration(duration)  

    #     # (고정 : x 좌표, 넓이, 길이/   이동: y좌표 )
    #     anim.setStartValue(QRect(widget.x(), start_y, widget.width(), widget.height()))
    #     anim.setEndValue(QRect(widget.x(), end_y, widget.width(), widget.height()))


    #     self.animations.append(anim)  
    #     anim.start()

    #     effect = QGraphicsOpacityEffect()
    #     widget.setGraphicsEffect(effect)
    #     # 투명도 조절 [시작(0) > (1)]
    #     fade_anim = QPropertyAnimation(effect, b"opacity")
    #     fade_anim.setDuration(duration)
    #     fade_anim.setStartValue(0.0)
    #     fade_anim.setEndValue(1.0)
    #     self.effects.append(effect)  
    #     self.animations.append(fade_anim)  
    #     fade_anim.start()

    #=============================GroupBox를 ListWidget에 추가======================================

    # groupbox = 파일 listwidget= 파일을 담는 행 


    def populate_table(self, tasks):
        if not tasks:
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
                # if thumbnail_url:
                #     pixmap = QPixmap(thumbnail_url)
                #     label_thumbnail.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
                # layout.addWidget(label_thumbnail, alignment=Qt.AlignCenter)

                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_task_name)
                
                file_box.setLayout(layout)
                file_box.mousePressEvent = partial(self.show_task_details, task_id)

                list_item = QListWidgetItem()
                list_item.setSizeHint(file_box.sizeHint())
                list_item.setData(Qt.UserRole, {"id": task_id, "name": task_name})  # Task 데이터 저장

                target_list = self.list_widgets[index]
                target_list.addItem(list_item)
                target_list.setItemWidget(list_item, file_box)

                # QTimer.singleShot(index * delay, lambda fb=file_box: self.animate_widget(fb, duration=1800))

            index += 1


    def get_filetype(self, file_name):
    
        if file_name == None:
            return "work file 없음"
        elif file_name.endswith((".ma", ".mb")):
            return "Maya 파일"
        elif file_name.endswith(".nk"):
            return "Nuke 파일"
        else:
            return "알 수 없는 파일 형식"

    def show_task_details(self, task_id, event=None):
        task = manager.get_task_by_id(task_id)
        self.label_filename.setText(task['content']) 
        self.label_startdate.setText(task["start_date"])
        self.label_duedate.setText(task["due_date"])


        works = manager.get_works_for_task(task_id)
        if works:
            count = len(works)-1
            file_name = works[count]['path']
        else:
            file_name = None
        file_type = self.get_filetype(file_name)
        self.label_type.setText(file_type)  

        self.tab_widget.show()

    def loadmayanuke(self):
        """선택된 Task의 파일을 열기"""
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





    
    



class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)  # 드래그 가능하도록 설정

    def mousePressEvent(self, event):
        """마우스 클릭 시 드래그할 아이템을 저장"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """드래그 발생 감지"""
        if not hasattr(self, "start_pos"):
            return

        distance = (event.pos() - self.start_pos).manhattanLength()
        if event.buttons() == Qt.LeftButton and distance > 10:  # 최소 드래그 거리 설정
            self.startDrag()
        super().mouseMoveEvent(event)

    def startDrag(self):
        """드래그 이벤트 실행"""
        selected_item = self.currentItem()
        if not selected_item:
            return

        task_data = selected_item.data(Qt.UserRole)  # Task ID 또는 데이터 가져오기
        file_paths = manager.get_works_for_task(task_data["id"])

        if not file_paths:
            print("⚠ 드래그할 파일이 없음")
            return
        
        file_path = file_paths[0].get("path")  # 첫 번째 파일 경로 가져오기

        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(file_path)])  # OS에서 Drag & Drop 지원

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)

   
    # def load_assets(self):
    #         self.listWidget_asset = self.ui.findChild(QListWidget, "listWidget_asset")
    #         self.listWidget_clip = self.ui.findChild(QListWidget, "listWidget_clip")
    #         self.listWidget_pub = self.ui.findChild(QListWidget, "listWidget_pub")
    #         self.listWidget_hm = self.ui.findChild(QListWidget, "listWidget_hm")
    #         self.listWidget_bookmark = self.ui.findChild(QListWidget, "listWidget_bookmark")

    #         self.label_filename_2 = self.ui.findChild(QLabel, "label_filename_2")
    #         self.label_filetype_2 = self.ui.findChild(QLabel, "label_filetype_2")


    #         self.pushButton_import = self.ui.findChild(QPushButton, "pushButton_import")
    #         self.pushButton_reference = self.ui.findChild(QPushButton, "pushButton_reference")


       
    #         assets = manager.get_assets(1)  # 프로젝트 ID는 예시로 1 사용
    #         if not assets:
    #             return

    #         self.listWidget_asset.clear()

    #         grid_layout = QGridLayout()
    #         row, col = 0, 0

    #         for asset in assets:
    #             asset_id = asset["id"]
    #             asset_name = asset["code"]

    #             # Asset 파일 박스
    #             file_box = QGroupBox()
    #             layout = QVBoxLayout()

    #             label_name = QLabel(asset_name)
    #             label_name.setAlignment(Qt.AlignCenter)
    #             layout.addWidget(label_name)

    #             file_box.setLayout(layout)
    #             file_box.mousePressEvent = partial(self.show_asset_details, asset_id)

    #             list_item = QListWidgetItem()
    #             list_item.setSizeHint(file_box.sizeHint())

    #             self.listWidget_asset.addItem(list_item)
    #             self.listWidget_asset.setItemWidget(list_item, file_box)

    #             # 가로 파일 3개 배치 후 다음 줄로 이동
    #             col += 1
    #             if col >= 3:
    #                 col = 0
    #                 row += 1



if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())