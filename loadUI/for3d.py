from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QWidget, QVBoxLayout, QListWidget, QTabWidget

)
from PySide6.QtCore import Qt, QPropertyAnimation, QRectF, QPointF
from PySide6.QtGui import QTransform, QPainter
class AnimatedListView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ✅ QGraphicsView.Antialiasing이 아니라, QPainter.Antialiasing을 사용해야 함
        self.setRenderHint(QPainter.Antialiasing)  
        self.tabWidget = QTabWidget
        self.layout_proxies = []  

        # ✅ tabWidget 내부의 QListWidget 가져오기
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            list_widget = tab.findChild(QListWidget) 

            if list_widget:
                # ✅ QWidget을 만들어 QListWidget을 포함하도록 구성
                container = QWidget()
                layout = QVBoxLayout(container)
                layout.addWidget(list_widget)
                container.setLayout(layout)

                proxy = QGraphicsProxyWidget()
                proxy.setWidget(container)  
                self.scene().addItem(proxy)

                # ✅ 초기 위치 설정
                x_pos = i * 300  
                proxy.setPos(x_pos, 0)

                self.layout_proxies.append(proxy)  

        self.centerIndex = 1  
        self.updatePositions()

    def updatePositions(self):
        """위젯 회전 및 크기 조정"""
        for i, proxy in enumerate(self.layout_proxies):  
            animation = QPropertyAnimation(proxy, b"pos")  
            animation.setDuration(800)

            if i == self.centerIndex:
                transform = QTransform().rotate(0).scale(1.3, 1.3)
                proxy.setTransform(transform)
                proxy.setZValue(1)
                animation.setEndValue(QPointF(400, 0))  
            else:
                angle = -25 if i < self.centerIndex else 25
                transform = QTransform().rotate(angle).scale(0.9, 0.9)
                proxy.setTransform(transform)
                proxy.setZValue(0)
                x_offset = -120 if i < self.centerIndex else 120
                animation.setEndValue(QPointF(400 + x_offset, 40))  

            animation.start()



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    view = AnimatedListView()
    view.show()
    sys.exit(app.exec())



