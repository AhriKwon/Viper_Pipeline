from PySide6.QtWidgets import (
    QMainWindow, QApplication, QCheckBox, QGroupBox, QVBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QLabel, QFileDialog, QLineEdit
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys, os
from shotgun_api3 import Shotgun

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
from user_authenticator import UserAuthenticator
from shotgrid_connector import ShotGridConnector


class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_ui()
        self.set_checkbox() # 체크박스 실행 
        self.connect_signals() # 파일 정보 열람 
        self.populate_file_list()  # 파일 목록을 treeWidget_filelist에 추가

        # load.ui 사이즈 조절 
        self.setGeometry(100, 100, 1200, 800)
        self.resize(600, 700)


    #-------------------------선택파일이 마야 파일일 경우 groupbox 안에 체크박스가 실행되는 ------------------------------------


    def set_checkbox(self):

        self.groupBox_checkbox = self.ui.findChild(QGroupBox, "groupBox_checkbox")
        if self.groupBox_checkbox is None:
            print("오류: groupBox_checkbox를 찾을 수 없음")
            return

        groupBoxLayout = self.groupBox_checkbox.layout()
        if groupBoxLayout is None:
            groupBoxLayout = QVBoxLayout()
            self.groupBox_checkbox.setLayout(groupBoxLayout)

        # 체크박스 옵션 설정 (마야파일일때만 실행)
        options = ["shader", "wireframe on shader", "textured", "wireframe on textured"]
        self.checkboxes = []

        for option in options:
            checkbox = QCheckBox(option)
            checkbox.stateChanged.connect(self.if_checked_checkbox)
            groupBoxLayout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        self.groupBox_checkbox.setVisible(False) # 평소엔 보이지 않도록 


    #-------------------------파일명을 라벨안에 입력 하는 행 ------------------------------------


    def connect_signals(self):
        self.treeWidget_filelist = self.ui.findChild(QTreeWidget, "treeWidget_filelist")
      
      
        self.treeWidget_filelist.itemSelectionChanged.connect(self.on_file_selected)

        self.label_filename = self.ui.findChild(QLabel, "label_filename")
        self.lineEdit_taskname = self.ui.findChild(QLineEdit, "lineEdit_taskname")

        # 썸네일 설정하기
        self.groupBox_thumbnail = self.ui.findChild(QGroupBox, "groupBox_thumbnail")
        if self.groupBox_thumbnail is None:
            print("오류: groupBox_thumbnail을 찾을 수 없음")
        else:
            self.groupBox_thumbnail.mousePressEvent = self.open_file_dialog


    #-------------------------TreeWidget에 파일 목록을 추가하기 ------------------------------------


    def populate_file_list(self):
   
        directory_path = "/nas/show/Viper/assets/Character/teapot/CFS/maya/alembic"
        
        if not os.path.exists(directory_path):
            print(f"오류: 디렉터리가 존재하지 않음 - {directory_path}")
            return

        self.treeWidget_filelist.clear()  # 기존 항목 제거

        for file_name in sorted(os.listdir(directory_path)):  # 파일 정렬 후 추가
            if os.path.isfile(os.path.join(directory_path, file_name)):  # 파일만 추가
                item = QTreeWidgetItem(self.treeWidget_filelist)
                item.setText(0, file_name)


    #-------------------------유저가 클릭한 파일만 호출되도록 하기 ------------------------------------


    def on_file_selected(self):
       
        selected_items = self.treeWidget_filelist.selectedItems()

        if selected_items:
            selected_item = selected_items[0]
            file_name = selected_item.text(0)  # 파일 이름을 가져옴
            
            if self.label_filename:
                self.label_filename.setText(f"선택된 파일: {file_name}")

            if self.lineEdit_taskname:
                self.lineEdit_taskname.setText(file_name)

            # Maya 파일일 경우 체크박스 보이기, Nuke/Houdini 파일일 경우 숨기기
            if file_name.endswith(".ma") or file_name.endswith(".mb") or file_name.endswith(".abc"):
                self.groupBox_checkbox.setVisible(True)
            elif file_name.endswith(".nk") or file_name.endswith(".hip"):
                self.groupBox_checkbox.setVisible(False)
            else:
                self.groupBox_checkbox.setVisible(False)


    # -----------------------------------콤보박스의 옵션을 선택하는 행----------------------------------------


    def if_checked_checkbox(self, state):
        sender = self.sender()
        selected_options = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        print("선택된 옵션:", selected_options)

    def open_file_dialog(self, event):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp *.jpeg *.gif)")
        file_dialog.setViewMode(QFileDialog.List)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            print("선택된 파일:", selected_files)


    #-------------------------UI 로드-------------------------


    def load_ui(self):
        ui_file_path = "/home/rapa/teamwork/Viper/publishUI/publish.ui"

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PublishUI()
    ex.show()
    app.exec()
