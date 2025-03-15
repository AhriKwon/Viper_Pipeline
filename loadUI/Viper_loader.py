from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QGraphicsOpacityEffect, QGridLayout,QTableWidget, QTableWidgetItem, QCheckBox,QGraphicsOpacityEffect,QGraphicsBlurEffect,
    QLabel
    )
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile, Qt, QPropertyAnimation, QRect, QTimer, QMimeData, QUrl,
    QByteArray, QDataStream, QIODevice, QTimer, QPoint,QPropertyAnimation,QEasingCurve,
    qInstallMessageHandler

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
        UI_support.center_on_screen(self)
    
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
        self.resize(734, 491)
        
        self.lineEdit_id = self.ui.findChild(QLineEdit, "lineEdit_id")
        self.label_id = self.ui.findChild(QLabel, "label_id") 
        self.pushButton_login = self.ui.findChild(QPushButton, "pushButton_login")
        self.pushButton_help = self.ui.findChild(QPushButton, "pushButton_help") 
        self.pushButton_login.clicked.connect(self.attempt_login)
        self.label_background = self.ui.findChild(QLabel, "label_background")

        image_path = f"{current_directory}/forui/login.png"  # 배경 이미지 경로 확인
        self.label_background.setPixmap(QPixmap(image_path))
        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        image_path_2 = f"{current_directory}/forui/Group 3995.png"  # 배경 이미지 경로 확인
        self.label_id.setPixmap(QPixmap(image_path_2))
        self.label_id.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정

        self.label_background.setScaledContents(True)  # QLabel 크기에 맞게 자동 조정
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

        def custom_message_handler(mode, context, message):
            ignored_messages = [
                "QPainter::setOpacity: Painter not active",
                "QPainter::setWorldTransform: Painter not active",
                "QPainter::restore: Unbalanced save/restore",
                "QPainter::begin: A paint device can only be painted by one painter at a time.",
                "QPainter::translate: Painter not active",
                "QPainter::begin: A paint device can only be painted by one painter at a time.",
                "QPainter::begin: Paint device returned engine == 0, type: 1",
                "QPainter::drawRects: Painter not active"
            ]
            
            # 특정 메시지 무시
            if any(ignored_msg in message for ignored_msg in ignored_messages):
                return

            # 기본 Qt 메시지 출력
            print(message)

        # Qt 메시지 핸들러 설치
        qInstallMessageHandler(custom_message_handler)
      

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
        print("로그인 창 페이드 아웃 애니메이션 시작!")  # 디버깅용 출력

        # 투명도 효과 적용
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # 투명도 애니메이션 설정 (1.0 → 0.0)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(2000)  # 2초 동안 서서히 사라짐
        self.animation.setStartValue(1.0)  # 처음에는 불투명
        self.animation.setEndValue(0.0)  # 완전히 투명

        # 애니메이션이 끝나면 `open_main_window()` 실행
        self.animation.finished.connect(self.open_main_window)
        self.animation.start()
    def open_main_window(self):
        """애니메이션 종료 후 메인 윈도우 실행"""
        print("애니메이션 완료 → 메인 윈도우 실행!")
        self.accept()  # 로그인 창 닫기
        self.main_window = LoadUI(self.lineEdit_id.text().strip())  # 메인 윈도우 실행
        self.main_window.show()



        

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
        self.setWindowFlags(Qt.FramelessWindowHint)  # 타이틀바 제거
        self.setAttribute(Qt.WA_TranslucentBackground)  # 배경 투명 설정
        
        UI_support.center_on_screen(self)

        """My Task tab"""
        self.login_and_load_tasks()

        """Lib tab"""
        self.library_manager = LibraryTab(self.ui)

        """이벤트"""
        self.ui.pushButton_open.clicked.connect(self.run_file) # open 버튼을 누르면 마야와 누크 파일이 열리도록
        self.ui.listWidget_works.itemDoubleClicked.connect(self.run_file)

        self.ui.listWidget_wtg.itemClicked.connect(self.on_item_clicked)
        self.ui.listWidget_ip.itemClicked.connect(self.on_item_clicked)
        self.ui.listWidget_fin.itemClicked.connect(self.on_item_clicked)

        # ip 리스트 위젯 상태가 바뀔 때 마다 새로고침
        self.list_widgets[1].itemChanged.connect(lambda item: self.update_list_items(self.list_widgets[1]))

        # 메인 윈도우 흐려지게 시작하고 점점 뚜렷하게
        self.blur_in_animation()

        self.create_bouncing_dots()
  

  #====================================loadui 로드=======================================
  #================================(loginui가 성공할 시에)=================================

    def load_ui(self):
        current_directory = os.path.dirname(__file__)
        ui_file_path = f"{current_directory}/lastload.ui"

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        # self.ui.show()
        

        self.list_widgets = [self.ui.listWidget_wtg, self.ui.listWidget_ip, self.ui.listWidget_fin]

        self.ui.tabWidget_info.setVisible(False)
    
    #====================================애니메이션 함수들=======================================
    #================================(loginui가 성공할 시에)=================================

    def initialize_labels(self):
        """ 애니메이션 실행 전에 모든 라벨을 초기 위치로 설정 """
        print(" 모든 라벨 초기화")

        self.label_left = self.ui.label_left  
        self.label_logo = self.ui.label_logo
        self.label_viper = self.ui.label_viper
        self.label_user = self.ui.label_user

        # 원래 위치 저장
        self.original_positions = {
            "left": QPoint(self.label_left.x(), self.label_left.y()),
            "logo": QPoint(self.label_logo.x(), self.label_logo.y()),
            "viper": QPoint(self.label_viper.x(), self.label_viper.y()),
            "user": QPoint(self.label_user.x(), self.label_user.y()),
        }

        # 화면 크기 기준으로 시작 위치 설정 (label_user는 오른쪽 바깥에서 들어옴)
        screen_width = self.width()  
        offset = 150  

        self.start_positions = {
            "left": QPoint(-self.label_left.width() - offset, self.original_positions["left"].y()),  
            "logo": QPoint(-self.label_logo.width() - offset, self.original_positions["logo"].y()),  
            "viper": QPoint(-self.label_viper.width() - offset, self.original_positions["viper"].y()),  
            "user": QPoint(screen_width + offset, self.original_positions["user"].y()),  
        }

        # 애니메이션 실행 전에 위치 강제 설정 + 숨김 처리
        for key, label in [
            ("left", self.label_left),
            ("logo", self.label_logo),
            ("viper", self.label_viper),
            ("user", self.label_user),
        ]:
            label.move(self.start_positions[key])  
            label.setVisible(False)

        print("모든 라벨 초기화 완료")

    def animate_labels(self):
        """  라벨이 위에서 아래로 떨어지는 애니메이션 실행 """
        print("라벨 애니메이션 시작!")

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
            #  QGraphicsOpacityEffect 추가 (처음에는 보이지 않도록)
            opacity_effect = QGraphicsOpacityEffect(label)
            label.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(0)  #  처음에는 완전 투명
            # 초기 위치 저장 (현재 y 좌표를 저장)
            self.initial_positions[label] = label.y()
            start_pos = QPoint(label.x(), self.initial_positions[label] - 150)  # 시작 위치 (위에서 아래로)
            end_pos = QPoint(label.x(), self.initial_positions[label])  # 최종 위치

            label.move(start_pos)  #  시작 위치로 이동 (처음에는 안 보임)
            label.setVisible(False)  # 초기에는 완전히 숨김 (중간에 깜빡이는 문제 해결)
            if label == self.ui.label_ani1:
                print("🚀 label_ani1과 label_left 애니메이션 동시 실행")
                self.start_label_left_animation() 

            # QTimer를 활용해 순차적으로 실행되도록 설정
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda lbl=label, dur=durations[index], eff=opacity_effect: self.start_label_animation(lbl, dur, eff))
            timer.start(sum(delays[:index + 1])) 

            self.label_animations.append(timer)

    def start_label_animation(self, label, duration, opacity_effect):
        """ 개별 라벨 애니메이션 실행 (더 부드럽게) """
        print(f"{label.objectName()} 애니메이션 시작! 지속시간: {duration}ms")
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
        """ 중앙 라벨이 마스크처럼 펼쳐지는 애니메이션 """
        print("중앙 라벨 확장 애니메이션 시작!")

        # 라벨 가져오기
        self.label_central = self.ui.label_central
        self.label_central.setVisible(False)   

        # 원본 크기 저장
        original_width = self.label_central.width()
        original_height = self.label_central.height()

        # 초기 마스크 설정 (중앙 1px만 보이게)
        self.mask_step = 1  # 시작 크기 (1px)
        self.max_mask_width = original_width  # 최종 마스크 크기
        self.label_central.setVisible(False)  # 처음에는 숨김

        # 0.1초 후 애니메이션 시작 (label_central이 애니메이션 시작 전 보이지 않도록)
        QTimer.singleShot(200, self._start_mask_animation)
    def _start_mask_animation(self):
        """ 마스크 애니메이션 시작 """
        self.label_central.setVisible(True)  # 이제 보이도록 설정
        self.mask_timer = QTimer(self)
        self.mask_timer.timeout.connect(self._update_mask_animation)
        self.mask_timer.start(25)  # 15ms마다 실행 (부드러운 확장 효과)

    def _update_mask_animation(self):
        """ 마스크 확장 업데이트 (부드러운 애니메이션) """
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
        """ label_left, label_logo, label_viper, label_user가 함께 이동하는 애니메이션 실행 """
        print("label_left 애니메이션 시작!")

        self.animations = []  # 애니메이션 참조 유지 리스트
        labels = [
            ("left", self.ui.label_left),
            ("logo", self.ui.label_logo),
            ("viper", self.ui.label_viper),
            ("user", self.ui.label_user)
        ]

        # 디버깅용: 현재 위치와 이동 거리 확인
        for key, label in labels:
            print(f"🔹 {key} 시작 위치: {self.start_positions[key]} -> {self.original_positions[key]}")

        for key, label in labels:
            label.setVisible(True)  # 애니메이션 시작 전 보이도록 설정

            animation = QPropertyAnimation(label, b"pos", self)
            animation.setDuration(2000)  # 2초 동안 이동
            animation.setStartValue(self.start_positions[key])  
            animation.setEndValue(self.original_positions[key])  
            animation.setEasingCurve(QEasingCurve.OutBack)  

            animation.start()
            self.animations.append(animation)  # GC 방지: 리스트에 저장

        # 애니메이션 실행 후 UI 강제 업데이트 (안 보이는 문제 해결)
        self.update()

    def create_bouncing_dots(self):
        """ label_central 아래에 원이 튀어오르는 애니메이션 생성 """
        print("🔹 점프 애니메이션 원 생성 시작!")

        self.dots = []  # 원 리스트
        self.dot_animations = []  # 애니메이션 리스트

        dot_count = 5  # 원 개수
        dot_size = 3  # 원 크기
        spacing = 20  # 원 간격

        # 🔹 기준이 되는 중앙 라벨 가져오기
        label_central = self.ui.label_central
        central_x = label_central.x()
        central_y = label_central.y() + label_central.height() + 20  # label_central 바로 아래 배치

        for i in range(dot_count):
            dot = QLabel(self)
            dot.setFixedSize(dot_size, dot_size)
            dot.move(central_x + i * spacing, central_y)
            dot.setStyleSheet("background-color: gray; border-radius: 7px;")
            dot.show()
            self.dots.append(dot)

            # 애니메이션 설정
            animation = QPropertyAnimation(dot, b"pos")
            animation.setDuration(1600)
            animation.setStartValue(QPoint(dot.x(), central_y))  # 원래 위치
            animation.setEndValue(QPoint(dot.x(), central_y - 10))  # 위로 점프
            animation.setEasingCurve(QEasingCurve.OutQuad)  # 부드럽게 점프

            # 애니메이션이 끝나면 다시 원래 위치로 돌아옴
            animation.setLoopCount(-1)  # 🔹 무한 반복
            self.dot_animations.append(animation)

        self.start_bouncing_animation()

    def start_bouncing_animation(self):
        """ 점프 애니메이션 실행 (순차적으로 시작) """
        delay = 300  # 개별 점의 딜레이 시간

        for index, animation in enumerate(self.dot_animations):
            QTimer.singleShot(index * delay, animation.start)  # 순차적으로 실행
    
    def blur_in_animation(self):
        """ 메인 윈도우가 흐릿하게 시작되었다가 점점 선명해지는 효과 """
        print("메인 윈도우 블러 애니메이션 시작!")
        
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


        self.animation.finished.connect(self.remove_login_message)

        self.animation.start()

        self.show_login_message()  # ✅ 로그인 메시지 애니메이션 시작
    
    def show_login_message(self):
        """로그인 메시지를 중앙에 표시하고 글자 간격이 벌어지는 애니메이션 실행"""
        print("로그인 메시지 애니메이션 시작!")

        text = "12345456로 로그인되셨습니다"
        self.letter_labels = []  # 개별 글자 라벨 저장
        self.letter_animations = []  # 애니메이션 리스트

        # 🔹 중앙 정렬 기준
        window_width = self.width()
        window_height = self.height()
        start_x = window_width // 2
        start_y = window_height // 2 - 20  # 🔹 중앙 위치
       
        letter_spacing = 20  # 글자 간격 (최종 간격)
        total_text_width = len(text) * letter_spacing  # 전체 텍스트의 너비 계산
        
        # 개별 글자 QLabel 생성
        for i, char in enumerate(text):
            letter_label = QLabel(char, self)
            letter_label.setStyleSheet("font-size: 10px; color: white;")
            letter_label.setGeometry(start_x, start_y, 20, 30)  # 초기 위치 (모든 글자가 한 점에 모여있음)
            letter_label.show()
            self.letter_labels.append(letter_label)

            # 🔹 글자가 점점 퍼지는 애니메이션
            final_x = start_x - ((len(text) * letter_spacing) // 2) + (i * letter_spacing)  # 중앙 정렬된 최종 위치
            animation = QPropertyAnimation(letter_label, b"pos")
            animation.setDuration(3000)  # 1초 동안 진행
            animation.setStartValue(QPoint(start_x, start_y))
            animation.setEndValue(QPoint(final_x, start_y))
            animation.setEasingCurve(QEasingCurve.OutCubic)

            self.letter_animations.append(animation)

        # 모든 애니메이션 시작
        for anim in self.letter_animations:
            anim.start()

        QTimer.singleShot(7300, self.remove_login_message)

    def fade_out_login_message(self):
        """로그인 메시지를 서서히 사라지게 만듦"""
        print("로그인 메시지 페이드아웃 시작!")

        self.fade_animations = []  # 페이드아웃 애니메이션 리스트

        for label in self.letter_labels:
            fade_animation = QPropertyAnimation(label, b"windowOpacity")
            fade_animation.setDuration(1000)  # 1초 동안 서서히 사라짐
            fade_animation.setStartValue(1.0)  # 시작은 불투명
            fade_animation.setEndValue(0.0)  # 끝은 완전 투명
            fade_animation.setEasingCurve(QEasingCurve.OutCubic)

            self.fade_animations.append(fade_animation)
            fade_animation.start()

        # 애니메이션이 끝난 후 QLabel 삭제
        QTimer.singleShot(1000, self.remove_login_message)

    def remove_login_message(self):
        """로그인 메시지 완전히 삭제"""
        print("로그인 메시지 제거")
        for label in self.letter_labels:
            label.deleteLater()
        self.letter_labels.clear()
    
    def animate_info_labels(self):
        """Task 정보 라벨들이 화면 왼쪽에서 부드럽게 등장하는 애니메이션"""
        print("Task 정보 라벨 애니메이션 시작!")

        # 사용할 라벨 리스트 (각 라벨과 대응하는 제목 라벨)
        label_pairs = [
            ("label_6", "label_filename"),
            ("label_7", "label_type"),
            ("label_8", "label_startdate"),
            ("label_9", "label_duedate")
        ]

        # 라벨 객체 저장
        self.labels = [(getattr(self.ui, lbl1), getattr(self.ui, lbl2)) for lbl1, lbl2 in label_pairs]

        print ("****" * 5000)

        # 원래 위치 저장
        self.original_positions = {
            label: QPoint(label.x(), label.y()) for pair in self.labels for label in pair
        }

        print ("ㅗㅗㅗㅗ" * 5000)

        # 시작 위치 설정 (화면 왼쪽 바깥으로 이동)
        screen_offset = -200  
        self.start_positions = {
            label: QPoint(screen_offset, label.y()) for pair in self.labels for label in pair
        }

        print ("ㅠㅠㅠㅠㅠ" * 5000)

        # 애니메이션 실행 전에 위치 강제 설정
        for pair in self.labels:
            
            for label in pair:
                print (pair, label)
                label.move(self.start_positions[label])  
                label.setVisible(True)  

        # UI 업데이트 후 100ms 뒤에 애니메이션 실행
        QTimer.singleShot(100, self._start_info_label_animation)


    def _start_info_label_animation(self):
        """Task 정보 라벨 등장 애니메이션 실행"""
        print("Task 정보 라벨 등장 애니메이션 실행!")

        self.animations = []
        delay = 0

        for pair in self.labels:
            for label in pair:
                animation = QPropertyAnimation(label, b"pos", self)
                animation.setDuration(1500)  
                print (self.start_positions[label])
                animation.setStartValue(self.start_positions[label])  
                animation.setEndValue(self.original_positions[label])  
                animation.setEasingCurve(QEasingCurve.OutBack)  

                QTimer.singleShot(delay, animation.start)  # ✅ 순차적 실행
                self.animations.append(animation)

            delay += 200  # ✅ 딜레이 추가 (순차적 등장)


#=============================로그인 후, task 목록을 가져오는 함수====================================
#=============================파일 오픈 및 My task 탭 여러 내부 기능====================================
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
        
        if not os.path.exists(thumb_path) or not os.path.isdir(thumb_path):
            return "/nas/Viper/thumb.jpg"
        
        # 지원하는 이미지 확장자
        valid_extensions = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
        
        # 해당 폴더 내 파일 목록 가져오기 (이미지 파일만 필터링)
        image_files = [f for f in os.listdir(thumb_path) if f.lower().endswith(valid_extensions)]
        
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