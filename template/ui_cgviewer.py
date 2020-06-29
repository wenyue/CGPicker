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
        CGViewer.resize(1172, 672)
        self.centralwidget = QtWidgets.QWidget(CGViewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        CGViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CGViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1172, 23))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        CGViewer.setMenuBar(self.menubar)

        self.retranslateUi(CGViewer)
        QtCore.QMetaObject.connectSlotsByName(CGViewer)

    def retranslateUi(self, CGViewer):
        _translate = QtCore.QCoreApplication.translate
        CGViewer.setWindowTitle(_translate("CGViewer", "CGViewer"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CGViewer = QtWidgets.QMainWindow()
    ui = Ui_CGViewer()
    ui.setupUi(CGViewer)
    CGViewer.show()
    sys.exit(app.exec_())

