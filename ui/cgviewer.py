#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QAction, QActionGroup
from template.ui_cgviewer import Ui_CGViewer

from ui.editor import Editor
from ui.viewer import Viewer
from ui.picker_config import PickerConfig

from common import config
from common.random_pool import RatingRandomPool


class CGViewer(QMainWindow, Ui_CGViewer):

    def __init__(self, *args, **kwargs):
        super(CGViewer, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setupFullScreenAction()

        self._randomPool = RatingRandomPool(config.get('path', 'output'))

        self.viewer = Viewer(self)
        self.viewer.init(self._randomPool)
        self.horizontalLayout.addWidget(self.viewer)
        self.viewer.setVisible(True)

        self.editor = Editor(self)
        self.horizontalLayout.addWidget(self.editor)
        self.editor.setVisible(False)

        self.pickerConfig = PickerConfig(self)
        self.horizontalLayout.addWidget(self.pickerConfig)
        self.pickerConfig.setVisible(False)

        self.setupMainMenu()

    def setupFullScreenAction(self):
        self.showFullScreen()
        self.menubar.setFixedHeight(0)

        def toggleFullScreen():
            if not self.isFullScreen():
                self.showFullScreen()
                self.menubar.setFixedHeight(0)
            else:
                self.showMaximized()
                self.menubar.setFixedHeight(23)

        toggleFullScreenAction = QAction(self)
        toggleFullScreenAction.setShortcut(QKeySequence.FullScreen)
        toggleFullScreenAction.triggered.connect(toggleFullScreen)
        self.addAction(toggleFullScreenAction)

    def setupMainMenu(self):
        # File menu
        fileMenu = self.menubar.addMenu('&File')

        quitAction = fileMenu.addAction('&Quit')
        quitAction.triggered.connect(self.close)

        # Window menu
        windowMenu = self.menubar.addMenu('&Window')

        viewerAction = windowMenu.addAction('Viewer')
        viewerAction.setCheckable(True)
        viewerAction.triggered.connect(self.switchToViewMode)

        editorAction = windowMenu.addAction('Editor')
        editorAction.setCheckable(True)
        editorAction.triggered.connect(self.switchToEditMode)

        toggleWorkModeAction = QAction(self)
        toggleWorkModeAction.setShortcut('Esc')
        toggleWorkModeAction.triggered.connect(self.toggleWorkMode)
        self.addAction(toggleWorkModeAction)

        workModeGroup = QActionGroup(windowMenu)
        workModeGroup.addAction(viewerAction)
        workModeGroup.addAction(editorAction)

        def update():
            viewerAction.setChecked(self.viewer.isVisible())
            editorAction.setChecked(self.editor.isVisible())

        windowMenu.aboutToShow.connect(update)

        windowMenu.addSeparator()

        pickerConfigAction = windowMenu.addAction('Picker Config')
        pickerConfigAction.setShortcut('`')
        pickerConfigAction.setCheckable(True)
        pickerConfigAction.setChecked(self.pickerConfig.isVisible())
        pickerConfigAction.triggered.connect(self.pickerConfig.toggle)

        # Viewer menus
        self.viewer.setupMainMenu(self.menubar)
        # Editor menus
        self.editor.setupMainMenu(self.menubar)

    def toggleWorkMode(self):
        if self.viewer.isVisible():
            self.switchToEditMode()
        else:
            self.switchToViewMode()

    def switchToViewMode(self):
        self._randomPool.setDirty(self.viewer.curDatabaseIdx, needToFlush=True)
        self.viewer.refresh()
        self.viewer.setVisible(True)
        self.editor.setVisible(False)

    def switchToEditMode(self):
        self.editor.init(self.viewer.curDatabase, self.viewer.curSceneIdx)
        self.viewer.setVisible(False)
        self.editor.setVisible(True)

    def closeEvent(self, event):
        self._randomPool.flush()
