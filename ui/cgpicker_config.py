#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame
from template.ui_cgpicker_config import Ui_CGPickerConfig
import macro


class CGPickerConfig(Ui_CGPickerConfig):
    def __init__(self, *args, **kwargs):
        self.root = QFrame(*args, **kwargs)
        self.setupUi(self.root)

        self.root.setVisible(False)
        self._macroList = (
            ('SCENE_ABERRATION_THRESHOLD', self.sceneAberrationThreshold),
            ('SCENE_ABERRATION_ENDURANCE', self.sceneAberrationEndurance),
            ('FACE_BEST_SIZE', self.faceBestSize),
            ('FACE_MAX_SIZE', self.faceMaxSize),
            ('FACE_EXTEND_FACTOR', self.faceExtendFactor),
            ('FACE_REFORCE_FACTOR', self.faceReforceFactor),
            ('FACE_SIZE_FACTOR', self.faceSizeFactor),
            ('FACE_SHAPE_FACTOR', self.faceShapeFactor),
            ('FACE_ABERRATION_FACTOR', self.faceAberrationFactor),
        )
        self.bindWithMacro()

    def toggle(self):
        self.root.setVisible(not self.root.isVisible())

    def bindWithMacro(self):
        for macroName, ctrl in self._macroList:
            ctrl.setValue(getattr(macro, macroName))
            ctrl.valueChanged.connect(self.updateMacro)

    def updateMacro(self):
        for macroName, ctrl in self._macroList:
            setattr(macro, macroName, ctrl.value())
