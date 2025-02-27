from PySide6.QtWidgets import QMainWindow, QWidget,QApplication, QVBoxLayout,QTableWidgetItem, QGroupBox, QLabel, QTableWidget
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
        #//////findChild은 QTableWidget에 해당하는 클래스 타입 위젯을 찾아온다 

        # task를 불러오는 위젯
        self.tableWidget_2 = self.ui.findChild(QTableWidget, "tableWidget_2")

        # task의 정보를 불러오는 위젯
        self.groupBox_infor = self.ui.findChild(QGroupBox, "groupBox_infor")

        self.label_file_name = self.ui.findChild(QLabel, "label_filename")
        self.label_task_name = self.ui.findChild(QLabel, "label_task_name")
        self.label_version_id = self.ui.findChild(QLabel, "label_version_id")
        self.label_created_at = self.ui.findChild(QLabel, "label_created_at")
        self.tableWidget_2 = self.ui.findChild(QTableWidget, "tableWidget_2")
    

    

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

        # task를 담을 테이블 행과 열 (세로는 task 수만큼, 가로는 3줄)
        self.tableWidget_2.setRowCount(len(tasks) // 3 + (1 if len(tasks) % 3 != 0 else 0))
        self.tableWidget_2.setColumnCount(3)  

        # 헤더와 그리드라인 제거 (보기깔끔하게)
        self.tableWidget_2.horizontalHeader().setVisible(False)
        self.tableWidget_2.verticalHeader().setVisible(False)
        self.tableWidget_2.setShowGrid(False) 

       
        row, col = 0, 0

        for task in tasks:
            task_id = task["id"] # 샷그리드 내의 id
            task_name = task["content"] # 샷그리드 내의 content

            # 해당 Task에 연결된 파일(버전)들 가져오기
            versions = ShotGridConnector.get_publishes_for_task(task_id)

            # 기본적인 Task 정보만 테이블에 추가 (썸네일과 Task 이름)
            for version in versions:
                thumbnail_url = version.get("thumbnail", None)  # 썸네일 가져오기 

                # 세로 정렬된 썸네일 + Task 이름을 담을 위젯 생성
                container_widget = QWidget()
                layout = QVBoxLayout()

                # 테이블에 썸네일을 불러오는 코드 
                label_thumbnail = QLabel()
                if thumbnail_url:
                    pixmap = QPixmap(thumbnail_url)
                    label_thumbnail.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                layout.addWidget(label_thumbnail, alignment=Qt.AlignCenter)

                # Task 이름 추가
                label_task_name = QLabel(task_name)
                label_task_name.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_task_name)
                
                container_widget.setLayout(layout)
                self.tableWidget_2.setCellWidget(row, col, container_widget)
                
                # 다음 열로 이동, 3개를 채우면 다음 행으로 이동
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
               

             


        # 테이블의 행 크기를 자동으로 맞추기
        self.tableWidget_2.resizeRowsToContents()

        # 스크롤바 활성화 (수직 스크롤바는 자동으로 활성화)
        self.tableWidget_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # 파일 클릭 시 정보를 업데이트할 이벤트 연결
        self.tableWidget_2.cellClicked.connect(self.on_file_click)




####3===================================클릭한 파일의 정보를 띄우는 창====================================
#======================================================================================================



    def on_file_click(self, row, column):
        cell_widget = self.tableWidget_2.cellWidget(row, column)
        if cell_widget:
            task_name = cell_widget.layout().itemAt(1).widget().text()
            task_id = ShotGridConnector.get_task_id_by_name(task_name)
            
            # 해당 Task의 세부 정보 가져오기
            task = ShotGridConnector.get_user_tasks(int(task_id))

            # 상세 정보 표시
            self.label_task_name.setText(f"{task_name}")
            self.label_version_id.setText(f"{task['version_id']}")
            self.label_file_name.setText(f"{task['file_name']}")
            self.label_created_at.setText(f"{task['created_at']}")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LoadUI()
    ex.show()
    app.exec()
   