# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'face.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Face(object):
    def setupUi(self, Face):
        Face.setObjectName("Face")
        Face.resize(418, 317)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Face.sizePolicy().hasHeightForWidth())
        Face.setSizePolicy(sizePolicy)
        self.img = QtWidgets.QLabel(Face)
        self.img.setGeometry(QtCore.QRect(0, 0, 200, 200))
        self.img.setText("")
        self.img.setScaledContents(True)
        self.img.setObjectName("img")
        self.star = QtWidgets.QLabel(Face)
        self.star.setGeometry(QtCore.QRect(220, 200, 31, 31))
        self.star.setText("")
        self.star.setPixmap(QtGui.QPixmap("resource/star.png"))
        self.star.setScaledContents(True)
        self.star.setObjectName("star")

        self.retranslateUi(Face)
        QtCore.QMetaObject.connectSlotsByName(Face)

    def retranslateUi(self, Face):
        _translate = QtCore.QCoreApplication.translate
        Face.setWindowTitle(_translate("Face", "Form"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Face = QtWidgets.QWidget()
    ui = Ui_Face()
    ui.setupUi(Face)
    Face.show()
    sys.exit(app.exec_())

