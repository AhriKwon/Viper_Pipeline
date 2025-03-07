from PySide6.QtWidgets import QMainWindow, QApplication, QCheckBox, QGroupBox, QVBoxLayout
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QLabel, QFileDialog, QLineEdit, QPushButton, QWidget
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QLineEdit,QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from shotgun_api3 import Shotgun
from PySide6.QtGui import QFont, QColor, QBrush, QIcon, QPixmap,QFontDatabase, QFont
from PySide6.QtCore import Qt
import sys, os, time




publish_path = os.path.dirname(__file__)
viper_path = os.path.join(publish_path, '..')

print (publish_path)
print (viper_path)



# # 샷그리드 연동
sys.path.append(os.path.abspath(os.path.join(viper_path, 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_connector import ShotGridConnector

# 마야 publisher 연동
# sys.path.append(os.path.abspath(os.path.join(viper_path, 'Publisher')))
# from MayaPublisher import MayaPublisher
# from Generating import FilePath
# from publisher.convert_to_mov import FileConverter

ICON_PATHS = {
    "maya": "/nas/Viper/minseo/icon/maya.png",
    "nuke": "/nas/Viper/minseo/icon/nuke.png",
    "houdini": "/nas/Viper/minseo/icon/hou.png"
}

class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()


        self.load_ui() # qt
        self.connect_signals() # 파일 정보 열람
        self.set_checkbox() # 체크박스 실행 (마야파일일때)
        self.populate_file_list()  # 파일 목록을 tableWidget_filelist에 추가


        # publish2.ui 사이즈 조절
        self.setGeometry(100, 100, 1200, 800)
        self.resize(850, 750)


        # #폰트 적용 
        # font_path = os.path.join(publish_path, "MYRIADPRO-SEMIBOLD.OTF")  # 확장자 추가

        # if os.path.exists(font_path):  # 파일 존재 여부 확인
        #     font_id = QFontDatabase.addApplicationFont(font_path)

        #     if font_id != -1:
        #         font_families = QFontDatabase.applicationFontFamilies(font_id)
        #         if font_families:
        #             custom_font = QFont(font_families[0], 12)

        #             # 🔹 스타일시트 적용
        #             self.ui.setStyleSheet(f"* {{ font-family: '{font_families[0]}'; font-size: 12pt; }}")

        #             print(f"폰트 스타일시트 적용 성공: {font_families[0]}")
        #         else:
        #             print("폰트 로드 성공했지만 적용할 수 없습니다.")





        # publish 버튼을 누르면 퍼블리쉬되도록 연동
        self.publish_button = self.ui.findChild(QPushButton, "publish_button")
        if self.publish_button:
            self.publish_button.clicked.connect(self.publish_selected_file)

        # 파일 : 로고, 이름 , 메모 
        self.lineEdit_memo = self.ui.findChild(QLineEdit, "lineEdit_memo")
        self.label_name = self.ui.findChild(QLabel, "label_filename")
        self.label_logo = self.ui.findChild(QLabel, "label_logo")


        # 파일별 설정 별도 저장하기 
        self.file_checkbox_states = {}
        self.current_file = None
        self.memo_states = {}
        self.current_file = None


 #-------------------------<TEAM: publish버튼을 누르면 퍼블리셔와 연동되도록 하는 함수> ------------------------------------

    def publish_selected_file(self):

        selected_items = self.tableWidget_filelist.selectedItems()
        selected_item = selected_items[0]
        file_name = selected_item.text()
        task_type = self.lineEdit_taskname.text()

        # Task 유형을 판별하여 적절한 퍼블리시 실행
        if task_type in ["MDL", "RIG", "TXT"]:
            publisher = MayaPublisher(task_type, asset_name=file_name)
        elif task_type in ["MM", "LAY", "ANM"]:
            publisher = MayaPublisher(task_type, seq="SEQ_NAME", shot=file_name)
        else:
            return

        publisher.publish() 

    #========================================================================================================
    #-------------------------  0. 설정: 파일별로 존재하는 체크박스와 메모  ------------------------------------

    def set_checkbox(self):

        # findchild : qtdesigner내의 해당 위젯 찾기
        self.groupBox_checkbox = self.ui.findChild(QGroupBox, "groupBox_checkbox")

        groupBoxLayout = self.groupBox_checkbox.layout()
        if groupBoxLayout is None:
            groupBoxLayout = QVBoxLayout()
            self.groupBox_checkbox.setLayout(groupBoxLayout)

        # 체크박스 옵션 설정 (마야파일일때만 실행)
        options = ["shader", "wireframe on shader", "textured", "wireframe on textured"]
        self.checkboxes = []

        # 체크 상태 유지
        for option in options:
            checkbox = QCheckBox(option)
            checkbox.stateChanged.connect(self.save_checkbox_state)
            groupBoxLayout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # 평소엔 보이지 않도록
        self.groupBox_checkbox.setVisible(False)


    def add_memo(self):
        if self.lineEdit_memo:
            text = self.lineEdit_memo.text().strip()
            if text:
                self.lineEdit_memo.addItem(text)  # 리스트에 추가
                self.lineEdit_memo.clear()  # 입력창 초기화

    #================================================================================================
    #-----------------------------------1-1.파일리스트 설정  ----------------------------------------------


    def connect_signals(self):


        self.tableWidget_filelist = self.ui.findChild(QTableWidget, "tableWidget_filelist")

        # tableWidget_filelist 내의 유저가 선택 행
        self.tableWidget_filelist.itemSelectionChanged.connect(self.on_file_selected)
        self.label_name = self.ui.findChild(QLabel, "label_filename")
        self.lineEdit_memo = self.ui.findChild(QLineEdit, "lineEdit_memo")
        

    #---------------------------------1-2.파일리스트 --------- ---------------------------------------

    def populate_file_list(self):

        # task 경로 # 바꿔야 함
        directory_path = "/nas/show/Viper/assets/Character/teapot/LKD/pub/lookfile"

        self.tableWidget_filelist.clear()
        self.tableWidget_filelist.setColumnCount(5)
        self.tableWidget_filelist.verticalHeader().setVisible(False)  # 행 번호 제거
        self.tableWidget_filelist.horizontalHeader().setVisible(False)
        self.tableWidget_filelist.setSelectionBehavior(QTableWidget.SelectRows)  # 행 단위 선택
        self.tableWidget_filelist.verticalHeader().setDefaultSectionSize(50)  # 행 간격 늘리기
        self.tableWidget_filelist.horizontalHeader().setStretchLastSection(True)  # 마지막 열 자동 확장
        self.tableWidget_filelist.horizontalHeader().setSectionResizeMode(self.tableWidget_filelist.horizontalHeader().ResizeToContents)  # 전체 테이블 폭에 맞춤

        """
        # os.listdir : directory_path에 있는 모든 파일 의 이름을 리스트로 받아온다
        # sorted: 오름차순 정렬
        # os.path.join : 경로와 파일이름을 결합하여 전체 경로를 만든다 # 이게 왜 필요하지?
        """

        for file_name in sorted(os.listdir(directory_path)):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path): # 파일일 경우에만 불러온다 (폴더는 불러오지 않음)
                row_position = self.tableWidget_filelist.rowCount()
                self.tableWidget_filelist.insertRow(row_position)

                # 1-2 0행: 파일리스트/ 체크
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(lambda state, row=row_position: self.select_entire_row(row, state))
                self.tableWidget_filelist.setCellWidget(row_position, 0, checkbox)

                # 1-2 1행 : 파일리스트/ 아이콘 
                icon_path = self.get_icon_for_file(file_name)
                icon_item = QTableWidgetItem()
                if icon_path:
                    icon_item.setIcon(QIcon(icon_path))

                self.tableWidget_filelist.setItem(row_position, 1, icon_item) 

                # 1-2 3행 : 파일리스트 / 파일이름
                self.tableWidget_filelist.setItem(row_position, 3, QTableWidgetItem(file_name))

                # 1-2 4,5행 :파일리스트/파일크기,수정시간 
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                modified_time = time.ctime(os.path.getmtime(file_path))

                mod_time_item = QTableWidgetItem(modified_time)
                mod_time_item.setFont(QFont("Arial", 9))  
                mod_time_item.setForeground(QBrush(QColor(169, 169, 169))) 
                self.tableWidget_filelist.setItem(row_position, 4, mod_time_item)
                file_size_item = QTableWidgetItem(f"{file_size:.2f} MB")
                file_size_item.setFont(QFont("Arial", 9))  
                file_size_item.setForeground(QBrush(QColor(169, 169, 169)))  
                self.tableWidget_filelist.setItem(row_position, 5, file_size_item)
 

    # 1-2 0행: 파일리스트/체크 # 설정 
    def select_entire_row(self, row, state):
        for col in range(1, self.tableWidget_filelist.columnCount()):  
            item = self.tableWidget_filelist.item(row, col)
            if item:
                item.setSelected(state == Qt.Checked)
    # 1-2 1행 : 파일리스트/ 아이콘  # 설정 
    def get_icon_for_file(self, file_name):
      
        if file_name.endswith((".ma", ".mb")):
            return ICON_PATHS["maya"]
        elif file_name.endswith(".nk"):
            return ICON_PATHS["nuke"]
        elif file_name.endswith(".hip"):
            return ICON_PATHS["houdini"]
        return None

    #========================================================================================================
    #-------------------------2-1 유저가 클릭한 파일만 정보 표시되도록 하기 ------------------------------------

    # 2-1 : 1. 파일리스트는 한 행으로 묶여서 선택되도록 한다.
    # 2-1 : 2. 메모/체크박스 설정은 각행마다 별개의 할당된 정보로 저장된다. 
    # 2-1 : 3. 파일이름/ 로고는 파일리스트의 각행의 정보를 그대로 받아온다. 
    def on_file_selected(self):
    
        # 2-1: 1. 유저가 선택한 모든 셀을 리스트로 받아온다. 
        selected_items = self.tableWidget_filelist.selectedItems()
        # 2-1: 1. 선택 행이 있다면 진행한다. 
        if selected_items:
            selected_item = selected_items[1]
            file_name = selected_item.text()

  
        # 2-1 : 2. <메모> 각 행에 정보가 별개로 할당되도록 이전 메모 상태 저장 
        if self.current_file:
            self.memo_states[self.current_file] = self.lineEdit_memo.text()
            self.file_checkbox_states[self.current_file] = [checkbox.isChecked() for checkbox in self.checkboxes]

        # 2-1 : 2. <메모> self.current_file 값을 새로 선택한 파일로 메모 업데이트.
        self.current_file = file_name

        # 2-1: 2.  <메모> 새로운 메모를 적을 수 있도록 한다. 
        if file_name in self.memo_states:
            self.lineEdit_memo.setText(self.memo_states[file_name])
        else:
            self.lineEdit_memo.clear()
        
        # 2-1 : 2. <체크박스> 마야파일이면 체크박스가 나타노도록 설정
        is_maya_file = file_name.endswith((".ma", ".mb", ".abc"))
        self.groupBox_checkbox.setVisible(is_maya_file)

        # 2-1 : 2. <체크박스> 각 행에 정보가 별개로 할당되도록 이전 체크 상태 저장 
        if file_name in self.file_checkbox_states:
            for checkbox, state in zip(self.checkboxes, self.file_checkbox_states[file_name]):
                checkbox.setChecked(state)
        else:
            for checkbox in self.checkboxes:
                checkbox.setChecked(False)

       # 2-1: 2. <파일 이름> 파일리스트의 이름(2행)을 받아오기 
        self.label_filename = self.ui.findChild(QLabel, "label_filename")
        file_name = selected_item.text()
        self.label_filename.setText(file_name)
        font = self.label_filename.font()
        font.setPointSize(14)
        self.label_filename.setFont(font)


        # 2-1: 3. 파일리스트의 로고(1행)을 label_logo에 불러오기 
        row = self.tableWidget_filelist.currentRow()
        icon_item = self.tableWidget_filelist.item(row, 1) 

        if icon_item and not icon_item.icon().isNull():  
            self.label_logo.setPixmap(icon_item.icon().pixmap(50, 50))  
        else:
            self.label_logo.clear() 
     # -----------------------------------2-2. 할당된 정보의 세부 사항들----------------------------------------

    def if_checked_checkbox(self, state):
        sender = self.sender()
        selected_options = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        print("선택된 옵션:", selected_options)

    def save_checkbox_state(self): 
        if self.current_file:
            self.file_checkbox_states[self.current_file] = [checkbox.isChecked() for checkbox in self.checkboxes]

     #===========================================================================================
     #----------------------------------------3-1. 로드 ------------------------------------------

    def load_ui(self):

        ui_file_path = os.path.join( publish_path ,"publish2.ui")

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()

        self.groupBox_checkbox = self.ui.findChild(QGroupBox, "groupBox_checkbox")

# 예외 발생 시 종료 코드 반환
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        ex = PublishUI()
        ex.show()
        sys.exit(app.exec())  
    except Exception as e:
        print(f"오류 발생: {e}")