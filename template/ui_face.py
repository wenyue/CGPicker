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
        self.number = QtWidgets.QLabel(self.icons)
        self.number.setGeometry(QtCore.QRect(0, 0, 50, 50))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.number.setFont(font)
        self.number.setTextFormat(QtCore.Qt.AutoText)
        self.number.setAlignment(QtCore.Qt.AlignCenter)
        self.number.setObjectName("number")
        self.outline = QtWidgets.QLabel(self.icons)
        self.outline.setEnabled(True)
        self.outline.setGeometry(QtCore.QRect(0, 0, 50, 50))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.outline.setFont(font)
        self.outline.setStyleSheet("color: white")
        self.outline.setTextFormat(QtCore.Qt.AutoText)
        self.outline.setAlignment(QtCore.Qt.AlignCenter)
        self.outline.setObjectName("outline")
        self.star.raise_()
        self.circle.raise_()
        self.outline.raise_()
        self.number.raise_()

        self.retranslateUi(Face)
        QtCore.QMetaObject.connectSlotsByName(Face)

    def retranslateUi(self, Face):
        _translate = QtCore.QCoreApplication.translate
        Face.setWindowTitle(_translate("Face", "Form"))
        self.number.setText(_translate("Face", "20"))
        self.outline.setText(_translate("Face", "20"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Face = QtWidgets.QWidget()
    ui = Ui_Face()
    ui.setupUi(Face)
    Face.show()
    sys.exit(app.exec_())

