from PySide6.QtWidgets import (
    QTableWidget, QWidget, QVBoxLayout, QLabel, QCheckBox,
    QTableWidgetItem,QHeaderView, QSizePolicy, QHBoxLayout, QApplication
    )
from PySide6.QtCore import(
    Qt, QMimeData, QUrl
)
from PySide6.QtGui import QPixmap, QDrag
import os, sys


class LibraryTab:
    def __init__(self, ui):
        self.ui = ui
        self.table_widget = QTableWidget()  # 테이블 위젯 생성
        self.setup_table()
        self.setup_connections()

        self.setDragEnabled(True)  # 드래그 활성화
        self.setFocusPolicy(Qt.ClickFocus)  # 클릭으로 포커스 받을 수 있도록 설정

        self.selected_pathes = []  # 선택된 Task ID 저장
        self.start_pos = None  # 마우스 클릭 시작 위치 저장

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
        self.table_widget.setColumnCount(3)
        self.table_widget.setRowCount(0)  # 초기 행 개수 0
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 불가
        self.table_widget.setShowGrid(False)  # 그리드 없애기

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 

        # 스크롤바 숨기기
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 테이블 위젯의 헤더 숨기기
        self.table_widget.horizontalHeader().setVisible(False)  # 가로 헤더 숨기기
        self.table_widget.verticalHeader().setVisible(False)  # 세로 헤더 숨기기

        # tabWidget_lib 내부에 레이아웃이 있는지 확인 후 추가
        if self.ui.tabWidget_lib.layout() is None:
            layout = QVBoxLayout()
            layout.setContentsMargins(5, 30, 5, 5)  # 왼쪽, 위쪽, 오른쪽, 아래쪽 여백 설정
        
        # 테이블 위젯 추가
        layout.addWidget(self.table_widget)

        # 현재 위젯에 레이아웃 설정
        self.ui.tabWidget_lib.setLayout(layout)

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
        self.table_widget.setColumnCount(3)  # 3개의 컬럼 설정

        if not folder_path or not os.path.exists(folder_path):
            return  # 폴더가 없으면 종료

        row = 0  # 행 인덱스 초기화
        col = 0  # 열 인덱스 초기화

        # 폴더 내 디렉토리 검색
        for folder in os.listdir(folder_path):
            folder_full_path = os.path.join(folder_path, folder)
            if os.path.isdir(folder_full_path):  # 폴더만 추가
                self.add_table_item(folder, row, col)

                col += 1  # 다음 열로 이동
                if col >= 3:  # 3개의 열이 채워지면 새로운 행으로 이동
                    col = 0
                    row += 1

    def add_table_item(self, folder_name, row, col, thumbnail_path="/nas/show/Viper/lib/thumb.png"):
        """
        테이블 위젯에 폴더 아이템을 추가 (썸네일, 폴더 이름, 북마크 체크박스 포함)
        """
        # 행이 부족하면 추가
        if row >= self.table_widget.rowCount():
            self.table_widget.insertRow(row)

        # 셀에 들어갈 위젯 생성
        cell_widget = QWidget()
        layout = QVBoxLayout()
        H_layout = QHBoxLayout()

        # 썸네일 QLabel (기본값 제공)
        label_thumbnail = QLabel()
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
        else:
            pixmap = QPixmap(200, 150)  # 기본 썸네일 생성
         
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
        H_layout.addWidget(label_name)
        H_layout.addWidget(bookmark_checkbox)
        layout.addLayout(H_layout)
        layout.setAlignment(Qt.AlignCenter)  # 모든 요소 중앙 정렬
        cell_widget.setLayout(layout)

        # 테이블에 위젯 추가
        self.table_widget.setCellWidget(row, col, cell_widget)
        self.table_widget.setColumnWidth(col, 200)  # 컬럼 너비 설정
        self.table_widget.setRowHeight(row, 150)  # 행 높이 설정

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
    
    def mousePressEvent(self, event):
        """
        마우스 클릭 시 선택된 셀의의 파일 경로 가져오기
        """
        super().mousePressEvent(event)  # 기본 선택 로직 먼저 실행

        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()  # 클릭한 위치 저장 (드래그 판별용)
            selected_items = self.selectedItems()

            # 선택한 아이템이 없을 경우
            if not selected_items:
                return
            
            # 선택된 파일 경로 가져오기
            self.selected_pathes = [
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

            file = manager.get_works_for_task(task_id)[0]

            file_path = file.get('path')
            file_paths.append(file_path)

        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(path) for path in file_paths]
        mime_data.setUrls(urls)  # OS에서 Drag & Drop 인식하도록 설정

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)  # 운영체제에서 Drag & Drop 인식하도록 설정