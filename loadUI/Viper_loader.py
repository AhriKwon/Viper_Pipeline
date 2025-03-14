from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QGraphicsOpacityEffect, QGridLayout,QTableWidget, QTableWidgetItem, QCheckBox,QGraphicsOpacityEffect,QGraphicsBlurEffect,
    QLabel
    )
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile, Qt, QPropertyAnimation, QRect, QTimer, QMimeData, QUrl,
    QByteArray, QDataStream, QIODevice, QTimer, QPoint,QPropertyAnimation,QEasingCurve
    

    )
from PySide6.QtGui import QRegion, QPainter  
from PySide6.QtGui import QPixmap, QColor, QDrag,QPainter, QBrush

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
from final_test import FileLoaderGUI
# 로더 UI
import UI_support
from Viper_loader_lib import LibraryTab

 #============================================================================================
 #================================로그인 창 : LoginWindow==============================================


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
    
    def load_ui(self):
        current_directory = os.path.dirname(__file__)
        ui_file_path = f"{current_directory}/newlogin.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        # 로그인 창 크기 조정 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(734, 491)
        # 창 프레임 제거
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        # 창 배경을 검정색으로 설정하여 투명도 문제 해결
        self.setStyleSheet("background-color: black; border: none;")
        
        self.label_background = self.ui.findChild(QLabel, "label_background")
        self.label_id = self.ui.findChild(QLabel, "label_id")
        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.label_id = self.ui.findChild(QLabel, "label_id") 
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")
        self.pushButton_help = self.ui.findChild(QPushButton, "pushButton_help")

        image_path = f"{current_directory}/forui/login.png"  # 배경 이미지 경로 확인
        self.label_background.setPixmap(QPixmap(image_path))
        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        image_path = f"{current_directory}/forui/Group 3995.png"  # 배경 이미지 경로 확인
        self.label_id.setPixmap(QPixmap(image_path))
        self.label_id.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        #로그인 버튼
        self.pushButton_login.clicked.connect(self.attempt_login)
        self.label_background = self.ui.findChild(QLabel, "label_background")

        image_path = "/nas/Viper/minseo/forui/login.png"  # 배경 이미지 경로 확인
        self.label_background.setPixmap(QPixmap(image_path))
        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        image_path_2 = "/nas/Viper/minseo/forui/Group 3995.png"  # 배경 이미지 경로 확인
        self.label_id.setPixmap(QPixmap(image_path_2))
        self.label_id.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        self.label_id.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정
        self.setAttribute(Qt.WA_TranslucentBackground)  # 창의 배경을 투명하게 설정
    

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 전체 창 크기 가져오기
        rect = self.rect()

        # 배경을 투명하게 설정
        painter.setBrush(QBrush(Qt.transparent))
        painter.setPen(QColor(0, 0, 0))  # 검정색 테두리

        # 검정 테두리를 그리기 (1px)
        painter.drawRect(rect.adjusted(10, 10, -10, -10))  # 안쪽으로 1px 조정하여 테두리만 표시
        self.forlogin_ani()
      


    #/////////////////////로그인창 애니메이션 실행 함수 넣는 곳!!1/////////////////////////////////////

    def forlogin_ani(self):
       

        # 텍스트 애니메이션 설정
        self.full_text = "Please enter your e-mail"  # 최종 표시될 텍스트
        self.current_text = ""  # 현재 보여질 텍스트
        self.text_index = 0  # 현재 위치 인덱스

        # QTimer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_placeholder)
        self.timer.start(100)  # 100ms 간격으로 실행

    def update_placeholder(self):
        """ 한 글자씩 placeholder에 추가하는 함수 """
        if self.text_index < len(self.full_text):
            self.current_text += self.full_text[self.text_index]  # 한 글자 추가
            self.lineEdit_id.setPlaceholderText(self.current_text)  # 업데이트
            self.text_index += 1  # 다음 인덱스로 이동
        else:
            self.timer.stop()  # 모든 글자가 추가되면 타이머 중지

    



    #///////////////////////////////////////////////////////////////////////////////////////////////


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
            UI_support.show_message("error", "오류", "이메일을 입력해주세요")
            return
        
        user_data = UserAuthenticator.login(email)

        if user_data:
            self.accept()
            # self.main_window = LoadUI(email)
            self.fade_out_animation()
            self.main_window.show()
           
        else:
            UI_support.show_message("error", "오류", "등록되지 않은 사용자입니다")
            return
        
    def fade_out_animation(self):
        """로그인 창이 서서히 사라지는 애니메이션 효과"""
        print("🎬 로그인 창 페이드 아웃 애니메이션 시작!")  # ✅ 디버깅용 출력

        # 🔹 투명도 효과 적용
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # 🔹 투명도 애니메이션 설정 (1.0 → 0.0)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(2000)  # 2초 동안 서서히 사라짐
        self.animation.setStartValue(1.0)  # 처음에는 불투명
        self.animation.setEndValue(0.0)  # 완전히 투명

        # 🔹 애니메이션이 끝나면 `open_main_window()` 실행
        self.animation.finished.connect(self.open_main_window)
        self.animation.start()
    def open_main_window(self):
        """애니메이션 종료 후 메인 윈도우 실행"""
        print("🟢 애니메이션 완료 → 메인 윈도우 실행!")
        self.accept()  # 로그인 창 닫기
        self.main_window = LoadUI(self.lineEdit_id.text().strip())  # 메인 윈도우 실행
        self.main_window.show()



        

 #==========================================================================================
 #====================loader ui class : LoadUI==============================================
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
            """
            QListWidgetItem을 PNG 이미지로 대체
            """
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

            
#==========================================================================================
#====================loader ui class : LoadUI==============================================


class LoadUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.projects = manager.get_projects()
        self.animations = []
        self.effects = []
        self.load_ui()
        self.setGeometry(100, 100, 1240, 800)
        self.resize(1240, 720)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 🔹 타이틀바 제거
        self.setAttribute(Qt.WA_TranslucentBackground)  # 🔹 배경 투명 설정
        
        self.setGeometry(100, 100, 1800, 1000)
        self.resize(1000, 650)

        """My Task tab"""
        self.login_and_load_tasks()

        """Lib tab"""
        self.library_manager = LibraryTab(self.ui)

        """이벤트"""
        self.ui.pushButton_open.clicked.connect(self.run_file) # open 버튼을 누르면 마야와 누크 파일이 열리도록
        self.ui.listWidget_works.itemDoubleClicked.connect(self.run_file)

        # ip 리스트 위젯 상태가 바뀔 때 마다 새로고침
        self.list_widgets[1].itemChanged.connect(lambda item: self.update_list_items(self.list_widgets[1]))

        # ✅ 메인 윈도우 흐려지게 시작하고 점점 뚜렷하게
        self.blur_in_animation()

        
        

  #====================================loadui 로드=======================================
  #================================(loginui가 성공할 시에)=================================

    def load_ui(self):
        current_directory = os.path.dirname(__file__)
        ui_file_path = f"{current_directory}/lastload.ui"

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()
        

        self.list_widgets = [self.ui.listWidget_wtg, self.ui.listWidget_ip, self.ui.listWidget_fin]

    
    def blur_in_animation(self):
        """ 🎬 메인 윈도우가 흐릿하게 시작되었다가 점점 선명해지는 효과 """
        print("🎬 메인 윈도우 블러 애니메이션 시작!")
        
        # 블러 효과 적용
        self.blur_effect = QGraphicsBlurEffect(self)  # 블러 효과 객체 생성
        self.blur_effect.setBlurRadius(20)  # 초기에 블러 강도 (최대 흐림)
        self.setGraphicsEffect(self.blur_effect)  # 현재 창에 블러 적용

        # 블러 애니메이션 설정 (BlurRadius: 20 → 0)
        self.animation = QPropertyAnimation(self.blur_effect, b"blurRadius")
        self.animation.setDuration(1300)  # 2초 동안 점점 선명해짐
        self.animation.setStartValue(20)  # 처음에는 블러 효과 강함
        self.animation.setEndValue(0)  # 점점 선명하게

        # 부드러운 가속도 설정
        self.animation.finished.connect(self.animate_labels)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # 자연스럽게 변화
        self.animation.start()

