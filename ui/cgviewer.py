#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QAction
from template.ui_cgviewer import Ui_CGViewer

from ui.cgpicker import CGPicker

from common import config
from common.random_pool import RatingRandomPool


class CGViewer(QMainWindow, Ui_CGViewer):

    def __init__(self, *args, **kwargs):
        super(CGViewer, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.showMaximized()

        self._randomPool = RatingRandomPool(config.get('path', 'output'))
