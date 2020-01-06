#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QTimer
from template.ui_loading import Ui_Loading


class Loading(QDialog, Ui_Loading):

    def __init__(self, *args, **kwargs):
        super(Loading, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)

        self.task = None
        self.timer = None
        self.step = 0

    def runTask(self):
        try:
            text = next(self.task)
            self.label.setText(text)
            self.step += 1
            self.progressBar.setValue(self.step / self.taskNum * 100)
        except StopIteration:
            self.timer.stop()
            self.close()

    def startTask(self, task):
        self.task = task()
        try:
            self.taskNum = next(self.task)
        except StopIteration:
            return
        if self.taskNum == 0:
            return

        self.timer = QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.runTask)
        self.timer.start()

        timestamp = time.time()
        self.show()
        self.exec_()

        if sys.platform.startswith('win') and time.time() - timestamp > 60:
            import winsound
            duration = 500
            freq = 440
            winsound.Beep(freq, duration)
