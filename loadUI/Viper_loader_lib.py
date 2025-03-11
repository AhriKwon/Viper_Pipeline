from PySide6.QtWidgets import (
    QTableWidget, QWidget, QVBoxLayout, QLabel, QCheckBox,
    QTableWidgetItem
    )
from PySide6.QtCore import(
    Qt, 
)
from PySide6.QtGui import QPixmap
import os

#=============================Lib탭 테이블 위젯 생성====================================


class LibraryTab:
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
        self.table_widget.setColumnCount(3)
        self.table_widget.setColumnWidth(0, 200)  # 폴더 이름 너비
        self.table_widget.setRowCount(0)  # 초기 행 개수 0
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 불가
        self.table_widget.setShowGrid(False)  # 그리드 없애기
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

        # 썸네일 QLabel (기본값 제공)
        label_thumbnail = QLabel()
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
        else:
            pixmap = QPixmap(80, 80)  # 기본 썸네일 생성
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
        self.table_widget.setCellWidget(row, col, cell_widget)
        self.table_widget.setColumnWidth(col, 120)  # 컬럼 너비 설정
        self.table_widget.setRowHeight(row, 120)  # 행 높이 설정

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