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
            ('ABERRATION_ENDURANCE', self.aberrationEndurance),
            ('SCENE_ABERRATION_THRESHOLD', self.sceneAberrationThreshold),
            ('ACTION_ABERRATION_THRESHOLD', self.actionAberrationThreshold),
            ('FACE_BEST_SIZE', self.faceBestSize),
            ('FACE_MIN_SIZE', self.faceMinSize),
            ('FACE_MAX_SIZE', self.faceMaxSize),
            ('FACE_EXTEND_FACTOR', self.faceExtendFactor),
            ('FACE_SIZE_FACTOR', self.faceSizeFactor),
            ('FACE_SHAPE_FACTOR', self.faceShapeFactor),
            ('FACE_LEFT_FACTOR', self.faceLeftFactor),
            ('FACE_TOP_FACTOR', self.faceTopFactor),
            ('FACE_ABERRATION_FACTOR', self.faceAberrationFactor),
            ('FACE_REFORCE_FACTOR', self.faceReforceFactor),
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

        macro.FACE_MIN_SIZE = min(macro.FACE_MIN_SIZE, macro.FACE_BEST_SIZE)
        self.faceMinSize.setValue(macro.FACE_MIN_SIZE)
        macro.FACE_MAX_SIZE = max(macro.FACE_MAX_SIZE, macro.FACE_BEST_SIZE)
        self.faceMaxSize.setValue(macro.FACE_MAX_SIZE)

    def reloadMacro(self):
        from importlib import reload
        reload(macro)
        for macroName, ctrl in self._macroList:
            ctrl.setValue(getattr(macro, macroName))
