# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cgpicker.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CGPicker(object):
    def setupUi(self, CGPicker):
        CGPicker.setObjectName("CGPicker")
        CGPicker.resize(1172, 672)
        self.centralwidget = QtWidgets.QWidget(CGPicker)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        CGPicker.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CGPicker)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1172, 23))
        self.menubar.setObjectName("menubar")
        CGPicker.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(CGPicker)
        self.statusbar.setObjectName("statusbar")
        CGPicker.setStatusBar(self.statusbar)

        self.retranslateUi(CGPicker)
        QtCore.QMetaObject.connectSlotsByName(CGPicker)

    def retranslateUi(self, CGPicker):
        _translate = QtCore.QCoreApplication.translate
        CGPicker.setWindowTitle(_translate("CGPicker", "MainWindow"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CGPicker = QtWidgets.QMainWindow()
    ui = Ui_CGPicker()
    ui.setupUi(CGPicker)
    CGPicker.show()
    sys.exit(app.exec_())

