#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog, qApp, QAction
from template.ui_cgpicker import Ui_CGPicker

from ui.image_viewer import ImageViewer
from ui.cgpicker_config import CGPickerConfig
from ui.loading import Loading
from database import data
import config
import macro


class CGPicker(QMainWindow, Ui_CGPicker):
    def __init__(self, *args, **kwargs):
        super(CGPicker, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.setupMainMenu()
        self.addSubPanel()

    def addSubPanel(self):
        windowMenu = self.menubar.addMenu('&Window')

        self.imageViewer = ImageViewer(self.menubar)
        self.imageViewer.setupMainMenu(self.menubar)
        self.horizontalLayout.addWidget(self.imageViewer)

        self.CGPickerConfig = CGPickerConfig(self.menubar)
        self.CGPickerConfig.setupMainMenu(windowMenu)
        self.horizontalLayout.addWidget(self.CGPickerConfig)

    def setupMainMenu(self):
        menubar = self.menubar
        fileMenu = menubar.addMenu('&File')

        importAction = QAction('&Import', self)
        importAction.setShortcut('Ctrl+I')
        importAction.triggered.connect(self.pickCG)
        fileMenu.addAction(importAction)

        exportAction = QAction('&Export', self)
        exportAction.setShortcut('Ctrl+O')
        exportAction.triggered.connect(self.collectPickToCG)
        fileMenu.addAction(exportAction)

        fileMenu.addSeparator()

        formatAction = QAction('&Format Image names', self)
        formatAction.triggered.connect(self.formatImageNames)
        fileMenu.addAction(formatAction)

        upscaleAction = QAction('&Upscale Images', self)
        upscaleAction.triggered.connect(self.upscaleImages)
        fileMenu.addAction(upscaleAction);

        convertAction = QAction('&Convert Images', self)
        convertAction.triggered.connect(self.convertImages)
        fileMenu.addAction(convertAction)

        fileMenu.addSeparator()

        quitAction = QAction('&Quit', self)
        quitAction.setShortcut('Esc')
        quitAction.triggered.connect(self.quit)
        fileMenu.addAction(quitAction)

    def pickCG(self):
        from tools.name_formater import formatImageNames
        from tools.upscaler import upscaleImages
        from tools.converter import convertImages
        from tools.picker import pickCG
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Pick CG',
                                                  lastCGRoot)
        if not CGRoot:
            return

        if not os.path.isfile(os.path.join(CGRoot, macro.DATABASE_FILE)):
            from importlib import reload
            reload(macro)
            self.CGPickerConfig.reloadMacro()
            formatImageNames(CGRoot)
            self.createLoading(lambda: upscaleImages(CGRoot))
            self.createLoading(lambda: convertImages(CGRoot))
            self.createLoading(lambda: pickCG(CGRoot))

        config.set('path', 'input', CGRoot)
        data.loadDatabase(CGRoot)
        self.imageViewer.refresh()

    def collectPickToCG(self):
        from tools.collector import collectPickToCG
        data.flush()
        CGRoot = config.get('path', 'input')
        outPath = config.get('path', 'output')
        newCGRoot = os.path.join(outPath, os.path.basename(CGRoot))
        if (os.path.isdir(newCGRoot) and os.path.samefile(CGRoot, newCGRoot)):
            return

        self.createLoading(lambda: collectPickToCG(CGRoot, newCGRoot))
        utils.remove(CGRoot)

        config.set('path', 'input', newCGRoot)
        data.loadDatabase(newCGRoot)
        self.imageViewer.refresh()

    def formatImageNames(self):
        from tools.name_formater import formatImageNames
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Format Image Names',
                                                  lastCGRoot)
        if not CGRoot:
            return
        config.set('path', 'input', CGRoot)
        formatImageNames(CGRoot)

    def upscaleImages(self):
        from tools.upscaler import upscaleImages
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Upscale Images',
                                                  lastCGRoot)
        if not CGRoot:
            return
        config.set('path', 'input', CGRoot)
        self.createLoading(lambda: upscaleImages(CGRoot))

    def convertImages(self):
        from tools.converter import convertImages
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Convert Images',
                                                  lastCGRoot)
        if not CGRoot:
            return
        config.set('path', 'input', CGRoot)
        self.createLoading(lambda: convertImages(CGRoot))

    def refresh(self):
        self.showMaximized()
        lastCGRoot = config.get('path', 'input')
        data.loadDatabase(lastCGRoot)
        self.imageViewer.refresh()

    def createLoading(self, task):
        self.setEnabled(False)
        loading = Loading(self)
        loading.startTask(task)
        self.setEnabled(True)

    def quit(self):
        data.save()
        qApp.quit()
