import os, sys
from PySide6.QtWidgets import QApplication, QTableWidget, QAbstractItemView
from PySide6.QtGui import QDrag
from PySide6.QtCore import Qt, QMimeData, QUrl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_connector import ShotGridConnector  # ShotGrid API 연결


class DragDropHandler(QTableWidget):
    """
    QTableWidget을 상속받아 마우스 이벤트 직접 처리
    """

    def __init__(self, parent=None):
        super().__init__(parent)
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
            # 수정 예정
            """
            현재 방식은 클릭한 테이블 위젯의 테스크ID를 인식하고
            샷그리드API로 퍼블리시 경로를 불러오는 방식 (임시)
            
            해당 방법이 아니라 로더를 열 때 샷그리드 API로 정보들을 불러오고
            각 테스크 셀에 필요한 인포메이션이 정리된 데이터를 따로 저장해서
            셀을 누르면 그 셀에 해당하는 work 폴더 경로가 연결되게 (LIB 탭일 경우에는 그 LIB폴더로)

            캐시화 (반복해서 API로 조회하는게 아니라 한번에 정보 받아온 후 따로 빼서 저장한 정보에서 조회할수 있게 최적화)
            """

            file_path = file.get('path')
            file_paths.append(file_path)

        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(path) for path in file_paths]
        mime_data.setUrls(urls)  # OS에서 Drag & Drop 인식하도록 설정

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)  # 운영체제에서 Drag & Drop 인식하도록 설정