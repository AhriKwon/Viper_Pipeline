from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QGraphicsOpacityEffect, QGridLayout,QTableWidget, QTableWidgetItem, QCheckBox
    )
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile, Qt, QPropertyAnimation, QRect, QTimer, QMimeData, QUrl,
    QByteArray, QDataStream, QIODevice
    )
from PySide6.QtGui import QPixmap, QColor, QDrag

import sys, os, glob
from functools import partial 
# 샷그리드 API
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()
# 로더
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loader')))
from MayaLoader import MayaLoader
from NukeLoader import NukeLoader
# 팝업 UI
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
        self.resize(600, 700)
        
        
        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")
       
        self.pushButton_login.clicked.connect(self.attempt_login)

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


 #==========================================================================================
 #====================loader ui class : LoadUI==============================================


class LoadUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.animations = []
        self.effects = []
        self.load_ui()
        
        self.login_and_load_tasks()

        self.setGeometry(100, 100, 1800, 1000)
        self.resize(1000, 650)

        self.pushButton_open = self.ui.findChild(QPushButton, "pushButton_open")
        self.ui.pushButton_open.clicked.connect(self.loadmayanuke) # open 버튼을 누르면 마야와 누크 파일이 열리도록 

        # ip 리스트 위젯 상태가 바뀔 때 마다 새로고침
        self.list_widgets[1].itemChanged.connect(lambda item: self.update_list_items(self.list_widgets[1]))


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

        """My Task tab"""
        # listwidget의 색깔 설정 
        self.list_widgets = [self.ui.listWidget_wtg, self.ui.listWidget_ip, self.ui.listWidget_fin]
        list_labels = [self.ui.label_wtg, self.ui.label_ip, self.ui.label_fin]
        row_colors = ["#012E40", "#03A696", "#024149", "#F28705"]

        # 행이 될 3개의 listwidget (색, 형태 조정)
        for i, list_widget in enumerate(self.list_widgets):
            list_widget.setStyleSheet(f"background-color: {row_colors[i]}; border-radius: 15px; margin-right: 20px;")
        
        for i, list_label in enumerate(list_labels):
            list_label.setStyleSheet(f"background-color: {row_colors[i]}; border-radius: 15px; margin-right: 20px;")


        """Lib tab"""
        self.library_manager = LibraryTabManager(self.ui)


#=============================로그인, task 목록을 가져오는 함수====================================

    def login_and_load_tasks(self):
        user_data = UserAuthenticator.login(self.username)

        if user_data:
            user_id = user_data["id"]
            user_tasks = manager.get_tasks_by_user(user_id) 
            self.populate_table(user_tasks)
        else:
            popup.show_message("error", "오류", "부여받은 Task가 없습니다")

    def populate_table(self, tasks):
        """
        Task 데이터를 받아서 list_widgets에 QListWidgetItem을 추가
        """
        if not tasks:
            popup.show_message("error", "오류", "Task를 찾을 수 없습니다.")
            return

        index = 0
        status_list = ["wtg", "ip", "fin"]

        for status in status_list:
            filtered_tasks = manager.filter_tasks_by_status(tasks, status)

            for task in filtered_tasks:
                task_id = task["id"]
                task_name = task["content"]

                # 리스트 아이템 생성
                list_item = QListWidgetItem()
                list_item.setData(Qt.UserRole, {"id": task_id, "name": task_name})  # Task 데이터 저장
                list_item.setTextAlignment(Qt.AlignCenter)

                # QListWidget에 추가 (초기 상태에서는 UI 요소 없이 추가)
                target_list = self.list_widgets[index]
                target_list.addItem(list_item)

                # 리스트 아이템 클릭 시 show_task_details 실행
                target_list.itemClicked.connect(self.on_item_clicked)

            self.update_list_items(self.list_widgets[index])
            index += 1

    def update_list_items(self, list_widget):
        """
        특정 리스트 위젯(list_widget)에 있는 모든 아이템을 file_box로 업데이트
        """
        for index in range(list_widget.count()):
            list_item = list_widget.item(index)  # 리스트 위젯 내의 아이템 가져오기

            if list_item:
                task_data = list_item.data(Qt.UserRole)  # Task 데이터 가져오기
                task_name = task_data.get("name", "Unknown Task")

                # file_box 생성
                widget = QWidget()
                layout = QVBoxLayout()

                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_task_name)
                
                widget.setLayout(layout)
                widget.setContentsMargins(20, 0, 0, 0)

                # 기존 list_item의 크기 조정 및 file_box 추가
                list_item.setSizeHint(widget.sizeHint())
                list_widget.setItemWidget(list_item, widget)
    
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


