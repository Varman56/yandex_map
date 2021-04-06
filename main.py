import os
import sys
import math
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import uic

SCREEN_SIZE = [600, 450]


class ShowMap(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.is_enable = False
        self.req_text.setEnabled(False)
        self.find_btn.setEnabled(False)
        self.find_btn.clicked.connect(self.getImage)
        self.typ = "map"
        self.z = 17
        self.x, self.y = 0, 0
        self.pt = None
        self.image = self.label
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.ad = ''
        self.initUI()

    def getImage(self):
        resp = self.req_text.text()
        if not resp:
            return
        if not self.ad or self.ad != resp:
            self.ad = resp
            self.get_pos(resp)
        params = {
            "ll": f"{self.y},{self.x}",
            "z": str(self.z),
            "l": self.typ,
            'pt': self.pt

        }
        print(params)
        map_request = f"http://static-maps.yandex.ru/1.x/?"
        response = requests.get(map_request, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason,
                  ")")
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
        elif event.key() == Qt.Key_PageDown:
            if self.z - 1 <= 0:
                return
            self.z -= 1
        elif event.key() == Qt.Key_Left:
            self.y -= 0.025 * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Right:
            self.y += 0.025 * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Down and self.y < 85:
            self.x -= 0.008 * math.pow(2, 15 - self.z)
            if self.x < -85:
                self.x = -85
        elif event.key() == Qt.Key_Up and self.y > -85:
            self.x += 0.008 * math.pow(2, 15 - self.z)
            if self.x > 85:
                self.x = 85
        elif event.key() == Qt.Key_1:
            self.typ = "map"
        elif event.key() == Qt.Key_2:
            self.typ = "sat"
        elif event.key() == Qt.Key_3:
            self.typ = "sat,skl"
        elif event.key() == Qt.Key_Return:
            self.is_enable = not self.is_enable
            self.req_text.setEnabled(self.is_enable)
            self.find_btn.setEnabled(self.is_enable)
            self.setFocus()
        else:
            return
        self.getImage()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

    def get_pos(self, address):
        params = {"apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                  "geocode": address,
                  "format": "json"}
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?"
        response = requests.get(geocoder_request, params=params)
        if response:
            json_response = response.json()
            toponym = \
                json_response["response"]["GeoObjectCollection"][
                    "featureMember"][
                    0][
                    "GeoObject"]
            self.y, self.x = tuple(map(float, toponym['Point']['pos'].split()))
            self.pt = f'{self.y},{self.x},comma'
            return
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShowMap()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
