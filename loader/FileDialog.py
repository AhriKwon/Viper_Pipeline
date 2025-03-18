from PySide6 import QtWidgets


class FileDialog(QtWidgets.QDialog):
    """파일 생성 대화 상자"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("새 파일 생성")
        self.setLayout(self._create_ui())

    def _create_ui(self):
        """GUI 요소 생성"""
        layout = QtWidgets.QVBoxLayout()

        # 프로그램 선택 (Maya, Nuke, Houdini)
        self.program_selector = QtWidgets.QComboBox()
        self.program_selector.addItems(["Maya", "Nuke", "Houdini"])
        layout.addWidget(self.program_selector)

        # 파트 선택 드롭다운
        self.part_selector = QtWidgets.QComboBox()
        self.part_selector.addItems(["MDL", "RIG", "LDV", "LAY", "ANM", "LGT", "FX", "COM"])
        layout.addWidget(self.part_selector)

        # 필수 정보 입력 필드
        self.asset_type_input = QtWidgets.QLineEdit()
        self.asset_type_input.setPlaceholderText("asset_type (MDL, RIG, LDV 전용)")
        layout.addWidget(self.asset_type_input)

        self.asset_name_input = QtWidgets.QLineEdit()
        self.asset_name_input.setPlaceholderText("asset_name")
        layout.addWidget(self.asset_name_input)

        self.seq_input = QtWidgets.QLineEdit()
        self.seq_input.setPlaceholderText("seq (LAY, ANM, LGT, FX, COM 전용)")
        layout.addWidget(self.seq_input)

        self.shot_input = QtWidgets.QLineEdit()
        self.shot_input.setPlaceholderText("shot (LAY, ANM, LGT, FX, COM 전용)")
        layout.addWidget(self.shot_input)

        self.task_input = QtWidgets.QLineEdit()
        self.task_input.setPlaceholderText("task")
        layout.addWidget(self.task_input)

        # 파일 생성 버튼
        self.create_button = QtWidgets.QPushButton("파일 생성 및 실행")
        layout.addWidget(self.create_button)

        return layout

    def get_selected_options(self):
        """사용자가 선택한 옵션을 반환"""
        return {
            "program": self.program_selector.currentText(),
            "part": self.part_selector.currentText(),
            "asset_type": self.asset_type_input.text(),
            "asset_name": self.asset_name_input.text(),
            "seq": self.seq_input.text(),
            "shot": self.shot_input.text(),
            "task": self.task_input.text(),
        }