#=============================로그인, task 목록을 가져오는 함수====================================

    def login_and_load_tasks(self):
        user_data = UserAuthenticator.login(self.username)

        if user_data:
            user_id = user_data["id"]
            user_tasks = manager.get_tasks_by_user(user_id) 
            self.populate_table(user_tasks)
        else:
            UI_support.show_message("error", "오류", "부여받은 Task가 없습니다")

    def populate_table(self, tasks):
        """
        Task 데이터를 받아서 list_widgets에 QListWidgetItem을 추가
        """
        if not tasks:
            UI_support.show_message("error", "오류", "Task를 찾을 수 없습니다.")
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
                task_id = task_data.get("id", "Unknown Task")
                task_path = manager.get_task_publish_path(self.projects[0], task_id)  # 퍼블리시 경로 가져오기
                thumbnail_path = self.get_latest_thumbnail(task_path)  # 최신 썸네일 가져오기

                # file_box 생성
                widget = QWidget()
                layout = QVBoxLayout()

                # 썸네일 QLabel
                label_thumb = QLabel()
                if os.path.exists(thumbnail_path):
                    pixmap = QPixmap(thumbnail_path)
                else:
                    pixmap = QPixmap(160, 90)  # 기본 썸네일 생성
                rounded_pixmap = UI_support.round_corners_pixmap(pixmap, radius=15)
                label_thumb.setPixmap(rounded_pixmap.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                label_thumb.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_thumb)

                # 테스크 이름 QLabel
                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                label_task_name.setStyleSheet("color: white;")  # 흰색 텍스트 적용

                layout.addWidget(label_task_name)

                widget.setLayout(layout)

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
            self.show_task_works(task_id)

    def get_latest_thumbnail(self, task_path):
        """
        해당 테스크의 퍼블리시 썸네일 폴더에서 가장 최근 생성된 이미지를 찾음
        """
        thumb_path = os.path.join(task_path, "thumb")
        print(f"경로 중간점검: {thumb_path}")
        
        if not os.path.exists(thumb_path) or not os.path.isdir(thumb_path):
            return "/nas/Viper/thumb.jpg"
        
        # 지원하는 이미지 확장자
        valid_extensions = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
        
        # 해당 폴더 내 파일 목록 가져오기 (이미지 파일만 필터링)
        image_files = [f for f in os.listdir(thumb_path) if f.lower().endswith(valid_extensions)]
        print(f"이미지 있?: {image_files}")
        
        if not image_files:
            return
        
        # 가장 최근 생성된 파일 찾기 (생성 시간 기준 정렬)
        image_files.sort(key=lambda f: os.path.getctime(os.path.join(thumb_path, f)), reverse=True)
        latest_thumbnail = os.path.join(thumb_path, image_files[0])

        return latest_thumbnail

    def get_filetype(self, file_name):
        if file_name == None:
            return "work file 없음"
        elif file_name.endswith((".ma", ".mb")):
            return "Maya"
        elif file_name.endswith((".nk", ".nknc")):
            return "Nuke"
        elif file_name.endswith((".hip", ".hiplc", ".hipnc")):
            return "Houdini"
        else:
            return "알 수 없는 파일 형식"

    def show_task_details(self, task_id, event=None):
        """
        클릭한 테스크 정보를 info탭에 띄워주는 함수
        """
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

    def show_task_works(self, task_id, event=None):
        """
        클릭한 테스크의 work파일들을 리스트 위젯에 보여주는 함수
        """
        self.ui.listWidget_works.clear()

        # 데이터베이스에서 works 가져오기
        works = manager.get_works_for_task(task_id)

        if not works:
            return

        # works 데이터 추가
        for work in works:
            file_name = work["file_name"]  # 파일 이름이 없을 경우 기본값 설정
            file_type = self.get_filetype(file_name)
            
            # 파일 형식에 맞게 로고 QLabel을 설정
            label_logo = QLabel()
            if file_type == "Maya":
                pixmap = QPixmap("/nas/Viper/logo/maya.png")
            elif file_type == "Nuke":
                pixmap = QPixmap("/nas/Viper/logo/nuke.png")
            elif file_type == "Houdini":
                pixmap = QPixmap("/nas/Viper/logo/houdini.png")
            else:
                pixmap = QPixmap(20, 20)
            label_logo.setPixmap(pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label_logo.setMaximumSize(20, 20)


            # 파일 이름 QLabel
            label_name = QLabel(file_name)
            label_name.setStyleSheet("color: white;")
            # H_layout에 라벨 추가
            H_layout = QHBoxLayout()
            H_layout.addWidget(label_logo)
            H_layout.addWidget(label_name)
            # 레이아웃을 QWidget에 설정
            item_widget = QWidget()
            item_widget.setLayout(H_layout)

            item = QListWidgetItem()  # 리스트 아이템 생성
            item.setSizeHint(item_widget.sizeHint())
            # QListWidget에 아이템 추가 후 위젯 설정
            self.ui.listWidget_works.addItem(item)
            self.ui.listWidget_works.setItemWidget(item, item_widget)
            item.setData(Qt.UserRole, work)

    def run_file(self):
        """
        설정된 파일 경로를 읽고 Maya or Nuke or Houdini에서 실행
        """
        selected_items = [self.ui.listWidget_works.currentItem()]
        print(f"선택된 아이템: {selected_items}")
        
        for selected_item in selected_items:
            work_data = selected_item.data(Qt.UserRole)
            if not work_data:
                UI_support.show_message("error", "오류", "work 데이터를 찾을 수 없습니다.")
                continue

            work_name = work_data["file_name"]

            file_path = work_data["path"]
            print(f"파일 경로: {file_path}")

            if not file_path:
                UI_support.show_message("error", "오류", f"{work_name}의 파일 경로를 찾을 수 없습니다.")
                continue

        # 경로를 절대 경로로 변환
        file_path = os.path.abspath(file_path)

        if file_path.endswith((".ma", ".mb")):
            MayaLoader.launch_maya(file_path)
        elif file_path.endswith((".nk", ".nknc")):
            NukeLoader.launch_nuke(file_path)
        elif file_path.endswith((".hip", ".hiplc", ".hipnc")):
            FileLoaderGUI.launch_houdini(file_path)
        else:
            UI_support.show_message("error", "오류", "지원되지 않는 파일 형식입니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())