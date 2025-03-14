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
        self.z = 15
        self.theme = "light"
        self.themeBtn.clicked.connect(self.change_theme)
        self.searchBtn.clicked.connect(self.get_coords)
        self.searchEdit.setText("Московский Кремль")
        self.resetBtn.clicked.connect(self.reset)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.themeBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.searchBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.resetBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.searchEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.get_coords()

    def getImage(self):
        api_server = "https://static-maps.yandex.ru/v1"
        params = {
            "apikey": "82a98fae-2424-4ed7-ad90-847166e51acf",
            "ll": ",".join(map(str, (self.lon, self.lat))),
            "z": str(self.z),
            "theme": self.theme,
        }
        if self.search != ():
            params["pt"] = (",".join((*map(str, self.search), "pm2rdm")),)
            self.resultLbl.setText(self.adress)
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

    def closeEvent(self, event):
        os.remove(self.map_file)

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
            self.lat += 90 / 2**self.z
            if self.lat >= 85:
                self.lat = -85
            self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Down:
            self.lat -= 90 / 2**self.z
            if self.lat <= -85:
                self.lat = 85
            self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.lon -= 180 / 2**self.z
            if self.lon <= -180:
                self.lon = 180
            self.getImage()
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.lon += 180 / 2**self.z
            if self.lon >= 180:
                self.lon = -180
            self.getImage()
        elif (
            event.key() == QtCore.Qt.Key.Key_Return
            or event.key() == QtCore.Qt.Key.Key_Enter
        ):
            self.get_coords()
            self.setFocus()

    def change_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.getImage()

    def get_coords(self):
        place = self.searchEdit.text()
        api_server = "http://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            "geocode": place,
            "format": "json",
        }
        response = requests.get(api_server, params=params)
        try:
            result = response.json()["response"]["GeoObjectCollection"][
                "featureMember"
            ][0]["GeoObject"]["Point"]["pos"]
            self.adress = response.json()["response"]["GeoObjectCollection"][
                "featureMember"
            ][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
            self.lon, self.lat = map(float, result.split())
            self.search = (self.lon, self.lat)
        except Exception:
            self.search = ()
        self.getImage()

    def reset(self):
        self.search = ()
        self.getImage()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
