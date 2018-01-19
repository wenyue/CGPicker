#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QFileDialog, qApp
from PyQt5.QtCore import Qt
from template.ui_cgpicker import Ui_CGPicker
from ui.imageviewer import ImageViewer


class CGPicker(Ui_CGPicker):
	def __init__(self, *args, **kwargs):
		self.root = QMainWindow(*args, **kwargs)
		self.setupUi(self.root)
		self.root.keyPressEvent = self.keyPressEvent

		self.addSubPanel()

	def addSubPanel(self):
		self.viewer = ImageViewer(self.root)
		self.verticalLayout.addWidget(self.viewer.root)

	def pickCGToTmp(self):
		from tools.picker import pickCGToTmp
		CGPath = QFileDialog.getExistingDirectory(self.root, "choose directory")
		pickCGToTmp(CGPath)

	def collectPickToCG(self):
		from tools.collector import collectPickToCG
		CGPath = QFileDialog.getExistingDirectory(self.root, "choose directory")
		collectPickToCG(CGPath)

	def keyPressEvent(self, event):
		QMainWindow.keyPressEvent(self.root, event)
		if event.key() == Qt.Key_O:
			self.collectPickToCG()
		elif event.key() == Qt.Key_I:
			self.pickCGToTmp()
		elif event.key() == Qt.Key_Escape:
			qApp.quit()
		else:
			event.ignore()
		

	def show(self):
		self.root.show()
		self.viewer.showScene()
