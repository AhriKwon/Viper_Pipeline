try:
    from PySide6.QtWidgets import QMessageBox, QApplication, QMainWindow
    from PySide6.QtGui import QPixmap, QPainter, QBrush, QPainterPath, QScreen
    from PySide6.QtCore import Qt
except:
    from PySide2.QtWidgets import QMessageBox, QApplication, QMainWindow
    from PySide2.QtGui import QPixmap, QPainter, QBrush, QPainterPath, QScreen
    from PySide2.QtCore import Qt

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

#================================UI를 윈도우 가운데에서 시작=====================================


def center_on_screen(ui):
        """
        현재 사용하는 화면의 중앙에 윈도우를 배치
        """
        screen = QApplication.primaryScreen()  # 현재 사용 중인 화면 가져오기
        screen_geometry = screen.availableGeometry()  # 사용 가능한 화면 크기

        window_geometry = ui.frameGeometry()  # 현재 창의 크기
        window_geometry.moveCenter(screen_geometry.center())  # 화면의 중앙으로 이동

        ui.move(window_geometry.topLeft())  # 이동된 위치로 창을 배치