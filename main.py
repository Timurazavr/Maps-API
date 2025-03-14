import os
import sys

import requests
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow
from decimal import Decimal


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        self.z = 15
        self.theme = "light"
        self.themeBtn.clicked.connect(self.change_theme)
        self.searchBtn.clicked.connect(self.search)
        self.searchEdit.setText("Московский Кремль")
        self.resetBtn.clicked.connect(self.reset)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.themeBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.searchBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.resetBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.indexBox.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.searchEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.indexBox.checkStateChanged.connect(self.getImage)
        self.search()

    def getImage(self):
        api_server = "https://static-maps.yandex.ru/v1"
        params = {
            "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13",
            "ll": ",".join(map(str, self.ll)),
            "z": self.z,
            "theme": self.theme,
        }
        if self.pt is not None:
            params["pt"] = ",".join((*map(str, self.pt), "pm2rdm"))
            if self.indexBox.isChecked():
                self.resultLbl.setText(self.adress)
            else:
                self.resultLbl.setText(self.adress[self.adress.find(",") + 2 :])
        else:
            self.resultLbl.setText("")
        response = requests.get(api_server, params=params)
        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.photoLbl.setPixmap(self.pixmap)

        # print(response.url)

    def search(self, *args, coord: list | None = None):
        place = self.searchEdit.text()
        api_server = "http://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            "geocode": ",".join(map(str, coord)) if coord else place,
            "format": "json",
        }
        try:
            response = requests.get(api_server, params=params)
            result = response.json()["response"]["GeoObjectCollection"][
                "featureMember"
            ][0]["GeoObject"]
            self.adress = result["metaDataProperty"]["GeocoderMetaData"]["text"]
            if (
                "postal_code"
                in result["metaDataProperty"]["GeocoderMetaData"]["Address"]
            ):
                self.adress = (
                    result["metaDataProperty"]["GeocoderMetaData"]["Address"][
                        "postal_code"
                    ]
                    + ", "
                    + self.adress
                )
            else:
                self.adress = "Индекс не указан, " + self.adress
            if coord is None:
                self.ll = list(map(Decimal, result["Point"]["pos"].split()))
                self.pt = self.ll.copy()
            else:
                self.pt = coord.copy()
        except Exception as err:
            self.pt = None
        self.getImage()

    def mousePressEvent(self, event):
        if self.z > 7:
            x, y = event.pos().x(), event.pos().y()
            if 0 <= x <= 600 and 30 <= y <= 480:
                self.search(
                    coord=[
                        self.ll[0]
                        + Decimal("0.0002") / 300 * (x - 300) * 2 ** (21 - self.z),
                        self.ll[1]
                        - Decimal("0.000086") / 225 * (y - 255) * 2 ** (21 - self.z),
                    ]
                )

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_PageDown:
            if self.z > 0:
                self.z -= 1
                self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_PageUp:
            if self.z < 21:
                self.z += 1
                self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Up:
            self.ll[1] += Decimal(90) / 2**self.z
            if self.ll[1] >= 85:
                self.ll[1] = -85
            self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Down:
            self.ll[1] -= Decimal(90) / 2**self.z
            if self.ll[1] <= -85:
                self.ll[1] = 85
            self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.ll[0] -= Decimal(180) / 2**self.z
            if self.ll[0] <= -180:
                self.ll[0] = 180
            self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.ll[0] += Decimal(180) / 2**self.z
            if self.ll[0] >= 180:
                self.ll[0] = -180
            self.getImage()
        elif (
            event.key() == QtCore.Qt.Key.Key_Return
            or event.key() == QtCore.Qt.Key.Key_Enter
        ):
            self.search()
            self.setFocus()

    def reset(self):
        self.pt = None
        self.getImage()

    def change_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.getImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
