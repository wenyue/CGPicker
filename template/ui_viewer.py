# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'viewer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Viewer(object):
    def setupUi(self, Viewer):
        Viewer.setObjectName("Viewer")
        Viewer.setEnabled(True)
        Viewer.resize(838, 659)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Viewer.sizePolicy().hasHeightForWidth())
        Viewer.setSizePolicy(sizePolicy)
        Viewer.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.verticalLayout = QtWidgets.QVBoxLayout(Viewer)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.imgFrame = QtWidgets.QWidget(Viewer)
        self.imgFrame.setObjectName("imgFrame")
        self.img = QtWidgets.QLabel(self.imgFrame)
        self.img.setGeometry(QtCore.QRect(290, 190, 261, 211))
        self.img.setScaledContents(True)
        self.img.setObjectName("img")
        self.rating = QtWidgets.QLabel(self.imgFrame)
        self.rating.setGeometry(QtCore.QRect(0, 0, 54, 18))
        self.rating.setMinimumSize(QtCore.QSize(54, 18))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.rating.setFont(font)
        self.rating.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.rating.setObjectName("rating")
        self.verticalLayout.addWidget(self.imgFrame)

        self.retranslateUi(Viewer)
        QtCore.QMetaObject.connectSlotsByName(Viewer)

    def retranslateUi(self, Viewer):
        _translate = QtCore.QCoreApplication.translate
        self.rating.setText(_translate("Viewer", "⭐⭐⭐"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Viewer = QtWidgets.QWidget()
    ui = Ui_Viewer()
    ui.setupUi(Viewer)
    Viewer.show()
    sys.exit(app.exec_())

