import os
import sys

import requests
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        self.lon, self.lat = "37.618879", "55.751422"
        self.z = 15
        self.getImage()

    def getImage(self):
        api_server = "https://static-maps.yandex.ru/v1"
        params = {
            "apikey": "82a98fae-2424-4ed7-ad90-847166e51acf",
            "ll": ",".join((self.lon, self.lat)),
            "z": str(self.z),
        }
        response = requests.get(api_server, params=params)
        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.lbl.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_PageDown:
            if self.z > 0:
                print(1)
                self.z -= 1
                self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_PageUp:
            if self.z < 21:
                self.z += 1
                self.getImage()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
