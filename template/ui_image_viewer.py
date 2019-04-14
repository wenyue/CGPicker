# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'image_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ImageViewer(object):
    def setupUi(self, ImageViewer):
        ImageViewer.setObjectName("ImageViewer")
        ImageViewer.setEnabled(True)
        ImageViewer.resize(682, 601)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ImageViewer.sizePolicy().hasHeightForWidth())
        ImageViewer.setSizePolicy(sizePolicy)
        ImageViewer.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.verticalLayout = QtWidgets.QVBoxLayout(ImageViewer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.imgFrame = QtWidgets.QWidget(ImageViewer)
        self.imgFrame.setObjectName("imgFrame")
        self.img = QtWidgets.QLabel(self.imgFrame)
        self.img.setGeometry(QtCore.QRect(0, 0, 400, 150))
        self.img.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.img.setScaledContents(True)
        self.img.setObjectName("img")
        self.home = QtWidgets.QLabel(self.imgFrame)
        self.home.setGeometry(QtCore.QRect(200, 80, 240, 240))
        self.home.setText("")
        self.home.setPixmap(QtGui.QPixmap("resource/home.png"))
        self.home.setScaledContents(True)
        self.home.setObjectName("home")
        self.verticalLayout.addWidget(self.imgFrame)
        self.actionNum = QtWidgets.QLabel(ImageViewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.actionNum.sizePolicy().hasHeightForWidth())
        self.actionNum.setSizePolicy(sizePolicy)
        self.actionNum.setText("")
        self.actionNum.setAlignment(QtCore.Qt.AlignCenter)
        self.actionNum.setObjectName("actionNum")
        self.verticalLayout.addWidget(self.actionNum)
        self.faceFrame = QtWidgets.QScrollArea(ImageViewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.faceFrame.sizePolicy().hasHeightForWidth())
        self.faceFrame.setSizePolicy(sizePolicy)
        self.faceFrame.setMinimumSize(QtCore.QSize(0, 200))
        self.faceFrame.setFocusPolicy(QtCore.Qt.TabFocus)
        self.faceFrame.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.faceFrame.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.faceFrame.setWidgetResizable(True)
        self.faceFrame.setObjectName("faceFrame")
        self.faces = QtWidgets.QWidget()
        self.faces.setEnabled(True)
        self.faces.setGeometry(QtCore.QRect(0, 0, 16, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.faces.sizePolicy().hasHeightForWidth())
        self.faces.setSizePolicy(sizePolicy)
        self.faces.setFocusPolicy(QtCore.Qt.NoFocus)
        self.faces.setObjectName("faces")
        self.faceFrame.setWidget(self.faces)
        self.verticalLayout.addWidget(self.faceFrame)

        self.retranslateUi(ImageViewer)
        QtCore.QMetaObject.connectSlotsByName(ImageViewer)

    def retranslateUi(self, ImageViewer):
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ImageViewer = QtWidgets.QWidget()
    ui = Ui_ImageViewer()
    ui.setupUi(ImageViewer)
    ImageViewer.show()
    sys.exit(app.exec_())

