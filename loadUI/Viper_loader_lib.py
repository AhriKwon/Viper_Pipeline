from PySide6.QtWidgets import (
    QTableWidget, QWidget, QVBoxLayout, QLabel, QCheckBox,
    QTableWidgetItem,QHeaderView, QSizePolicy, QHBoxLayout, QApplication,QTabWidget
    )
from PySide6.QtCore import(
    Qt, QMimeData, QUrl,QTimer,QPoint,QPropertyAnimation,QEasingCurve
)
from PySide6.QtGui import QPixmap, QDrag
import os, sys, json, glob

import UI_support

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from shotgrid_manager import ShotGridManager
manager = ShotGridManager()

# 로더
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loader')))
from FileLoader import FileLoader
loader = FileLoader()


class LibraryTab:
    def __init__(self, ui):
        self.ui = ui
        self.table_widget = DraggableTableWidget()  # 테이블 위젯 생성
        self.setup_table()
        self.setup_connections()

        # 폴더 경로 매핑
        self.folder_paths = {
            "asset": "/nas/show/Viper/lib/asset",
            "clip": "/nas/show/Viper/lib/clip",
            "exr": "/nas/show/Viper/lib/exr",
            "rig": "/nas/show/Viper/lib/rig",
            "thumb": "/nas/show/Viper/lib/thumbs/"
        }

        self.BOOKMARK_FILE = "/home/rapa/bookmarks.json"
        self.bookmarked_items = []  # 북마크된 항목 저장
        self.bookmarked_items = self.load_bookmarks()
        self.tab_bookmark = self.ui.tabWidget_lib.widget(4)
        # self.label_filename_2 = self.ui.findChild(QLabel, "label_filename_2")
        # self.label_startdate_2 = self.ui.findChild(QLabel, "label_startdate_2")
        # self.label_filtype_2 = self.ui.findChild(QLabel, "label_filtype_2 ")
        # self.label_duedate_2 = self.ui.findChild(QLabel, "label_duedate_2 ")
        # self.tabWidget_info2 = self.ui.findChild(QTabWidget, "tabWidget_info2 ")
        
        self.load_files(1)

        # 이벤트 연결
        self.ui.pushButton_import.clicked.connect(self.import_file)
        # self.ui.pushButton_reference.clicked.connect(self.reference_file)

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
        self.ui.label_filename_2.setText(task['content'])
        self.ui.label_filename_2.setText(task['content'])
        self.ui.label_startdate_2.setText(task["start_date"])
        self.ui.label_duedate_2.setText(task["due_date"])

        file_type = self.get_filetype(file_name)
        self.ui.label_type_2.setText(file_type)  

        self.ui.tabWidget_info2.show()
        QTimer.singleShot(10, self.animate_info_labels)
        print ("show task details")

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

        # 원래 위치 저장
        self.original_positions = {
            label: QPoint(label.x(), label.y()) for pair in self.labels for label in pair
        }

        # 시작 위치 설정 (화면 왼쪽 바깥으로 이동)
        screen_offset = -200  
        self.start_positions = {
            label: QPoint(screen_offset, label.y()) for pair in self.labels for label in pair
        }

        # 애니메이션 실행 전에 위치 강제 설정
        for pair in self.labels:
            
            for label in pair:
                print (pair, label)
                label.move(self.start_positions[label])  
                label.setVisible(True)  

        # UI 업데이트 후 100ms 뒤에 애니메이션 실행
        QTimer.singleShot(100, self._start_info_label_animation)

    def _start_info_label_animation(self):
        """
        Task 정보 라벨 등장 애니메이션 실행
        """
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

                QTimer.singleShot(delay, animation.start)  # 순차적 실행
                self.animations.append(animation)

            delay += 200  # 딜레이 추가 (순차적 등장)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////

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

        self.table_widget.setStyleSheet("""QTableWidget { background: transparent; border: none; }
                                   QTableWidget::item { background: transparent; }""")

        # tabWidget_lib 내부에 레이아웃이 있는지 확인 후 추가
        if self.ui.tabWidget_lib.layout() is None:
            layout = QVBoxLayout()
            layout.setContentsMargins(5, 120, 5, 5)  # 왼쪽, 위쪽, 오른쪽, 아래쪽 여백 설정
        
        # 테이블 위젯 추가
        layout.addWidget(self.table_widget)

        # 현재 위젯에 레이아웃 설정
        self.ui.tabWidget_lib.setLayout(layout)

    def setup_connections(self):
        """
        탭 변경 시 폴더 내용 업데이트
        """
        self.ui.tabWidget_lib.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self, index):
        """
        탭 변경 시, 북마크 탭이라면 북마크된 파일만 표시
        """
        if index == 4:  # 북마크 탭이 선택되었을 때
            self.load_bookmarked_files()
        else:
            self.load_files(index)

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
        for file in os.listdir(folder_path):
            self.add_table_item(file, folder_path, row, col)

            col += 1  # 다음 열로 이동
            if col >= 3:  # 3개의 열이 채워지면 새로운 행으로 이동
                col = 0
                row += 1

    def add_table_item(self, file, folder_path, row, col):
        """
        테이블 위젯에 셀을 추가
        """
        # 행이 부족하면 추가
        if row >= self.table_widget.rowCount():
            self.table_widget.insertRow(row)

        file_path = os.path.join(folder_path, file)

        # 썸네일 폴더 경로
        thumb_folder = self.folder_paths["thumb"]
        file_name = file.rsplit('.')[0]

        # 같은 이름의 썸네일 파일 찾기 (.jpg, .png)
        thumbnail_candidates = glob.glob(os.path.join(thumb_folder, f"{file_name}.*"))

        # 기본 썸네일 경로
        thumbnail_path="/nas/Viper/thumb.jpg"

        for candidate in thumbnail_candidates:
            if candidate.lower().endswith((".jpg", ".png")):
                thumbnail_path = candidate  # 존재하는 썸네일을 사용
                break  # 가장 첫 번째로 발견된 썸네일을 사용

        # 테이블 셀 위젯 생성
        cell_widget = self.make_table_cell(file, file_path, thumbnail_path)

        # 테이블에 위젯 추가
        self.table_widget.setCellWidget(row, col, cell_widget)
        self.table_widget.setColumnWidth(col, 200)  # 컬럼 너비 설정
        self.table_widget.setRowHeight(row, 150)  # 행 높이 설정

    def load_bookmarked_files(self):
        """
        북마크된 파일들을 불러와 테이블에 표시
        """
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(3)  # 3개의 컬럼 설정

        row = 0
        col = 0

        for file_path, is_bookmarked in self.bookmarked_items.items():
            if is_bookmarked:  # 북마크된 파일만 표시
                file_name = os.path.basename(file_path)
                self.add_table_item(file_name, os.path.dirname(file_path), row, col)

                col += 1
                if col >= 3:
                    col = 0
                    row += 1

    def make_table_cell(self, file_name, file_path, thumbnail_path):
        """
        테이블 위젯 셀에 넣을 위젯 제작(썸네일, 폴더 이름, 북마크 체크박스 포함)
        """
        cell_widget = QWidget()
        layout = QVBoxLayout()

        # ✅ 썸네일 QLabel 생성
        label_thumbnail = QLabel()
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
        else:
            pixmap = QPixmap(320, 180)  # 기본 썸네일 생성

        scaled_pixmap = pixmap.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        rounded_pixmap = UI_support.round_corners_pixmap(scaled_pixmap, radius=10)

        label_thumbnail.setPixmap(rounded_pixmap)
        label_thumbnail.setAlignment(Qt.AlignCenter)
        label_thumbnail.setFixedSize(320, 180)  # ✅ 크기 고정

        # ✅ 북마크 체크박스 생성 (썸네일 위에 배치)
        bookmark_checkbox = QCheckBox(label_thumbnail)
        bookmark_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                image: url('/nas/Viper/minseo/forui/bookmark1.png');
            }
            QCheckBox::indicator:checked {
                image: url('/nas/Viper/minseo/forui/bookmark2.png');
            }
            QCheckBox {
                border: none;
                background: transparent;
            }
        """)
        bookmark_checkbox.setChecked(self.bookmarked_items.get(file_path, False))
        bookmark_checkbox.move(label_thumbnail.width() - 34, 14)  # ✅ 오른쪽 상단 배치
        bookmark_checkbox.stateChanged.connect(lambda state, f=file_path: self.update_bookmark(state, f))

        # ✅ 파일 이름 QLabel
        label_name = QLabel(file_name)
        label_name.setAlignment(Qt.AlignCenter)
        label_name.setStyleSheet("color: white;")

        # ✅ 최종 레이아웃 설정
        layout.addWidget(label_thumbnail)
        layout.addWidget(label_name)
        layout.setAlignment(Qt.AlignCenter)
        cell_widget.setLayout(layout)

        # ✅ 셀에 파일 경로 저장
        cell_widget.setProperty("file_path", file_path)

        return cell_widget

    def import_file(self):
        """
        파일 Import
        """
        selected_items = self.table_widget.selectedItems()
        print(f"선택된 아이템: {selected_items}")

        if not selected_items:
            UI_support.show_message("error", "오류", "파일이 선택되지 않았습니다.")
            return

        for item in selected_items:
            row = item.row()
            work_data = self.table_widget.item(row, 0).data(Qt.UserRole)

            if not work_data:
                UI_support.show_message("error", "오류", "work 데이터를 찾을 수 없습니다.")
                continue

            work_name = work_data["file_name"]
            file_path = work_data["path"]
            print(f"파일 경로: {file_path}")

            if not file_path:
                UI_support.show_message("error", "오류", f"{work_name}의 파일 경로를 찾을 수 없습니다.")
                continue

            loader.import_file(file_path)

    def save_bookmarks(self):
        """
        북마크 정보를 JSON 파일에 저장
        """
        with open(self.BOOKMARK_FILE, "w") as file:
            json.dump(self.bookmarked_items, file, indent=4)

    def load_bookmarks(self):
        """
        JSON 파일에서 북마크 리스트 불러오기
        """
        if not os.path.exists(self.BOOKMARK_FILE):
            return {}

        with open(self.BOOKMARK_FILE, "r") as file:
            return json.load(file)

    def update_bookmark(self, state, file_path):
        """
        북마크 상태 업데이트 및 저장
        """
        if state == Qt.Checked:
            if file_path not in self.bookmarked_items:
                self.bookmarked_items.append(file_path)
        else:
            if file_path in self.bookmarked_items:
                self.bookmarked_items.remove(file_path)

        # 북마크 목록 저장
        self.save_bookmarks(self.bookmarked_items)

    def update_bookmark(self, state, file_path):
        """
        북마크 상태 업데이트 및 저장
        """
        if state == Qt.Checked:
            self.bookmarked_items[file_path] = True  # 북마크 추가
        else:
            self.bookmarked_items[file_path] = False  # 북마크 해제

        # 북마크 목록 저장
        self.save_bookmarks()

        # 북마크 탭이 활성화된 경우 즉시 갱신
        if self.ui.tabWidget_lib.currentIndex() == 4:
            self.load_bookmarked_files()


    
"""
테이블 위젯 드래그 앤 드랍 활성화
"""
class DraggableTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True) # 드래그 활성화
        self.setFocusPolicy(Qt.ClickFocus) # 클릭으로 포커스 받을 수 있도록 설정
        self.start_pos = None # 마우스 클릭 시작 위치 저장
        self.selected_items = [] # 선택된 아이템 경로 저장

    def mousePressEvent(self, event):
        """
        마우스 클릭 시 선택된 셀의 파일 경로 가져오기
        """
        super().mousePressEvent(event) # 기본 선택 로직 실행

        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos() # 클릭한 위치 저장 (드래그 판별용)
            selected_cells = self.selectedIndexes()

            if not selected_cells:
                return

            # 선택된 파일 가져오기
            self.selected_items = []
            for index in selected_cells:
                cell_widget = self.cellWidget(index.row(), index.column())
                if cell_widget:
                    file_path = cell_widget.property("file_path")
                    if file_path:
                        self.selected_items.append(file_path)

            print("마우스 클릭 - 선택된 파일:", self.selected_items)

    def mouseMoveEvent(self, event):
        """
        마우스 드래그가 실행될 경우 이벤트가 발생할 수 있도록 함
        """
        if not self.start_pos:
            return

        # 거리 계산
        distance = (event.pos() - self.start_pos).manhattanLength()

        # 처음 위치에서 달라질 경우 -> 마우스 드래그가 발생할 경우 판별
        if event.buttons() == Qt.LeftButton and distance > QApplication.startDragDistance():
            self.startDrag()
        super().mouseMoveEvent(event)
        print("마우스 움직임")

    def startDrag(self):
        """
        파일 경로를 MIME 데이터로 설정하여 OS Drag & Drop 실행
        """
        if not self.selected_items:
            return

        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(path) for path in self.selected_items]
        mime_data.setUrls(urls)  # OS에서 Drag & Drop 인식하도록 설정

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)  # 운영체제에서 Drag & Drop 인식하도록 설정

