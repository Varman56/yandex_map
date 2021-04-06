import os
import sys
import math
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class ShowMap(QWidget):
    def __init__(self):
        super().__init__()
        self.z = 17
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.x, self.y = map(float, input().split(', '))
        self.initUI()
        self.getImage()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.y},{self.x}&z={self.z}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        os.remove('map.png')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.z + 1 >= 18:
                return
            self.z += 1
        if event.key() == Qt.Key_PageDown:
            if self.z - 1 <= 0:
                return
            self.z -= 1
        if event.key() == Qt.Key_Left:
            self.y -= 0.025 * math.pow(2, 15 - self.z)
        if event.key() == Qt.Key_Right:
            self.y += 0.025 * math.pow(2, 15 - self.z)
        if event.key() == Qt.Key_Down and self.y < 85:
            self.x -= 0.008 * math.pow(2, 15 - self.z)
        if event.key() == Qt.Key_Up and self.y > -85:
            self.x += 0.008 * math.pow(2, 15 - self.z)
        if self.y < -180:
            self.y = -180
        if self.y > 180:
            self.y = 180
        if self.x < -85:
            self.x = -85
        if self.x > 85:
            self.x = 85
        self.getImage()

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
