
from PySide6.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QGroupBox, QComboBox, QVBoxLayout
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QFile

import sys
# import nuke
# import maya 


class PublishUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_ui()
        self.set_combobox()

        


#------------------------- groupbox 안에 콤보박스를 만드는 행------------------------------------

    def set_combobox(self):

        self.groupBox_combobox = self.ui.findChild(QGroupBox, "groupBox_combobox")
 
        groupBoxLayout = self.groupBox_combobox.layout() 
        if not groupBoxLayout:
            groupBoxLayout = QVBoxLayout(self.groupBox_combobox) 


        # 콤보 박스 안의 옵션
        options = ["shader", "wireframe on shader", "textured", "wireframe on textured"]


        self.comboboxes = [] 

        for i in range(4):

            combobox = QComboBox() 

            combobox.addItems(options)

            # 아무것도 선택되지 않은 상태 
            combobox.setCurrentIndex(-1)
            # 선택된 상태
            combobox.currentIndexChanged.connect(self.if_checked_combobox)
            groupBoxLayout.addWidget(combobox)
            self.comboboxes.append(combobox) 

            self.ui.groupBox_combobox.setLayout(groupBoxLayout)


# -----------------------------------콤보박스의 옵션을 선택하는 행----------------------------------------

    def if_checked_combobox(self, index):

        # sender은 어떤 위젯이 특정 동작을 트리거 했는지 확인하는 메서드
        sender = self.sender()
        selected_options = sender.currentText()

        # cb = combobox
        selected_options = [cb.currentText() for cb in self.comboboxes if cb.currentText()]
        
        
    

    def load_ui(self):
        ui_file_path = f"/home/rapa/teamwork/publish.ui" 

        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui) 
        self.ui.show()

if __name__ =="__main__":
    app = QApplication(sys.argv) 
    app.exec()
    ex = PublishUI()
    ex.show()
