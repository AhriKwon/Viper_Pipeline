from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QGroupBox, QLabel, QTableWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QPixmap
import sys, os
from shotgun_api3 import Shotgun


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shotgridAPI')))
# sys.path.append("/home/rapa/teamwork/viper")
from user_authenticator import UserAuthenticator
# from user_authenticator import UserAuthenticator # 로그인 클래스 호출
from shotgrid_connector import ShotGridConnector # 샷그리드 클래스 호출 




#============================================================================================
#====================loader ui class : LoadUI==============================================



class LoadUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.load_ui()
        self.login_and_load_tasks()  

        # 연결될 샷그리드 
        # self.sg_url = "https://minseo.shotgrid.autodesk.com"
        # self.script_name = "Viper"
        # self.api_key = "jvceqpsfqvbl1azzcns?haksI"

        # ShotGridConnector(샷그리드 호출 class) 
        # self.sg_connector = ShotGridConnector()
        # self.sg_login = UserAuthenticator()
        



    #====================================qt designer 로드=======================================


    def load_ui(self):
    
        ui_file_path = "/home/rapa/teamwork/viper/loadUI/load.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.ui.show()

        # ui 설정하기 
        # findChild은 QTableWidget에 해당하는 클래스 타입 위젯을 찾아온다 

        # task를 불러오는
        self.tableWidget_2 = self.ui.findChild(QTableWidget, "tableWidget_2")
        # task의 정보를 불러오는 
        self.groupBox_infor = self.ui.findChild(QGroupBox, "groupBox_infor")

        self.label_file_name = self.ui.findChild(QLabel, "label_filename")
        self.label_task_name = self.ui.findChild(QLabel, "label_task_name")
        self.label_version_id = self.ui.findChild(QLabel, "label_version_id")
        self.label_created_at = self.ui.findChild(QLabel, "label_created_at")


    #=============================로그인, task 목록을 가져오는====================================



    def login_and_load_tasks(self):
        username = "owlgrowl0v0@gmail.com"
        user_data = UserAuthenticator.login(username)

        if "error" not in user_data:
            user_id = user_data["id"]
            user_tasks = ShotGridConnector.get_user_tasks(user_id) 
            self.populate_table(user_tasks)
        else:
            print("Error")

    #=======================================================================================


    def populate_table(self, tasks):
        if not tasks:
            return

        # task를 담을 테이블 행과 열 초기화
        self.tableWidget_2.setRowCount(len(tasks))
        self.tableWidget_2.setColumnCount(3)  # 썸네일과 Task 이름만 표시

        row = 0

        for task in tasks:
            task_id = task["id"]
            task_name = task["content"]

            # 해당 Task에 연결된 파일(버전)들 가져오기
            versions = ShotGridConnector.get_publishes_for_task(task_id)

            # 기본적인 Task 정보만 테이블에 추가 (썸네일과 Task 이름)
            for version in versions:
                thumbnail_url = version.get("thumbnail", None)

                # 테이블에 썸네일과 Task 이름 채우기
                if thumbnail_url:
                    pixmap = QPixmap(thumbnail_url)
                    label = QLabel()
                    label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                    self.tableWidget_2.setCellWidget(row, 0, label)
                else:
                    self.tableWidget_2.setCellWidget(row, 0, QLabel())

                self.tableWidget_2.setItem(row, 1, QTableWidgetItem(task_name))  # Task 이름

                # 클릭 시 해당 파일의 ID와 세부 정보를 얻을 수 있도록 설정
                self.tableWidget_2.setItem(row, 2, QTableWidgetItem(str(task_id)))  # Task ID 추가

                row += 1  # 행을 하나씩 추가

        # 테이블의 행 크기를 자동으로 맞추기
        self.tableWidget_2.resizeRowsToContents()

        # 스크롤바 활성화 (수직 스크롤바는 자동으로 활성화)
        self.tableWidget_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # 파일 클릭 시 정보를 업데이트할 이벤트 연결
        self.tableWidget_2.cellClicked.connect(self.on_file_click)


    def on_file_click(self, row, column):
        
        task_name = self.tableWidget_2.item(row, 1).text()  # 클릭된 Task 이름
        task_id = self.tableWidget_2.item(row, 2).text()  # 클릭된 Task ID 가져오기

        # 해당 Task의 세부 정보 가져오기
        task = self.sg_connector.get_task_status(int(task_id))

        # 상세 정보 표시
        self.label_task_name.setText(f"Task 이름: {task_name}")
        self.label_version_id.setText(f"버전 ID: {task['version_id']}")
        self.label_file_name.setText(f"파일 이름: {task['file_name']}")
        self.label_created_at.setText(f"생성일: {task['created_at']}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LoadUI()
    ex.show()
    app.exec()
   