#=============================Lib탭 테이블 위젯 생성====================================


class LibraryTabManager:
    def __init__(self, ui):
        self.ui = ui
        self.table_widget = QTableWidget()  # 테이블 위젯 생성
        self.setup_table()
        self.setup_connections()

        # 폴더 경로 매핑
        self.folder_paths = {
            "asset": "/nas/show/Viper/lib/asset",
            "clip": "/nas/show/Viper/lib/clip",
            "exr": "/nas/show/Viper/lib/exr",
            "rig": "/nas/show/Viper/lib/rig"
        }

        self.bookmarked_items = []  # 북마크된 항목 저장

    def setup_table(self):
        """
        테이블 위젯 초기 설정
        """
        self.table_widget.setColumnCount(1)  # 컬럼 1개 (폴더 정보)
        self.table_widget.setHorizontalHeaderLabels(["Library"])
        self.table_widget.setColumnWidth(0, 200)  # 폴더 이름 너비
        self.table_widget.setRowCount(0)  # 초기 행 개수 0
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 불가
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)  # 하나만 선택 가능
        self.table_widget.setShowGrid(False)  # 그리드 없애기

    def setup_connections(self):
        """
        탭 변경 시 폴더 내용 업데이트
        """
        self.ui.tabWidget_lib.currentChanged.connect(self.load_files)

    def load_files(self, index):
        """
        선택된 탭에 맞는 폴더의 파일을 로드
        """
        tab_name = self.ui.tabWidget_lib.tabText(index).lower()
        folder_path = self.folder_paths.get(tab_name)

        # 기존 데이터 초기화
        self.table_widget.setRowCount(0)

        if not folder_path or not os.path.exists(folder_path):
            return  # 폴더가 없으면 종료

        # 폴더 내 디렉토리 검색
        for folder in os.listdir(folder_path):
            folder_full_path = os.path.join(folder_path, folder)
            if os.path.isdir(folder_full_path):  # 폴더만 추가
                self.add_table_item(folder)

    def add_table_item(self, folder_name, thumbnail_path=""):
        """
        테이블 위젯에 폴더 아이템을 추가 (썸네일, 폴더 이름, 북마크 체크박스 포함)
        """
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # 셀에 들어갈 위젯 생성
        cell_widget = QWidget()
        layout = QVBoxLayout()

        # 썸네일 QLabel (기본값 제공)
        label_thumbnail = QLabel()
        pixmap = QPixmap(thumbnail_path) if thumbnail_path and os.path.exists(thumbnail_path) else QPixmap(80, 80)
        label_thumbnail.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_thumbnail.setAlignment(Qt.AlignCenter)

        # 폴더 이름 QLabel
        label_name = QLabel(folder_name)
        label_name.setAlignment(Qt.AlignCenter)

        # 북마크 체크박스
        bookmark_checkbox = QCheckBox()
        bookmark_checkbox.setStyleSheet("QCheckBox { margin-left: 10px; }")  # 체크박스 스타일 조정
        bookmark_checkbox.stateChanged.connect(lambda state, f=folder_name: self.update_bookmark(state, f))

        # 레이아웃에 추가
        layout.addWidget(label_thumbnail)
        layout.addWidget(label_name)
        layout.addWidget(bookmark_checkbox)
        layout.setAlignment(Qt.AlignCenter)  # 모든 요소 중앙 정렬
        cell_widget.setLayout(layout)

        # 테이블에 위젯 추가
        self.table_widget.setCellWidget(row_position, 0, cell_widget)

    def update_bookmark(self, state, folder_name):
        """
        북마크 상태 업데이트
        """
        if state == Qt.Checked:
            if folder_name not in self.bookmarked_items:
                self.bookmarked_items.append(folder_name)
        else:
            if folder_name in self.bookmarked_items:
                self.bookmarked_items.remove(folder_name)

        self.update_bookmark_tab()

    def update_bookmark_tab(self):
        """
        북마크된 폴더를 `tab_bookmark`에 업데이트
        """
        self.ui.tab_bookmark.setRowCount(0)  # 기존 항목 초기화
        for folder_name in self.bookmarked_items:
            row_position = self.ui.tab_bookmark.rowCount()
            self.ui.tab_bookmark.insertRow(row_position)
            item = QTableWidgetItem(folder_name)
            item.setTextAlignment(Qt.AlignCenter)
            self.ui.tab_bookmark.setItem(row_position, 0, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())