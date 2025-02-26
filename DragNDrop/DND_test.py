from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QIcon, QDrag
from PyQt5.QtCore import Qt, QMimeData
import sys
from shotgrid_connector import ShotGridConnector  # ShotGrid API 연결

class LoaderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShotGrid Loader")
        self.setGeometry(100, 100, 800, 400)
        
        # 테이블 위젯 생성
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(10, 10, 780, 380)
        self.table_widget.setColumnCount(2)  # ID, 썸네일
        self.table_widget.setHorizontalHeaderLabels(["Task ID", "Thumbnail"])
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # 행 단위 선택
        self.table_widget.setDragEnabled(True)  # 드래그 활성화
        self.table_widget.setAcceptDrops(False)  # 드롭 비활성화

        # ShotGrid에서 Task 정보 가져오기
        self.load_tasks()

    def load_tasks(self):
        """ShotGrid에서 Task 목록 불러와 테이블 위젯에 추가"""
        user_id = 121  # 현재 로그인한 사용자 ID (예제)
        tasks = ShotGridConnector.get_user_tasks(user_id)

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

    def startDrag(self):
        """드래그 시작"""
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        
        task_ids = [
            int(self.table_widget.item(row, 0).text()) 
            for row in range(self.table_widget.rowCount()) 
            if self.table_widget.item(row, 0).isSelected()
        ]

        # ShotGrid API를 사용하여 최신 퍼블리시 파일 경로 가져오기
        file_paths = ShotGridConnector.get_latest_published_files(task_ids)

        if file_paths:
            mime_data = QMimeData()
            mime_data.setText("\n".join(file_paths))  # 여러 파일 경로 전달 가능
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoaderUI()
    window.show()
    sys.exit(app.exec_())
