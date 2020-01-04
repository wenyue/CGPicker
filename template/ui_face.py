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
        Face.resize(130, 130)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Face.sizePolicy().hasHeightForWidth())
        Face.setSizePolicy(sizePolicy)
        self.img = QtWidgets.QLabel(Face)
        self.img.setGeometry(QtCore.QRect(0, 0, 130, 130))
        self.img.setAutoFillBackground(False)
        self.img.setText("")
        self.img.setScaledContents(True)
        self.img.setObjectName("img")
        self.icons = QtWidgets.QWidget(Face)
        self.icons.setGeometry(QtCore.QRect(80, 80, 50, 50))
        self.icons.setObjectName("icons")
        self.circle = QtWidgets.QLabel(self.icons)
        self.circle.setGeometry(QtCore.QRect(0, 0, 50, 50))
        self.circle.setText("")
        self.circle.setPixmap(QtGui.QPixmap("resource/circle.png"))
        self.circle.setScaledContents(True)
        self.circle.setObjectName("circle")
        self.star = QtWidgets.QLabel(self.icons)
        self.star.setGeometry(QtCore.QRect(0, 0, 50, 50))
        self.star.setText("")
        self.star.setPixmap(QtGui.QPixmap("resource/star.png"))
        self.star.setScaledContents(True)
        self.star.setObjectName("star")
        self.starNum = QtWidgets.QLabel(self.icons)
        self.starNum.setGeometry(QtCore.QRect(0, 0, 50, 50))
        self.starNum.setText("")
        self.starNum.setTextFormat(QtCore.Qt.AutoText)
        self.starNum.setAlignment(QtCore.Qt.AlignCenter)
        self.starNum.setObjectName("starNum")

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

