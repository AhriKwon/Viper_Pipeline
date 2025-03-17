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

<<<<<<< HEAD
import sys, os, time, subprocess, re
=======
import sys, os, time, subprocess
from typing import TypedDict
>>>>>>> b655724dad0294c57906c021de5962808dfd1513

publish_path = os.path.dirname(__file__)
viper_path = os.path.join(publish_path, '..')

# 샷그리드 API
sys.path.append(os.path.abspath(os.path.join(viper_path, 'shotgridAPI')))
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()

# UI 서포터
sys.path.append(os.path.abspath(os.path.join(viper_path, 'loadUI')))
import UI_support

class ScreenCapture(QWidget):
    """
    드래그를 통한 영역 지정으로 스크린샷을 실행
    """
    def __init__(self, parent=None):
        super().__init__()
        self.parent_ui = parent  # 부모 UI 저장
        self.start_pos = None
        self.end_pos = None

        QApplication.setOverrideCursor(Qt.CrossCursor) # 커서 오버라이드
        self.setWindowFlag(Qt.FramelessWindowHint) # 제목표시줄 삭제
        self.setWindowOpacity(0.3) # 윈도우 투명도 0.3
        self.setAttribute(Qt.WA_TranslucentBackground) # 투명도 사용
        self.showFullScreen() # 풀스크린 위젯

    def mousePressEvent(self, event):
        """
        마우스를 눌렀을때 발생하는 이벤트
        """
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos
            self.update()

    def mouseMoveEvent(self, event):
        """
        마우스를 움직일때 발생하는 이벤트 
        """
        if self.start_pos:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        마우스 왼쪽 버튼을 땟을때 발생하는 이벤트
        """
        if event.button() == Qt.LeftButton:
            self.end_pos = event.pos()
            self.capture_screen()
            QApplication.restoreOverrideCursor()
            self.start_pos = None
            self.end_pos = None
            self.close()

            # 부모 UI 다시 표시
            if self.parent_ui:
                self.parent_ui.show()

    def paintEvent(self, event):
        """
        마우스가 드래그되는 곳에 사각형 그려주는 페인트 메서드
        """
        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos)
            painter = QPainter(self)
            painter.setPen(Qt.white)
            painter.drawRect(rect)

    def capture_screen(self):
        """
        실제로 화면을 캡쳐하는 메서드
        """
        if self.start_pos and self.end_pos:
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y()) # X, Y는 드래그된 마우스 포인터의 좌상단 좌표
            w = abs(self.start_pos.x() - self.end_pos.x()) # 드래그 시작점과 끝점의 X 좌표간의 차이
            h = abs(self.start_pos.y() - self.end_pos.y()) # W, H는 드래그된 마우스 포인터의 가로와 세로 길이
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, x, y, w, h)


            save_dir = "/nas/show/Viper"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            save_path = os.path.join(save_dir, "capture_001.png")
            print ("save to : ", save_path)
            screenshot.save(save_path, "png", quality=100)

            # 썸네일 업데이트
            if self.parent_ui:
                self.parent_ui.update_thumbnail(save_path)

<<<<<<< HEAD
=======
class PublishedFileData(TypedDict):
    file_name: str
    file_path: str
    description: str
    thumbnail: str
>>>>>>> b655724dad0294c57906c021de5962808dfd1513

class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_ui()
        self.set_checkbox()
        self.setup_thumbnail_capture()
        self.setup_publish_info()

<<<<<<< HEAD
        # publish2.ui 사이즈 조절
        self.setGeometry(100, 100, 1200, 800)
        self.resize(850, 750)

        # # publish 버튼을 누르면 퍼블리쉬되도록 연동
        # self.ui.pushButton_publish.clicked.connect(self.run_publish)

    def start_capture_mode(self):
       self.hide()
       self.overlay = ScreenCapture(self)
       self.overlay.show()

    def load_ui(self):

        ui_file_path = os.path.join(publish_path ,"newpub.ui")

        ui_file = QFile(ui_file_path)
        if not ui_file.exists():
            print(f"⚠️ UI 파일을 찾을 수 없습니다: {ui_file_path}")
            return
        loader = QUiLoader()
        self.ui = loader.load(ui_file)

        if self.ui:
            self.setCentralWidget(self.ui)
            self.show()
            print("UI 로드 성공: UI가 정상적으로 표시됩니다.")
        else:
            print("⚠️ UI 로드 실패: QUiLoader가 UI 파일을 로드하지 못했습니다.")
=======
        # publish 버튼을 누르면 퍼블리쉬되도록 연동
        self.ui.pushButton_publish.clicked.connect(self.run_publish)
>>>>>>> b655724dad0294c57906c021de5962808dfd1513

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
        
        # 마야에서만 체크박스를 보이고, 누크에서는 숨김
        if self.is_maya():
            self.ui.groupBox_checkbox.setVisible(True)
        else:
            self.ui.groupBox_checkbox.setVisible(False)

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
            self.start_capture_mode()
            return True
        return super().eventFilter(obj, event)

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


     #===========================================================================================
     #--------------------------------------- 퍼블리시 실행 ------------------------------------------

    def run_publish(self):
        """
        현재 실행 중인 파일을 분석하고, Maya 또는 Nuke 퍼블리시 실행
        """
        file_path = self.get_current_file_path()  # 실행 중인 파일 경로 가져오기

        if not file_path:
            UI_support.popup.show_message("error", "오류", "현재 실행 중인 파일이 없습니다.")
            return
        
        # file_data 자동 생성
        file_data = self.generate_file_data(file_path)
        if not file_data:
            return  # 오류 발생 시 중단
            
        publish_result = None  # 퍼블리시 결과 저장 변수
        version_path = None  # DB 및 ShotGrid 업데이트에 사용될 버전 경로

        # 파일 확장자로 툴 판별
        if file_path.endswith((".ma", ".mb")):
            # Maya Publisher 실행
            sys.path.append(os.path.abspath(os.path.join(viper_path, 'publisher')))
            from MayaPublisher import MayaPublisher

            # MayaPublisher 인스턴스 생성 및 실행
            maya_pub = MayaPublisher(file_data)
            publish_result = maya_pub.publish()

            # MayaPublisher에서 버전 경로 가져오기
            version_path = f"{maya_pub.prod_path}{maya_pub.out_name}" # 퍼블리시된 최종 경로

        elif file_path.endswith(".nk", ".nknc"):
            sys.path.append(os.path.abspath(os.path.join(viper_path, 'publisher')))
            from NukePublisher import NukePublisher

            # NukePublisher 실행
            nuke_pub = NukePublisher(file_path)
            publish_result = nuke_pub.publish()

        else:
            UI_support.popup.show_message("error", "오류", "지원되지 않는 파일 형식입니다.")
            return

        # 퍼블리시 성공 여부 확인
        if publish_result:
            self.update_database_and_shotgrid(version_path, publish_result)
        else:
            UI_support.popup.show_message("error", "오류", "퍼블리시 실패")
        
    def get_current_file_path(self):
        """
        Maya 또는 Nuke에서 현재 열려있는 파일 경로를 가져옴
        """
        if self.is_maya():
            return cmds.file(q=True, sn=True)  # Maya 현재 파일 경로
        elif self.is_nuke():
            return nuke.root().name()  # Nuke 현재 파일 경로
        else:
            return None
    
    def is_maya(self):
        try:
            import maya.cmds as cmds
            return True
        except ImportError:
            return False

    def is_nuke(self):
        try:
            import nuke
            return True
        except ImportError:
            return False
    
<<<<<<< HEAD
    def generate_file_data(self, file_path):
        """
        주어진 파일 경로(file_path)를 기반으로 퍼블리시 데이터를 자동으로 생성.
        """
        # 파일에서 Task ID 가져오기
        task_id = manager.get_task_id_from_file(file_path)
        if not task_id:
            UI_support.popup.show_message("error", "오류", "파일에서 Task ID를 찾을 수 없습니다.")
            return None
        
        # 샷그리드에서 Task 정보 가져오기
        task_info = manager.get_task_by_id(task_id)
        if not task_info:
            UI_support.popup.show_message("error", "오류", "Task 정보를 가져올 수 없습니다.")
            return None

        # 프로젝트 정보 가져오기
        project = task_info["project"]["name"]
        entity_type = task_info["entity"]["type"]
        entity_name = task_info["entity"]["name"]
        task_type = task_info["content"]

        # 체크박스 옵션 가져오기 (Maya 체크박스 상태 반영)
        options = self.get_selected_options()

        # Asset 또는 Shot 정보 분기 처리
        asset_type, seq, shot = None, None, None
        if entity_type == "Asset":
            asset_type = task_info["entity"].get("sg_asset_type", "Unknown")
        elif entity_type == "Shot":
            seq = task_info["entity"].get("sg_sequence", {}).get("name", "Unknown")
            shot = entity_name

        # 현재 파일 버전 판별
        version = self.extract_version_from_filename(file_path)

        # 최종 퍼블리시 데이터 생성
        file_data = {
            "project": project,
            "entity_type": entity_type,
            "task_type": task_type.rsplit('_')[1],
            "options": options,
            "asset_type": asset_type,
            "name": entity_name.rsplit('_')[0],
            "seq": seq,
            "shot": shot,
            "version": version
        }

        print(f"생성된 file_data: {file_data}")
        return file_data
    
    def get_selected_options(self):
        """
        UI에서 체크된 옵션을 리스트로 반환
        """
        selected_options = []
        if hasattr(self, "checkboxes"):
            for checkbox in self.checkboxes:
                if checkbox.isChecked():
                    selected_options.append(checkbox.text())
        return selected_options
    
    def extract_version_from_filename(self, file_path):
        """
        파일 이름에서 버전 정보를 추출 (예: _v001, _v02 -> 1, 2)
        """
        filename = os.path.basename(file_path)
        match = re.search(r'_v(\d+)', filename)
        if match:
            return int(match.group(1))  # 정수 변환 후 반환
        return 1  # 기본 버전 값

    def update_database_and_shotgrid(self, version_path, publish_result):
=======
    def update_database_and_shotgrid(self, version_path, data: PublishedFileData):
>>>>>>> b655724dad0294c57906c021de5962808dfd1513
        """
        퍼블리시 성공 후 DB와 ShotGrid 업데이트
        """
        task_id = manager.get_task_id_from_file(data["path"])

        if not task_id:
            UI_support.popup.show_message("error", "오류", "파일에서 Task ID를 찾을 수 없습니다.")
            return
        
        manager.publish(task_id, version_path, data)


    #===========================================================================================
    #------------------------------------------ 로드 --------------------------------------------



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PublishUI()
    w.ui.show()
    sys.exit(app.exec())