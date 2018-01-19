#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint, QSize
from template.ui_face import Ui_Face

class Face(Ui_Face):
	def __init__(self, *args, **kwargs):
		self.root = QWidget(*args, **kwargs)
		self.setupUi(self.root)
	
	def setPixmap(self, pixmap):
		self.img.setPixmap(pixmap)
		size = pixmap.size()
		self.root.setMinimumSize(size)
		self.img.resize(size)
		pw, ph = size.width(), size.height()
		sw, sh = self.star.width(), self.star.height()
		self.star.move(QPoint(pw - sw, ph - sh))
		self.root.show()

	def setEnable(self, isEnable):
		if isEnable:
			w, h = self.img.width(), self.img.height()
			size = QSize(w * 0.9, h * 0.9)
			self.img.resize(size)
			self.img.move(QPoint(w * 0.05, h * 0.05))
		else:
			size = self.img.pixmap().size()
			self.img.resize(size)
			self.img.move(QPoint(0, 0))
