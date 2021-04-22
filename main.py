import os
import sys
import math
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import uic

SCREEN_SIZE = [600, 450]  # размеры экрана


class ShowMap(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.is_enable = False
        self.req_text.setEnabled(False)
        self.reset_btn.clicked.connect(self.reset_res)
        self.postal_code.stateChanged.connect(self.add_post_code)
        self.typ = "map"
        self.z = 17
        self.x, self.y = 0, 0
        self.pt = None
        self.image = self.label
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.ad = ''
        self.full_address = ''
        self.post = ''
        self.initUI()

    def add_post_code(self):
        if self.postal_code.isChecked():
            self.adress.setText(self.full_address + ' ' + self.post)
        else:
            self.adress.setText(self.full_address)

    def reset_res(self):
        self.pt = None
        self.full_address = ''
        self.adress.setText(self.full_address)
        self.getImage()

    def getImage(self, pt=False, mouse_req=False):
        if not mouse_req:
            resp = self.req_text.text()
            if not resp:
                return
            if not self.ad or pt:
                self.ad = resp
                self.get_pos(resp)
        params = {
            "ll": f"{self.y},{self.x}",
            "z": str(self.z),
            "l": self.typ,
            'pt': self.pt

        }
        map_request = f"http://static-maps.yandex.ru/1.x/?"
        response = requests.get(map_request, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(",
                  response.reason,
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
        elif event.key() == Qt.Key_Down and self.x < 85:
            self.x -= 0.008 * math.pow(2, 15 - self.z)
            if self.x < -85:
                self.x = -85
        elif event.key() == Qt.Key_Up and self.x > -85:
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
            self.setFocus()
            if not self.is_enable:
                self.getImage(True)
            return
        else:
            return
        self.getImage()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

    def to_geo_coords(self, pos):
        dx = 225 - pos[1]
        dy = pos[0] - 300
        lx = self.x + dx * 0.00002 * math.pow(2, 15 - self.z)
        ly = self.y + dy * 0.00004 * math.cos(
            math.radians(self.y)) * math.pow(2, 15 - self.z)
        return lx, ly

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
            try:
                self.full_address = \
                    toponym['metaDataProperty']['GeocoderMetaData']['Address'][
                        'formatted']
            except Exception:
                self.full_address = '---'
            try:
                self.post = \
                    toponym['metaDataProperty']['GeocoderMetaData']['Address'][
                        'postal_code']
            except Exception:
                self.post = '------'
            r = self.full_address
            if self.postal_code.isChecked():
                r += ' ' + self.post
            self.adress.setText(r)
            self.y, self.x = tuple(map(float, toponym['Point']['pos'].split()))
            self.pt = f'{self.y},{self.x},comma'
            return
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            x, y = self.to_geo_coords((event.x(), event.y()))
            self.get_pos(f"{y},{x}")
            self.getImage(mouse_req=True)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShowMap()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
