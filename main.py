import os
import sys
from io import BytesIO
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class ShowMap(QWidget):
    def __init__(self):
        super().__init__()
        self.spn = 20
        self.image = None
        self.x, self.y = input().split(', ')
        self.initUI()
        self.getImage()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.y},{self.x}&z={self.spn}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        if os.path.exists('map.png'):
            os.remove('map.png')
        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.spn + 1 >= 21:
                return
            self.spn += 1
            self.getImage()
        if event.key() == Qt.Key_PageDown:
            if self.spn - 1 <= 0:
                return
            self.spn -= 1
            self.getImage()
        print(self.spn)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShowMap()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
