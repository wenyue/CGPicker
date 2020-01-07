#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from template.ui_cgpicker import Ui_CGPicker

from ui.editor import Editor
from ui.picker_config import PickerConfig
from ui.loading import Loading

from common.database import Database
from common import config
from common import macro


class CGPicker(QMainWindow, Ui_CGPicker):

    def __init__(self, *args, **kwargs):
        super(CGPicker, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.showMaximized()

        self._database = Database(config.get('path', 'input'))
        sceneIdx = int(config.get('info', 'scene_index'))

        self.editor = Editor(self)
        self.editor.refresh(self._database, sceneIdx)
        self.horizontalLayout.addWidget(self.editor)
        self.editor.setVisible(True)

        self.pickerConfig = PickerConfig(self)
        self.horizontalLayout.addWidget(self.pickerConfig)
        self.pickerConfig.setVisible(False)

        self.setupMainMenu()

    def setupMainMenu(self):
        self.menubar.setNativeMenuBar(False)

        # File menu
        fileMenu = self.menubar.addMenu('&File')

        importAction = fileMenu.addAction('&Import')
        importAction.setShortcut('Ctrl+I')
        importAction.triggered.connect(self.pickCG)

        exportAction = fileMenu.addAction('&Export')
        exportAction.setShortcut('Ctrl+O')
        exportAction.triggered.connect(self.collectPickToCG)

        fileMenu.addSeparator()

        formatAction = fileMenu.addAction('&Format Image names')
        formatAction.triggered.connect(self.formatImageNames)

        upscaleAction = fileMenu.addAction('&Upscale Images')
        upscaleAction.triggered.connect(self.upscaleImages)

        convertAction = fileMenu.addAction('&Convert Images')
        convertAction.triggered.connect(self.convertImages)

        fileMenu.addSeparator()

        quitAction = fileMenu.addAction('&Quit')
        quitAction.setShortcut('Esc')
        quitAction.triggered.connect(self.close)

        # Window menu
        windowMenu = self.menubar.addMenu('&Window')

        editorAction = windowMenu.addAction('Editor')
        editorAction.setEnabled(False)
        editorAction.setCheckable(True)
        editorAction.setChecked(self.editor.isVisible())

        windowMenu.addSeparator()

        pickerConfigAction = windowMenu.addAction('Picker Config')
        pickerConfigAction.setShortcut('`')
        pickerConfigAction.setCheckable(True)
        pickerConfigAction.setChecked(self.pickerConfig.isVisible())
        pickerConfigAction.triggered.connect(self.pickerConfig.toggle)

        # Editor menus
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

        self._database.flush()

        if os.path.basename(CGRoot) == 'All':
            from importlib import reload
            import json
            reload(macro)
            self.pickerConfig.reloadMacro()
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
            self.pickerConfig.reloadMacro()
            formatImageNames(CGRoot)
            self.createLoading(lambda: upscaleImages(CGRoot))
            self.createLoading(lambda: convertImages(CGRoot))
            self.createLoading(lambda: pickCG(CGRoot))

        config.set('path', 'input', CGRoot)
        self._database.load(CGRoot)
        self.editor.refresh(self._database, 0)

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
        self._database.load(newCGRoot)
        self.editor.refresh(self._database, 0)

    def formatImageNames(self):
        from tools.name_formater import formatImageNames
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Format Image Names', lastCGRoot)
        if not CGRoot:
            return
        formatImageNames(CGRoot)

    def upscaleImages(self):
        from tools.upscaler import upscaleImages
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Upscale Images', lastCGRoot)
        if not CGRoot:
            return
        self.createLoading(lambda: upscaleImages(CGRoot))

    def convertImages(self):
        from tools.converter import convertImages
        lastCGRoot = config.get('path', 'input')
        CGRoot = QFileDialog.getExistingDirectory(self, 'Convert Images', lastCGRoot)
        if not CGRoot:
            return
        self.createLoading(lambda: convertImages(CGRoot))

    def createLoading(self, task):
        self.setEnabled(False)
        loading = Loading(self)
        loading.startTask(task)
        self.setEnabled(True)

    def closeEvent(self, event):
        self._database.flush()
        sceneIdx = self.editor.getSceneIdx()
        config.set('info', 'scene_index', str(sceneIdx))
