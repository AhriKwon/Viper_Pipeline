from PySide6.QtWidgets import QMessageBox

#====================================경고, 알림창 팝업=========================================

def show_message(msg_type, title, message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if msg_type == "info":
        msg_box.setIcon(QMessageBox.Information)
    elif msg_type == "warning":
        msg_box.setIcon(QMessageBox.Warning)
    elif msg_type == "error":
        msg_box.setIcon(QMessageBox.Critical)
    elif msg_type == "question":
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    return msg_box.exec()

#===============================Qpixmap의 모서리를 둥글게 처리====================================

from PySide6.QtGui import QPixmap, QPainter, QBrush, QPainterPath
from PySide6.QtCore import Qt

def round_corners_pixmap(pixmap, radius=10):
    """
    QPixmap의 모서리를 둥글게 처리하는 함수
    """
    size = pixmap.size()
    rounded = QPixmap(size)
    rounded.fill(Qt.transparent)  # 투명 배경

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)  # 안티앨리어싱 활성화

    # 둥근 사각형 경로 생성
    path = QPainterPath()
    path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)

    # 둥근 영역 클리핑
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return rounded