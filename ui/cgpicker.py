#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction
from template.ui_cgpicker import Ui_CGPicker

from ui.editor import Editor
from ui.picker_config import PickerConfig
from ui.loading import Loading

<<<<<<< HEAD
from common.database import Database
=======
from common.database import data
>>>>>>> c73d583709c49293239096943d944743df2723bb
from common import config
from common import macro


class CGPicker(QMainWindow, Ui_CGPicker):

    def __init__(self, *args, **kwargs):
        super(CGPicker, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self._database = Database()

        self.addSubPanel()
        self.setupMainMenu()

    def addSubPanel(self):
<<<<<<< HEAD
        self.editor = Editor(self._database, self)
        self.horizontalLayout.addWidget(self.editor)

        self.PickerConfig = PickerConfig(self)
=======
        windowMenu = self.menubar.addMenu('&Window')

        self.editor = Editor(self)
        self.editor.setupMainMenu(self.menubar)
        self.horizontalLayout.addWidget(self.editor)

        self.PickerConfig = PickerConfig(self)
        self.PickerConfig.setupMainMenu(windowMenu)
>>>>>>> c73d583709c49293239096943d944743df2723bb
        self.horizontalLayout.addWidget(self.PickerConfig)

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
        fileMenu.addAction(upscaleAction)

        convertAction = QAction('&Convert Images', self)
        convertAction.triggered.connect(self.convertImages)
        fileMenu.addAction(convertAction)

        fileMenu.addSeparator()

        quitAction = QAction('&Quit', self)
        quitAction.setShortcut('Esc')
        quitAction.triggered.connect(self.close)
        fileMenu.addAction(quitAction)

        windowMenu = self.menubar.addMenu('&Window')
        self.PickerConfig.setupMainMenu(windowMenu)

        self.editor.setupMainMenu(self.menubar)

    def pickCG(self):
        from tools.name_formater import formatImageNames
        from tools.upscaler import upscaleImages
        from tools.converter import convertImages
        from tools.picker import pickCG
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Pick CG', lastCGRoot)
        if not CGRoot:
            return

<<<<<<< HEAD
        self._database.flush()
=======
        data.flush()
>>>>>>> c73d583709c49293239096943d944743df2723bb

        if os.path.basename(CGRoot) == 'All':
            from importlib import reload
            import json
            reload(macro)
            self.PickerConfig.reloadMacro()
            self.createLoading(lambda: upscaleImages(CGRoot))
            self.createLoading(lambda: convertImages(CGRoot))
            self.createLoading(lambda: pickCG(CGRoot))

            picks = os.listdir(os.path.join(os.path.dirname(CGRoot), 'Pick'))
            loves = os.listdir(os.path.join(os.path.dirname(CGRoot), 'Love'))
            rating = 1
            dirname = os.path.dirname(CGRoot)
            if dirname.endswith(u'[☆]'):
                rating = 1
            elif dirname.endswith(u'[☆☆]'):
                rating = 2
            if dirname.endswith(u'[☆☆☆]'):
                rating = 3
            if dirname.endswith(u'[❤]'):
                rating = 4

            with open(os.path.join(CGRoot, macro.DATABASE_FILE), 'r') as f:
                proto = json.load(f)
            for sceneProto in proto:
                pickProto = []
                loveProto = []
                for action in sceneProto['actions']:
                    for image in action:
                        if image in picks:
                            pickProto.append(image)
                        if image in loves:
                            loveProto.append(image)
                sceneProto['pick'] = pickProto
                sceneProto['love'] = loveProto
                sceneProto['rating'] = rating if loveProto else 0
            with open(os.path.join(CGRoot, macro.DATABASE_FILE), 'w') as f:
                json.dump(proto, f, indent=2, sort_keys=True)
        elif not os.path.isfile(os.path.join(CGRoot, macro.DATABASE_FILE)):
            from importlib import reload
            reload(macro)
            self.PickerConfig.reloadMacro()
            formatImageNames(CGRoot)
            self.createLoading(lambda: upscaleImages(CGRoot))
            self.createLoading(lambda: convertImages(CGRoot))
            self.createLoading(lambda: pickCG(CGRoot))

        config.set('path', 'input', CGRoot)
<<<<<<< HEAD
        self._database.load(CGRoot)
=======
        data.loadDatabase(CGRoot)
>>>>>>> c73d583709c49293239096943d944743df2723bb
        self.editor.refresh()

    def collectPickToCG(self):
        from tools.collector import collectPickToCG
        self._database.flush()
        CGRoot = config.get('path', 'input')
        outPath = config.get('path', 'output')
        newCGRoot = os.path.join(outPath, os.path.basename(CGRoot))
        #######################
        if os.path.basename(CGRoot) == 'All':
            newCGRoot = os.path.dirname(CGRoot)
            if newCGRoot.endswith(u'[☆]'):
                newCGRoot = newCGRoot.replace(u'[☆]', '')
            elif newCGRoot.endswith(u'[☆☆]'):
                newCGRoot = newCGRoot.replace(u'[☆☆]', '')
            if newCGRoot.endswith(u'[☆☆☆]'):
                newCGRoot = newCGRoot.replace(u'[☆☆☆]', '')
            if newCGRoot.endswith(u'[❤]'):
                newCGRoot = newCGRoot.replace(u'[❤]', '')
        #########################
        if (os.path.isdir(newCGRoot) and os.path.samefile(CGRoot, newCGRoot)):
            return

        self.createLoading(lambda: collectPickToCG(CGRoot, newCGRoot))

        config.set('path', 'input', newCGRoot)
<<<<<<< HEAD
        self._database.load(newCGRoot)
=======
        data.loadDatabase(newCGRoot)
>>>>>>> c73d583709c49293239096943d944743df2723bb
        self.editor.refresh()

    def formatImageNames(self):
        from tools.name_formater import formatImageNames
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Format Image Names', lastCGRoot)
        if not CGRoot:
            return
        config.set('path', 'input', CGRoot)
        formatImageNames(CGRoot)

    def upscaleImages(self):
        from tools.upscaler import upscaleImages
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Upscale Images', lastCGRoot)
        if not CGRoot:
            return
        config.set('path', 'input', CGRoot)
        self.createLoading(lambda: upscaleImages(CGRoot))

    def convertImages(self):
        from tools.converter import convertImages
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Convert Images', lastCGRoot)
        if not CGRoot:
            return
        config.set('path', 'input', CGRoot)
        self.createLoading(lambda: convertImages(CGRoot))

    def refresh(self):
        self.showMaximized()
        lastCGRoot = config.get('path', 'input')
<<<<<<< HEAD
        self._database.load(lastCGRoot)
=======
        data.loadDatabase(lastCGRoot)
>>>>>>> c73d583709c49293239096943d944743df2723bb
        self.editor.refresh()

    def createLoading(self, task):
        self.setEnabled(False)
        loading = Loading(self)
        loading.startTask(task)
        self.setEnabled(True)

    def closeEvent(self, event):
<<<<<<< HEAD
        self._database.flush()
=======
        data.flush()
>>>>>>> c73d583709c49293239096943d944743df2723bb
