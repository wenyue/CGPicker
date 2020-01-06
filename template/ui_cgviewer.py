# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cgviewer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CGViewer(object):
    def setupUi(self, CGViewer):
        CGViewer.setObjectName("CGViewer")
        CGViewer.resize(792, 598)
        self.centralwidget = QtWidgets.QWidget(CGViewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.img = QtWidgets.QLabel(self.centralwidget)
        self.img.setEnabled(True)
        self.img.setGeometry(QtCore.QRect(9, 9, 16, 16))
        self.img.setText("")
        self.img.setScaledContents(True)
        self.img.setObjectName("img")
        CGViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CGViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 792, 23))
        self.menubar.setObjectName("menubar")
        CGViewer.setMenuBar(self.menubar)

        self.retranslateUi(CGViewer)
        QtCore.QMetaObject.connectSlotsByName(CGViewer)

    def retranslateUi(self, CGViewer):
        _translate = QtCore.QCoreApplication.translate
        CGViewer.setWindowTitle(_translate("CGViewer", "MainWindow"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CGViewer = QtWidgets.QMainWindow()
    ui = Ui_CGViewer()
    ui.setupUi(CGViewer)
    CGViewer.show()
    sys.exit(app.exec_())

