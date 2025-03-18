from PySide6.QtWidgets import QMainWindow, QApplication, QCheckBox, QGroupBox, QVBoxLayout,QGridLayout
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QLabel, QFileDialog, QLineEdit, QPushButton, QWidget,QGraphicsOpacityEffect
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QLineEdit,QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,QPropertyAnimation,QPoint,QEasingCurve
from shotgun_api3 import Shotgun
from PySide6.QtGui import QFont, QColor, QBrush, QIcon, QPixmap,QFontDatabase, QFont
from PySide6.QtCore import Qt, QTimer,QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
import sys, os, time, math




publish_path = os.path.dirname(__file__)
viper_path = os.path.join(publish_path, '..')

print (publish_path)
print (viper_path)



# # 샷그리드 연동
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()
# 로더
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loader')))
from MayaLoader import MayaLoader
from NukeLoader import NukeLoader

class LoadingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # self.setup_ui()

       
        


        self.load_ui() # qt
        self.label_back = self.ui.findChild(QLineEdit, "label_back")
        self.label_2 = self.ui.findChild(QLabel, "label_2")
        self.label_light = self.ui.findChild(QLabel, "label_light")
        self.label_logo = self.ui.findChild(QLabel, "label_logo")
        self.label_text = self.ui.findChild(QLabel, "label_text")
        self.label_text = self.ui.findChild(QLabel, "label_text")
        # ✅ 디버깅 메시지: QLabel이 제대로 로드되었는지 확인
        if self.label_text:
            print("✅ label_text 위젯 로드 성공!")
            self.label_text.setText("Click to Start!")  # ✅ 기본 텍스트 설정
            self.label_text.setAlignment(Qt.AlignCenter)  # ✅ 중앙 정렬
            self.label_text.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            self.label_text.show()
        else:
            print(" label_text 위젯을 찾을 수 없음!")

        # publish2.ui 사이즈 조절
        self.setGeometry(100, 100, 1200, 800)
        self.resize(391, 381)

        self.setWindowFlags(Qt.FramelessWindowHint)  #  타이틀바 제거
        self.setAttribute(Qt.WA_TranslucentBackground)  # 배경 투명 설정
        self.dragPos = None  # 창 이동을 위한 변수

        self.animate_logo_opacity()
        self.create_bouncing_dots()
        
        self.setup_text_rotation()  # 문장 변경 기능 추가
        self.animate_logo_opacity()  # 로고 애니메이션 실행

    def mousePressEvent(self, event):
            """ 마우스를 클릭했을 때 창의 현재 위치 저장 """
            if event.button() == Qt.LeftButton:
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

    def mouseMoveEvent(self, event):
            """ 마우스를 드래그하면 창 이동 """
            if event.buttons() == Qt.LeftButton and self.dragPos:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

    def mouseReleaseEvent(self, event):
            """ 마우스를 떼면 위치 초기화 """
            self.dragPos = None

      

    def setup_text_rotation(self):
        """ 클릭할 때마다 label_text의 문장이 변경되도록 설정 """
        self.texts = [
            "Welcome to Viper!",
            "Loading... Please wait",
            "Initializing system...",
            "Almost ready...",
            "Enjoy your work!"
        ]
        self.current_text_index = 0  # 현재 문장 인덱스
        
        
        print("텍스트 변경 기능 설정 완료")

    def mousePressEvent(self, event):
        """ 화면을 클릭하면 label_text의 문장을 변경 """
        if event.button() == Qt.LeftButton:  # 마우스 왼쪽 버튼 클릭 시 동작
            if self.label_text:
                print(f"텍스트 변경: {self.texts[self.current_text_index]}")  # 변경 확인
                self.label_text.setText(self.texts[self.current_text_index])
                self.current_text_index = (self.current_text_index + 1) % len(self.texts)  # 리스트 순환
                self.label_text.adjustSize()  # 크기 자동 조정 (텍스트가 잘리는 경우 방지)

    def animate_logo_opacity(self):
        """ abel_logo 오퍼시티 애니메이션 (30 → 70 → 10 반복) """
        
        # 오퍼시티 효과 추가
        opacity_effect = QGraphicsOpacityEffect(self.ui.label_light)
        self.ui.label_light.setGraphicsEffect(opacity_effect)

        # 오퍼시티 애니메이션 생성
        self.logo_animation = QSequentialAnimationGroup(self)

        # 30 → 70
        fade_in = QPropertyAnimation(opacity_effect, b"opacity")
        fade_in.setDuration(500)  # 0.5초 동안
        fade_in.setStartValue(0.3)
        fade_in.setEndValue(0.8)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)

        # 70 → 10
        fade_out = QPropertyAnimation(opacity_effect, b"opacity")
        fade_out.setDuration(500)  # 0.5초 동안
        fade_out.setStartValue(0.7)
        fade_out.setEndValue(0.1)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)

        # 10 → 30
        fade_back = QPropertyAnimation(opacity_effect, b"opacity")
        fade_back.setDuration(500)  # 0.5초 동안
        fade_back.setStartValue(0.1)
        fade_back.setEndValue(0.3)
        fade_back.setEasingCurve(QEasingCurve.InOutQuad)

        # 애니메이션 그룹에 추가
        self.logo_animation.addAnimation(fade_in)
        self.logo_animation.addAnimation(fade_out)
        self.logo_animation.addAnimation(fade_back)

        # 무한 반복
        self.logo_animation.setLoopCount(-1)
        self.logo_animation.start()


    def create_bouncing_dots(self):
        """ label_central 아래에 원이 튀어오르는 애니메이션 생성 """
        print("점프 애니메이션 원 생성 시작!")

        self.dots = []  # 원 리스트
        self.dot_animations = []  # 애니메이션 리스트

        dot_count = 5  # 원 개수
        dot_size = 3  # 원 크기
        spacing = 20  # 원 간격

        # 기준이 되는 중앙 라벨 가져오기
        label_2 = self.ui.label_2
        central_x = label_2.x()
        central_y = label_2.y() + label_2.height() + 20  # label_central 바로 아래 배치

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
            animation.setLoopCount(-1)  # 무한 반복
            self.dot_animations.append(animation)

        self.start_bouncing_animation()

    def start_bouncing_animation(self):
        """ 점프 애니메이션 실행 (순차적으로 시작) """
        delay = 300  # 개별 점의 딜레이 시간

        for index, animation in enumerate(self.dot_animations):
            QTimer.singleShot(index * delay, animation.start)  # 순차적으로 실행





    def load_ui(self):

            ui_file_path = os.path.join( publish_path ,"loading2.ui")

            ui_file = QFile(ui_file_path)
            loader = QUiLoader()
            self.ui = loader.load(ui_file)
            self.setCentralWidget(self.ui)
            self.ui.show()

     
# 예외 발생 시 종료 코드 반환
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        ex = LoadingUI()
        ex.show()
        sys.exit(app.exec())  
    except Exception as e:
        print(f"오류 발생: {e}")