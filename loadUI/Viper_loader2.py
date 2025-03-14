from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QGraphicsOpacityEffect, QGridLayout,QTableWidget, QTableWidgetItem, QCheckBox,QGraphicsOpacityEffect,QGraphicsBlurEffect,
    QLabel, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget,
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
# 로더 UI
import popup
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
        self.setWindowFlags(Qt.FramelessWindowHint)  # 🔹 타이틀바 제거
        self.setAttribute(Qt.WA_TranslucentBackground)  # 🔹 배경 투명 설정
        self.dragPos = None  # 창 이동을 위한 변수

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        # 로그인 창 크기 조정 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(741, 491)
        
        
       
        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.label_id = self.ui.findChild(QLabel, "label_id") 
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")
        self.pushButton_help = self.ui.findChild(QPushButton, "pushButton_help") 
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


    # 만약 email이 맞다면 mainwindow(loadui)가 실행되도록
    def attempt_login(self):
        email = self.lineEdit_id.text().strip()

        if not email:
            popup.show_message("error", "오류", "이메일을 입력해주세요")
            return
        
        user_data = UserAuthenticator.login(email)

        if user_data:
            self.accept()
            # self.main_window = LoadUI(email)
            self.fade_out_animation()
            self.main_window.show()
           
        else:
            popup.show_message("error", "오류", "등록되지 않은 사용자입니다")
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


class LoadUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.animations = []
        self.effects = []
        self.load_ui()
        self.setGeometry(100, 100, 1240, 800)
        self.resize(1240, 720)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 🔹 타이틀바 제거
        self.setAttribute(Qt.WA_TranslucentBackground)  # 🔹 배경 투명 설정

        # ✅ 기존 list_widgets를 AnimatedListView로 변경
        self.list_animated_view = AnimatedListView()
        self.ui.verticalLayout_wtg.addWidget(self.list_animated_view)  # UI에 추가
        
        """My Task tab"""
        self.login_and_load_tasks()

        """Lib tab"""
        self.library_manager = LibraryTab(self.ui)
        """이벤트"""
        self.ui.pushButton_open.clicked.connect(self.run_file) # open 버튼을 누르면 마야와 누크 파일이 열리도록 





       
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
        

        # listwidget의 색깔 설정 
        self.list_widgets = [self.ui.listWidget_wtg, self.ui.listWidget_ip, self.ui.listWidget_fin]
        list_labels = [self.ui.label_wtg, self.ui.label_ip, self.ui.label_fin]


        # 행이 될 3개의 listwidget (색, 형태 조정)

    
    def animate_labels(self):
        """ 🎬 라벨이 위에서 아래로 떨어지는 애니메이션 실행 """
        print("🎬 라벨 애니메이션 시작!")

        labels = [
            self.ui.label_ani1,
            self.ui.label_ani2,
            self.ui.label_ani3,
            self.ui.label_ani4,
        ]

        self.label_animations = []  # 애니메이션 객체 저장 리스트 추가
        self.opacity_animations = [] 
        self.initial_positions = {} 

        delays = [500, 200, 100, 20]  
        durations = [700, 1000, 1200, 2500]
        for index, label in enumerate(labels):
            # ✅ QGraphicsOpacityEffect 추가 (처음에는 보이지 않도록)
            opacity_effect = QGraphicsOpacityEffect(label)
            label.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(0)  #  처음에는 완전 투명
            # 초기 위치 저장 (현재 y 좌표를 저장)
            self.initial_positions[label] = label.y()
            start_pos = QPoint(label.x(), self.initial_positions[label] - 150)  # 시작 위치 (위에서 아래로)
            end_pos = QPoint(label.x(), self.initial_positions[label])  # 최종 위치

            label.move(start_pos)  #  시작 위치로 이동 (처음에는 안 보임)
            label.setVisible(False)  # 초기에는 완전히 숨김 (중간에 깜빡이는 문제 해결)

            # QTimer를 활용해 순차적으로 실행되도록 설정
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda lbl=label, dur=durations[index], eff=opacity_effect: self.start_label_animation(lbl, dur, eff))
            timer.start(sum(delays[:index + 1])) 

            self.label_animations.append(timer)
        

    def start_label_animation(self, label, duration, opacity_effect):
        """ 🎬 개별 라벨 애니메이션 실행 (더 부드럽게) """
        print(f"🎬 {label.objectName()} 애니메이션 시작! 지속시간: {duration}ms")
        label.setVisible(True)
        # 위치 애니메이션 (위에서 아래로 이동)
        move_animation = QPropertyAnimation(label, b"pos")
        move_animation.setDuration(duration)
        move_animation.setStartValue(QPoint(label.x(), self.initial_positions[label] - 150))  #  위에서 시작
        move_animation.setEndValue(QPoint(label.x(), self.initial_positions[label]))  #  원래 위치로 이동
        move_animation.setEasingCurve(QEasingCurve.OutCubic)  # 부드러운 감속 곡선

        # 투명도 애니메이션 (부드럽게 나타남)
        fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        fade_animation.setDuration(duration * 0.6)  #  위치보다 약간 빠르게 나타나도록 조절
        fade_animation.setStartValue(0)  # 처음엔 완전 투명
        fade_animation.setEndValue(1)  # 완전 보이게

        self.label_animations.append(move_animation)  # 참조를 유지하여 GC 방지
        self.opacity_animations.append(fade_animation)  # 투명도 애니메이션도 추가

        move_animation.start()
        fade_animation.start()
        self.start_expand_animation()
        self.start_label_left_animation()


    # label_central 용 애니메이션 
    def start_expand_animation(self):
        """ 🎬 중앙 라벨이 마스크처럼 펼쳐지는 애니메이션 """
        print("🎬 중앙 라벨 확장 애니메이션 시작!")

        # ✅ 라벨 가져오기
        self.label_central = self.ui.label_central
        self.label_central.setVisible(False)   

        # ✅ 원본 크기 저장
        original_width = self.label_central.width()
        original_height = self.label_central.height()

        # ✅ 초기 마스크 설정 (중앙 1px만 보이게)
        self.mask_step = 1  # 시작 크기 (1px)
        self.max_mask_width = original_width  # 최종 마스크 크기
        self.label_central.setVisible(False)  # 처음에는 숨김

        # ✅ 0.1초 후 애니메이션 시작 (label_central이 애니메이션 시작 전 보이지 않도록)
        QTimer.singleShot(200, self._start_mask_animation)
    def _start_mask_animation(self):
        """ 🔹 마스크 애니메이션 시작 """
        self.label_central.setVisible(True)  # 이제 보이도록 설정
        self.mask_timer = QTimer(self)
        self.mask_timer.timeout.connect(self._update_mask_animation)
        self.mask_timer.start(25)  # 15ms마다 실행 (부드러운 확장 효과)

    def _update_mask_animation(self):
        """ 🎬 마스크 확장 업데이트 (부드러운 애니메이션) """
        if self.mask_step < self.max_mask_width:
            new_mask = QRegion(
                (self.label_central.width() // 2) - (self.mask_step // 2), 0, 
                self.mask_step, self.label_central.height()
            )
            self.label_central.setMask(new_mask)
            self.mask_step += 4  # 확장 속도 (원하는 대로 조정)
        else:
            self.mask_timer.stop()  # 최대 크기에 도달하면 애니메이션 종료


    def start_label_left_animation(self):
        """ 🎬 label_left가 화면 왼쪽 바깥에서 이동하여 원래 위치로 오는 애니메이션 (label_ani2와 함께 실행) """
        print("🎬 label_left 이동 애니메이션 (label_ani2와 동기화) 시작!")

        # ✅ 라벨 가져오기
        self.label_left = self.ui.label_left  

        # ✅ 현재 위치 저장
        original_x = self.label_left.x()
        original_y = self.label_left.y()

        # ✅ 라벨을 완전히 화면 바깥으로 숨김
        start_x = -self.label_left.width() - 200  # 화면 왼쪽 바깥 더 멀리 이동
        self.label_left.move(start_x, original_y)  
        self.label_left.setVisible(False)  # 처음에는 보이지 않도록 설정

        # ✅ label_ani2가 실행되는 시점과 맞추어 시작 (동시에 실행)
        QTimer.singleShot(0, lambda: self._start_moving_label_left(original_x, original_y, start_x))

    def _start_moving_label_left(self, original_x, original_y, start_x):
        """ 🔹 label_left가 화면 왼쪽에서 원래 위치로 이동하는 애니메이션 실행 """
        print("🎬 label_left 애니메이션 실행!")

        self.label_left.setVisible(True)  # 이제 보이도록 설정

        # ✅ 애니메이션 설정
        self.move_animation = QPropertyAnimation(self.label_left, b"pos", self)
        self.move_animation.setDuration(2500)  # 2.5초 동안 이동 (너무 빠르지 않도록)
        self.move_animation.setStartValue(QPoint(start_x, original_y))  # 화면 왼쪽 바깥에서 시작
        self.move_animation.setEndValue(QPoint(original_x, original_y))  # 원래 위치로 이동
        self.move_animation.setEasingCurve(QEasingCurve.OutBack)  # 감속하면서 부드럽게 등장

        # ✅ 애니메이션 실행
        self.move_animation.start()



    
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
                # ✅ AnimatedListView에 아이템 추가
                self.list_animated_view.add_task(task_name, task_id)

                if hasattr(self, 'list_animated_view'):
                    self.list_animated_view.add_task(task_name, task_id)
                else:
                    print("⚠️ list_animated_view가 아직 초기화되지 않음!")

                # 리스트 아이템 생성
                list_item = QListWidgetItem()
                list_item.setData(Qt.UserRole, {"id": task_id, "name": task_name})  # Task 데이터 저장
                list_item.setTextAlignment(Qt.AlignCenter)

                # QListWidget에 추가 (초기 상태에서는 UI 요소 없이 추가)
                target_list = self.list_widgets[index]
                target_list.addItem(list_item)

                # 리스트 아이템 클릭 시 show_task_details 실행
                target_list.itemClicked.connect(self.on_item_clicked)
                target_list.itemClicked.connect(self.show_task_works)
                

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
                # widget.setContentsMargins(20, 0, 0, 0)

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
        print(task_id)
        # 데이터베이스에서 works 가져오기
        works = manager.get_works_for_task(task_id)
        print(f"💾 로컬 Work 파일 목록: {works}")

        if not works:
            return

        # works 데이터 추가
        for work in works:
            file_name = work.get("file_name", "Unknown File")  # 파일 이름이 없을 경우 기본값 설정
            item = QListWidgetItem(file_name)  # 리스트 아이템 생성
            item.setData(Qt.UserRole, work)  # work 데이터를 저장

            self.ui.listWidget_works.addItem(item)

    def run_file(self):
        """
        설정된 파일 경로를 읽고 Maya or Nuke or Houdini에서 실행
        """
        selected_items = [widget.currentItem() for widget in self.list_widgets if widget.currentItem()]
        
        for selected_item in selected_items:
            task_data = selected_item.data(Qt.UserRole)
            if not task_data:
                print("Task 데이터를 찾을 수 없습니다.")
                continue

            task_id = task_data["id"]
            file_paths = manager.get_works_for_task(task_id)

            if not file_paths:
                popup.show_message("error", "오류", f"Task {task_id}에 연결된 파일이 없습니다.")
                continue

            file_path = file_paths[-1]["path"]
            if not file_path:
                popup.show_message("error", "오류", f"Task {task_id}의 파일 경로를 찾을 수 없습니다.")
                continue
        
        if not file_path or not os.path.exists(file_path):
            popup.show_message("error", "오류", "유효한 파일 경로를 입력하세요.")
            return

        # 경로를 절대 경로로 변환
        file_path = os.path.abspath(file_path)

        if file_path.endswith((".ma", ".mb")):
            MayaLoader.launch_maya(file_path)
        elif file_path.endswith(".nk"):
            NukeLoader.launch_nuke(file_path)
        # elif file_path.endswith((".hip", ".hiplc")):
        #     self.launch_houdini(file_path)
        else:
            popup.show_message("error", "오류", "지원되지 않는 파일 형식입니다.")

    class AnimatedListView(QGraphicsView):
        def __init__(self):
            super().__init__()
            self.setScene(QGraphicsScene(self))
            self.setRenderHint(Qt.Antialiasing)  # 안티앨리어싱 활성화
            self.widgets = []

            # 🔹 UI 요소 설정 (label + listWidget 한 세트)
            widget_names = [
                ("label_wtg", "listWidget_wtg"),
                ("label_ip", "listWidget_ip"),
                ("label_fin", "listWidget_fin")
            ]

            # 🔹 UI 세트 추가
            for i, (label_name, list_name) in enumerate(widget_names):
                container = QWidget()
                layout = QVBoxLayout(container)

                # ✅ QLabel
                label = QLabel(label_name)
                label.setAlignment(Qt.AlignCenter)

                # ✅ QListWidget
                list_widget = QListWidget()
                list_widget.setFixedSize(200, 300)  # ListWidget 크기
                list_widget.addItem(f"Task {i+1}")

                layout.addWidget(label)
                layout.addWidget(list_widget)
                container.setLayout(layout)

                # ✅ QGraphicsProxyWidget을 사용하여 추가
                proxy = QGraphicsProxyWidget()
                proxy.setWidget(container)
                self.scene().addItem(proxy)

                # 초기 위치 설정
                x_pos = i * 250  # 좌우로 정렬
                proxy.setPos(x_pos, 0)

                self.widgets.append(proxy)

            self.centerIndex = 1  # 초기 중앙 포커스 인덱스
            self.updatePositions()

        def updatePositions(self):
            """위젯 회전 및 크기 조정"""
            for i, proxy in enumerate(self.widgets):
                animation = QPropertyAnimation(proxy, b"pos")  # 위치 애니메이션
                animation.setDuration(500)

                if i == self.centerIndex:
                    # 중앙 위젯 (정면, 크기 증가)
                    transform = QTransform().rotate(0).scale(1.2, 1.2)  # 크기 확대
                    proxy.setTransform(transform)
                    proxy.setZValue(1)  # Z-인덱스를 높여 최상위 배치
                    animation.setEndValue(QRectF(300, 0, 250, 300))
                else:
                    # 측면 위젯 (회전, 크기 감소)
                    angle = -30 if i < self.centerIndex else 30  # 왼쪽/오른쪽 방향
                    transform = QTransform().rotate(angle).scale(0.9, 0.9)
                    proxy.setTransform(transform)
                    proxy.setZValue(0)  # 뒤로 배치
                    x_offset = -100 if i < self.centerIndex else 100
                    animation.setEndValue(QRectF(300 + x_offset, 50, 250, 300))

                animation.start()

        def keyPressEvent(self, event):
            """← → 키로 중앙 포커스 변경"""
            if event.key() == Qt.Key_Left and self.centerIndex > 0:
                self.centerIndex -= 1
            elif event.key() == Qt.Key_Right and self.centerIndex < len(self.widgets) - 1:
                self.centerIndex += 1
            self.updatePositions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec():
        sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = AnimatedListView()
    view.show()
    sys.exit(app.exec())



