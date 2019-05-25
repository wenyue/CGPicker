#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QFileDialog, qApp, QAction
from template.ui_cgpicker import Ui_CGPicker
from ui.image_viewer import ImageViewer
from ui.cgpicker_config import CGPickerConfig
from ui.loading import Loading
from database import data
import config
import os


class CGPicker(Ui_CGPicker):
    def __init__(self, *args, **kwargs):
        self.root = QMainWindow(*args, **kwargs)
        self.setupUi(self.root)

        self.addSubPanel()
        self.setupMainMenu()

    def addSubPanel(self):
        self.imageViewer = ImageViewer()
        self.horizontalLayout.addWidget(self.imageViewer.root)

        self.CGPickerConfig = CGPickerConfig()
        self.horizontalLayout.addWidget(self.CGPickerConfig.root)

    def setupMainMenu(self):
        menubar = self.menubar
        fileMenu = menubar.addMenu('&File')

        importAction = QAction('&Import', self.root)
        importAction.setShortcut('Ctrl+I')
        importAction.triggered.connect(self.pickCGToTmp)
        fileMenu.addAction(importAction)

        importAction = QAction('&Import from love', self.root)
        importAction.setShortcut('Ctrl+Shift+I')
        importAction.triggered.connect(self.pickLoveToTmp)
        fileMenu.addAction(importAction)

        exportAction = QAction('&Export', self.root)
        exportAction.setShortcut('Ctrl+O')
        exportAction.triggered.connect(self.collectPickToCG)
        fileMenu.addAction(exportAction)

        convertAction = QAction('&Convert images', self.root)
        convertAction.setShortcut('Ctrl+F')
        convertAction.triggered.connect(self.convertImages)
        fileMenu.addAction(convertAction)

        fileMenu.addSeparator()

        quitAction = QAction('&Quit', self.root)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(quitAction)

        windowMenu = menubar.addMenu('&Window')

        CGPickerConfigAction = QAction('&Change pick factor', self.root)
        CGPickerConfigAction.setShortcut('`')
        CGPickerConfigAction.triggered.connect(self.CGPickerConfig.toggle)
        windowMenu.addAction(CGPickerConfigAction)

        self.imageViewer.setupMainMenu(menubar)

    def pickCGToTmp(self):
        from tools.picker import pickCGToTmp
        from tools.converter import convertImages
        lastCGPath = config.get('path', 'input')
        CGPath = QFileDialog.getExistingDirectory(
            self.root, 'choose directory', lastCGPath)
        if not CGPath:
            return
        config.set('path', 'input', CGPath)
        config.set('path', 'CGName', os.path.basename(CGPath))
        self.createLoading(lambda: convertImages(CGPath))
        self.CGPickerConfig.reloadMacro()
        self.createLoading(lambda: pickCGToTmp(CGPath))
        data.loadDataFromTmp()
        self.imageViewer.show()

    def pickLoveToTmp(self):
        from tools.picker import pickLoveToTmp
        outPath = config.get('path', 'output')
        lovePath = QFileDialog.getExistingDirectory(
            self.root, 'choose directory', outPath)
        if not lovePath:
            return
        index = lovePath.rfind('[')
        if index == -1:
            CGName = os.path.basename(lovePath)
        else:
            CGName = os.path.basename(lovePath[0:index])
        config.set('path', 'CGName', CGName)
        self.CGPickerConfig.reloadMacro()
        self.createLoading(lambda: pickLoveToTmp(outPath, lovePath, CGName))
        data.loadDataFromTmp()
        self.imageViewer.show()

    def collectPickToCG(self):
        from tools.collector import collectPickToCG
        CGName = config.get('path', 'CGName')
        outPath = config.get('path', 'output')
        self.createLoading(lambda: collectPickToCG(outPath, CGName))

    def convertImages(self):
        from tools.converter import convertImages
        lastCGPath = config.get('path', 'input')
        CGPath = QFileDialog.getExistingDirectory(
            self.root, 'choose directory', lastCGPath)
        if not CGPath:
            return
        config.set('path', 'input', CGPath)
        self.createLoading(lambda: convertImages(CGPath))

    def show(self):
        self.root.showMaximized()
        self.imageViewer.show()

    def createLoading(self, task):
        self.root.setEnabled(False)
        loading = Loading(self.root)
        loading.show(task)
        self.root.setEnabled(True)
