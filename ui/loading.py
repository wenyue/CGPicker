#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QTimer
from template.ui_loading import Ui_Loading


class Loading(Ui_Loading):

	def __init__(self, *args, **kwargs):
		self.root = QDialog(*args, **kwargs)
		self.setupUi(self.root)
		self.root.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)

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
			self.root.close()

	def show(self, task):
		self.task = task()
		self.taskNum = next(self.task)
		self.root.show()
		self.timer = QTimer()
		self.timer.setInterval(0)
		self.timer.timeout.connect(self.runTask)
		self.timer.start()
		self.root.exec_()
