from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QEvent

import sys


class ThumbnailWidget(QWidget):
    def __init__(self, image_path=None, info_text="정보 없음"):
        super().__init__()
        self.init_ui(image_path, info_text)

    def init_ui(self, image_path, info_text):
        self.setFixedSize(120, 120)  # 썸네일 크기 고정

        # QLabel을 이용해 썸네일 배경 생성 (기본 노란색)
        self.label_thumbnail = QLabel(self)
        self.label_thumbnail.setFixedSize(120, 120)
        self.label_thumbnail.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(120, 120)
        pixmap.fill(QColor("yellow"))  # 노란색 배경

        # 이미지가 있으면 불러오기
        if image_path:
            image = QPixmap(image_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap = image

        self.label_thumbnail.setPixmap(pixmap)

        # 정보 오버레이 QLabel (기본적으로 숨김)
        self.label_info = QLabel(info_text, self)
        self.label_info.setFixedSize(120, 120)
        self.label_info.setAlignment(Qt.AlignCenter)
        self.label_info.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; font-size: 14px; padding: 5px;"
        )
        self.label_info.setVisible(False)

        # 투명도 효과 추가
        self.opacity_effect = QGraphicsOpacityEffect()
        self.label_thumbnail.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)  # 기본 밝기

        # 이벤트 필터 등록
        self.label_thumbnail.installEventFilter(self)

    def eventFilter(self, obj, event):
        """ 마우스가 썸네일 위에 올라가거나 벗어날 때 처리 """
        if obj == self.label_thumbnail:
            if event.type() == QEvent.Enter:
                self.on_hover()
            elif event.type() == QEvent.Leave:
                self.on_leave()
        return super().eventFilter(obj, event)

    def on_hover(self):
        """ 마우스를 올렸을 때 (썸네일 어두워짐 + 추가 정보 표시) """
        self.opacity_effect.setOpacity(0.5)  # 썸네일을 어둡게
        self.label_info.setVisible(True)  # 정보 텍스트 표시

    def on_leave(self):
        """ 마우스가 떠났을 때 (기본 상태로 복귀) """
        self.opacity_effect.setOpacity(1.0)  # 밝기 복원
        self.label_info.setVisible(False)  # 정보 숨김


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()

    # 예제 Thumbnail 위젯 생성
    thumbnail1 = ThumbnailWidget(None, "파일 이름: Example_001\n크기: 1200x800")
    thumbnail2 = ThumbnailWidget("thumbnail.jpg", "파일 이름: Example_002\n크기: 1024x768")

    layout.addWidget(thumbnail1)
    layout.addWidget(thumbnail2)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())
