#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QActionGroup
from template.ui_cgviewer import Ui_CGViewer

from ui.editor import Editor
from ui.picker_config import PickerConfig

from common import config
from common.random_pool import RatingRandomPool


class CGViewer(QMainWindow, Ui_CGViewer):

    def __init__(self, *args, **kwargs):
        super(CGViewer, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.showMaximized()

        #  self._randomPool = RatingRandomPool(config.get('path', 'output'))
        from common.database import Database
        self._database = Database(config.get('path', 'input'))
        sceneIdx = int(config.get('info', 'scene_index'))

        self.viewer = Editor(self)
        self.viewer.refresh(self._database, sceneIdx)
        self.horizontalLayout.addWidget(self.viewer)
        self.viewer.setVisible(True)

        self.editor = Editor(self)
        self.editor.refresh(self._database, sceneIdx)
        self.horizontalLayout.addWidget(self.editor)
        self.editor.setVisible(False)

        self.pickerConfig = PickerConfig(self)
        self.horizontalLayout.addWidget(self.pickerConfig)
        self.pickerConfig.setVisible(False)

        self.setupMainMenu()

    def setupMainMenu(self):
        self.menubar.setNativeMenuBar(False)

        # Window menu
        windowMenu = self.menubar.addMenu('&Window')

        viewerAction = windowMenu.addAction('Viewer')
        viewerAction.setShortcut('Esc')
        viewerAction.setCheckable(True)
        viewerAction.setChecked(self.viewer.isVisible())
        viewerAction.triggered.connect(self.switchToViewMode)

        editorAction = windowMenu.addAction('Editor')
        editorAction.setShortcut('Space')
        editorAction.setCheckable(True)
        editorAction.setChecked(self.editor.isVisible())
        editorAction.triggered.connect(self.switchToEditMode)

        workModeGroup = QActionGroup(windowMenu)
        workModeGroup.addAction(viewerAction)
        workModeGroup.addAction(editorAction)

        windowMenu.addSeparator()

        pickerConfigAction = windowMenu.addAction('Picker Config')
        pickerConfigAction.setShortcut('`')
        pickerConfigAction.setCheckable(True)
        pickerConfigAction.setChecked(self.pickerConfig.isVisible())
        pickerConfigAction.triggered.connect(self.pickerConfig.toggle)

        # Viewer menus
        #  self.viewer.setupMainMenu(self.menubar)
        # Editor menus
        self.editor.setupMainMenu(self.menubar)

    def switchToViewMode(self):
        self.viewer.setVisible(True)
        self.editor.setVisible(False)

    def switchToEditMode(self):
        self.viewer.setVisible(False)
        self.editor.setVisible(True)
