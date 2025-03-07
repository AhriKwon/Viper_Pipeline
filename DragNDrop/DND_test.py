import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtGui import QPixmap, QIcon, QDrag
from PySide6.QtCore import Qt, QMimeData, QUrl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_connector import ShotGridConnector  # ShotGrid API 연결


class TaskTableWidget(QTableWidget):
    """
    QTableWidget을 상속받아 마우스 이벤트 직접 처리
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)  # ID, 썸네일
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 행 단위 선택
        self.setDragEnabled(True)  # 드래그 활성화
        self.setFocusPolicy(Qt.ClickFocus)  # 클릭으로 포커스 받을 수 있도록 설정

        self.selected_task_ids = []  # 선택된 Task ID 저장
        self.start_pos = None  # 마우스 클릭 시작 위치 저장

    def mousePressEvent(self, event):
        """
        마우스 클릭 시 선택된 Task의 파일 경로 가져오기
        """
        super().mousePressEvent(event)  # 기본 선택 로직 먼저 실행

        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()  # 클릭한 위치 저장 (드래그 판별용)
            selected_items = self.selectedItems()

            # 선택한 아이템이 없을 경우
            if not selected_items:
                return
            
            # 선택된 Task ID 가져오기
            self.selected_task_ids = [
                int(self.item(row, 0).text()) 
                for row in range(self.rowCount()) 
                if self.item(row, 0).isSelected()
            ]

    def mouseMoveEvent(self, event):
        """
        마우스 드래그가 실행 될 경우 이벤트가 발생할 수 있도록 함
        """
        if not self.start_pos:
            return

        # 거리 계산
        distance = (event.pos() - self.start_pos).manhattanLength()

        # 처음 위치에서 달라질 경우 -> 마우스 드래그가 발생할 경우 판별
        if event.buttons() == Qt.LeftButton and distance > QApplication.startDragDistance():
            self.startDrag()
        super().mouseMoveEvent(event)

    def startDrag(self):
        """
        파일 경로를 MIME 데이터로 설정하여 OS Drag & Drop 실행
        """
        if not self.selected_task_ids:
            return
        
        file_paths = []
        for task_id in self.selected_task_ids:
            file = ShotGridConnector.get_publishes_for_task(task_id)[0]
            file_path = file.get('path')
            file_paths.append(file_path)

        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(path) for path in file_paths]
        mime_data.setUrls(urls)  # OS에서 Drag & Drop 인식하도록 설정

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)  # 운영체제에서 Drag & Drop 인식하도록 설정


class LoaderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShotGrid Loader")
        self.setGeometry(100, 100, 800, 400)

        # TaskTableWidget 인스턴스 생성
        self.table_widget = TaskTableWidget(self)
        self.table_widget.setGeometry(10, 10, 780, 380)

        print("✅ UI 정상적으로 실행됨")  # ✅ UI 실행 확인 로그

        # ShotGrid에서 Task 정보 가져오기
        self.load_tasks()

    def load_tasks(self):
        """ShotGrid에서 Task 목록 불러와 테이블 위젯에 추가"""
        user_id = 121  # 현재 로그인한 사용자 ID (예제)
        print("🔍 ShotGrid에서 Task 불러오기...")  # ✅ ShotGrid API 실행 로그
        tasks = ShotGridConnector.get_user_tasks(user_id)

        print(f"✅ 불러온 Task 목록: {tasks}")  # ✅ Task 데이터 확인 로그

        for task in tasks:
            self.add_task(task["id"], task.get("image", None))  # 썸네일이 없으면 None 처리

    def add_task(self, task_id, thumbnail_url):
        """Task 정보를 테이블에 추가"""
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)

        # Task ID
        self.table_widget.setItem(row, 0, QTableWidgetItem(str(task_id)))

        # 썸네일 이미지
        if thumbnail_url:
            pixmap = QPixmap(thumbnail_url).scaled(50, 50, Qt.KeepAspectRatio)
            icon = QIcon(pixmap)
            item = QTableWidgetItem()
            item.setIcon(icon)
            self.table_widget.setItem(row, 1, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoaderUI()
    window.show()
    sys.exit(app.exec_())
