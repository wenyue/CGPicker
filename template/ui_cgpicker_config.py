# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cgpicker_config.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CGPickerConfig(object):
    def setupUi(self, CGPickerConfig):
        CGPickerConfig.setObjectName("CGPickerConfig")
        CGPickerConfig.resize(195, 551)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CGPickerConfig.sizePolicy().hasHeightForWidth())
        CGPickerConfig.setSizePolicy(sizePolicy)
        self.formLayout = QtWidgets.QFormLayout(CGPickerConfig)
        self.formLayout.setObjectName("formLayout")
        self.sceneAberrationEnduranceL = QtWidgets.QLabel(CGPickerConfig)
        self.sceneAberrationEnduranceL.setObjectName("sceneAberrationEnduranceL")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.sceneAberrationEnduranceL)
        self.sceneAberrationEndurance = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.sceneAberrationEndurance.setObjectName("sceneAberrationEndurance")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sceneAberrationEndurance)
        self.sceneAberrationThresholdL = QtWidgets.QLabel(CGPickerConfig)
        self.sceneAberrationThresholdL.setObjectName("sceneAberrationThresholdL")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.sceneAberrationThresholdL)
        self.sceneAberrationThreshold = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.sceneAberrationThreshold.setObjectName("sceneAberrationThreshold")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.sceneAberrationThreshold)
        self.faceBestSizeL = QtWidgets.QLabel(CGPickerConfig)
        self.faceBestSizeL.setObjectName("faceBestSizeL")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.faceBestSizeL)
        self.faceBestSize = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceBestSize.setObjectName("faceBestSize")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.faceBestSize)
        self.faceMaxSizeL = QtWidgets.QLabel(CGPickerConfig)
        self.faceMaxSizeL.setObjectName("faceMaxSizeL")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.faceMaxSizeL)
        self.faceMaxSize = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceMaxSize.setObjectName("faceMaxSize")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.faceMaxSize)
        self.faceExtendFactorL = QtWidgets.QLabel(CGPickerConfig)
        self.faceExtendFactorL.setObjectName("faceExtendFactorL")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.faceExtendFactorL)
        self.faceExtendFactor = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceExtendFactor.setObjectName("faceExtendFactor")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.faceExtendFactor)
        self.faceReforceFactorL = QtWidgets.QLabel(CGPickerConfig)
        self.faceReforceFactorL.setObjectName("faceReforceFactorL")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.faceReforceFactorL)
        self.faceReforceFactor = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceReforceFactor.setObjectName("faceReforceFactor")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.faceReforceFactor)
        self.faceSizeFactorL = QtWidgets.QLabel(CGPickerConfig)
        self.faceSizeFactorL.setObjectName("faceSizeFactorL")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.faceSizeFactorL)
        self.faceSizeFactor = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceSizeFactor.setObjectName("faceSizeFactor")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.faceSizeFactor)
        self.faceShapeFactorL = QtWidgets.QLabel(CGPickerConfig)
        self.faceShapeFactorL.setObjectName("faceShapeFactorL")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.faceShapeFactorL)
        self.faceShapeFactor = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceShapeFactor.setObjectName("faceShapeFactor")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.faceShapeFactor)
        self.faceAberrationFactorL = QtWidgets.QLabel(CGPickerConfig)
        self.faceAberrationFactorL.setObjectName("faceAberrationFactorL")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.faceAberrationFactorL)
        self.faceAberrationFactor = QtWidgets.QDoubleSpinBox(CGPickerConfig)
        self.faceAberrationFactor.setObjectName("faceAberrationFactor")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.faceAberrationFactor)
        self.line = QtWidgets.QFrame(CGPickerConfig)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.line)

        self.retranslateUi(CGPickerConfig)
        QtCore.QMetaObject.connectSlotsByName(CGPickerConfig)

    def retranslateUi(self, CGPickerConfig):
        _translate = QtCore.QCoreApplication.translate
        CGPickerConfig.setWindowTitle(_translate("CGPickerConfig", "Form"))
        self.sceneAberrationEnduranceL.setText(_translate("CGPickerConfig", "场景色差忍耐值："))
        self.sceneAberrationThresholdL.setText(_translate("CGPickerConfig", "场景色差阈值："))
        self.faceBestSizeL.setText(_translate("CGPickerConfig", "面部标准大小："))
        self.faceMaxSizeL.setText(_translate("CGPickerConfig", "面部上限大小："))
        self.faceExtendFactorL.setText(_translate("CGPickerConfig", "面部扩展系数："))
        self.faceReforceFactorL.setText(_translate("CGPickerConfig", "面部加强系数："))
        self.faceSizeFactorL.setText(_translate("CGPickerConfig", "面部大小系数："))
        self.faceShapeFactorL.setText(_translate("CGPickerConfig", "面部形状系数："))
        self.faceAberrationFactorL.setText(_translate("CGPickerConfig", "面部色差系数："))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CGPickerConfig = QtWidgets.QWidget()
    ui = Ui_CGPickerConfig()
    ui.setupUi(CGPickerConfig)
    CGPickerConfig.show()
    sys.exit(app.exec_())

