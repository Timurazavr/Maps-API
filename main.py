import os
import sys
import requests

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow

from decimal import Decimal
from math import pi, cos, sin, sqrt, atan2


def calculate_s(lon1, lag1, lon2, lag2):
    EARTH_RADIUS = 6372795
    lat1 = lon1 * pi / 180
    lat2 = lon2 * pi / 180
    long1 = lag1 * pi / 180
    long2 = lag2 * pi / 180
    cl1 = cos(lat1)
    cl2 = cos(lat2)
    sl1 = sin(lat1)
    sl2 = sin(lat2)
    delta = long2 - long1
    cdelta = cos(delta)
    sdelta = sin(delta)
    y = sqrt(pow(cl2 * sdelta, 2) + pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = atan2(y, x)
    dist = ad * EARTH_RADIUS
    return dist


class Example(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 530)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.photoLbl = QtWidgets.QLabel(parent=self.centralwidget)
        self.photoLbl.setGeometry(QtCore.QRect(0, 30, 600, 450))
        self.photoLbl.setText("")
        self.photoLbl.setObjectName("photoLbl")
        self.themeBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.themeBtn.setGeometry(QtCore.QRect(470, 490, 125, 30))
        self.themeBtn.setObjectName("themeBtn")
        self.searchEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.searchEdit.setGeometry(QtCore.QRect(5, 490, 200, 30))
        self.searchEdit.setInputMask("")
        self.searchEdit.setText("")
        self.searchEdit.setObjectName("searchEdit")
        self.searchBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.searchBtn.setGeometry(QtCore.QRect(285, 490, 75, 30))
        self.searchBtn.setObjectName("searchBtn")
        self.resetBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.resetBtn.setGeometry(QtCore.QRect(365, 490, 100, 30))
        self.resetBtn.setObjectName("resetBtn")
        self.resultLbl = QtWidgets.QLabel(parent=self.centralwidget)
        self.resultLbl.setGeometry(QtCore.QRect(0, 5, 600, 20))
        self.resultLbl.setText("")
        self.resultLbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.resultLbl.setObjectName("resultLbl")
        self.indexBox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.indexBox.setGeometry(QtCore.QRect(215, 490, 80, 30))
        self.indexBox.setObjectName("indexBox")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.themeBtn.setText(_translate("MainWindow", "Переключить тему"))
        self.searchBtn.setText(_translate("MainWindow", "Искать"))
        self.resetBtn.setText(_translate("MainWindow", "Сбросить цель"))
        self.indexBox.setText(_translate("MainWindow", "Индекс"))

    def __init__(self):
        super().__init__()
        self.setupUi(self)
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
            "apikey": "82a98fae-2424-4ed7-ad90-847166e51acf",
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

    def search(self, *args, coord: list | None = None, org: bool = False):
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
            if org:
                api_server = "https://search-maps.yandex.ru/v1/"
                params = {
                    "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
                    "text": self.adress[self.adress.find(",") + 2 :],
                    "lang": "ru_RU",
                    "type": "biz",
                    "spn": "0.001,0.001",
                    "results": 3,
                }
                response = requests.get(api_server, params=params)
                data = response.json().get("features", [])
                res = []
                for i in data:
                    res.append(
                        (
                            calculate_s(
                                *i["geometry"]["coordinates"], *map(float, coord)
                            ),
                            i["properties"]["CompanyMetaData"]["name"],
                        )
                    )
                if res and min(res)[0] < 100:
                    self.adress += " - " + min(res)[1]
        except Exception:
            self.pt = None
        self.getImage()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if self.z > 7:
            x, y = event.pos().x(), event.pos().y()
            if 0 <= x <= 600 and 30 <= y <= 480:
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self.search(
                        coord=[
                            self.ll[0]
                            + Decimal("0.0002") / 300 * (x - 300) * 2 ** (21 - self.z),
                            self.ll[1]
                            - Decimal("0.000086")
                            / 225
                            * (y - 255)
                            * 2 ** (21 - self.z),
                        ]
                    )
                elif event.button() == QtCore.Qt.MouseButton.RightButton:
                    self.search(
                        coord=[
                            self.ll[0]
                            + Decimal("0.0002") / 300 * (x - 300) * 2 ** (21 - self.z),
                            self.ll[1]
                            - Decimal("0.000086")
                            / 225
                            * (y - 255)
                            * 2 ** (21 - self.z),
                        ],
                        org=True,
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
