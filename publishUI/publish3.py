from PySide6.QtWidgets import QMainWindow, QApplication, QCheckBox, QGroupBox, QVBoxLayout, QTreeWidget, QLabel, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys
import shotgun_api3

class ShotGridConnector:
    """ShotGrid API와 연동하여 데이터를 가져오고 업데이트하는 클래스"""

    # ShotGrid 서버 정보 설정
    SG_URL = "https://minseo.shotgrid.autodesk.com"
    SCRIPT_NAME = "Viper"
    API_KEY = "jvceqpsfqvbl1azzcns?haksI"

    # ShotGrid API 연결
    sg = shotgun_api3.Shotgun(SG_URL, SCRIPT_NAME, API_KEY)

    def get_user_tasks(user_id):
        """현재 사용자의 Task 목록을 가져옴"""
        tasks = ShotGridConnector.sg.find(
            "Task",
            [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]],
            ["id", "content", "sg_status_list", "entity"]
        )
        return tasks
    

class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_ui()
        self.set_checkbox()
        self.connect_signals() 


#-------------------------선택파일이 마야 파일일 경우 groupbox 안에 체크박스가 실행되는 ------------------------------------


    def set_checkbox(self):
        self.ui.groupBox_checkbox = self.ui.findChild(QGroupBox, "groupBox_checkbox")
        groupBoxLayout = self.groupBox_checkbox.layout() 

        if not groupBoxLayout:
            groupBoxLayout = QVBoxLayout(self.groupBox_combobox) 


        # 체크박스 옵션 설정 (마야파일일때만 실행된다)
        options = ["shader", "wireframe on shader", "textured", "wireframe on textured"]
        self.checkboxes = [] 

       # groupbox 안에 checkbox가 들어가도롱
        for option in options:
            checkbox = QCheckBox(option)  
            checkbox.stateChanged.connect(self.if_checked_checkbox) 
            groupBoxLayout.addWidget(checkbox)  
            self.checkboxes.append(checkbox)  

        self.groupBox_checkbox.setLayout(groupBoxLayout)
        self.groupBox_checkbox.setVisible(False) 


#-------------------------파일명을 라벨안에 입력 하는 행 ------------------------------------


    def connect_signals(self):
       
        self.treeWidget_filelist = self.ui.findChild(QTreeWidget, "treeWidget_filelist")
        self.treeWidget_filelist.itemSelectionChanged.connect(self.on_file_selected)

  
        self.label_filename = self.ui.findChild(QLabel, "label_filename")

        # 썸네일 설정하기
        self.groupBox_thumbnail = self.ui.findChild(QGroupBox, "groupBox_thumbnail")
        self.groupBox_thumbnail.mousePressEvent = self.open_file_dialog

        



#-------------------------유저가 클릭한 파일만 호출되도록하기  ------------------------------------

    def on_file_selected(self):
        selected_items = self.treeWidget_filelist.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            file_name = selected_item.text(0)  # 파일 이름을 가져옴
            
         
            if self.label_filename:
                self.label_filename.setText(f"선택된 파일: {file_name}")
            
            # Maya 파일일 경우 체크박스 보이기, Nuke 파일일 경우 숨기기
            if file_name.endswith(".ma") or file_name.endswith(".mb"):
                self.groupBox_combobox.setVisible(True)
            elif file_name.endswith(".nk"):
                self.groupBox_combobox.setVisible(False)
            else:
                self.groupBox_combobox.setVisible(False)


# -----------------------------------콤보박스의 옵션을 선택하는 행----------------------------------------

    def if_checked_checkbox(self, state):
        sender = self.sender()
        selected_options = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        print("선택된 옵션:", selected_options)

    def open_file_dialog(self, event):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images(*.png *.jpg *.bmp *.jpeg *.gif")
        file_dialog.setViewMode(QFileDialog.List)

    def load_ui(self):
        ui_file_path = "/home/rapa/teamwork/viper/publishUI/publish.ui" 

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
