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
		self.setEnable(True)
		self.root.show()

	def setEnable(self, isEnable):
		if isEnable:
			size = self.img.pixmap().size()
			self.img.resize(size)
			self.img.move(QPoint(0, 0))
		else:
			size = self.img.pixmap().size()
			w, h = size.width(), size.height()
			scale = 0.85
			size = QSize(w * scale, h * scale)
			self.img.resize(size)
			self.img.move(QPoint(w * (1 - scale) / 2, h * (1 - scale) / 2))
		ix, iy = self.img.x(), self.img.y()
		iw, ih = self.img.width(), self.img.height()
		sw, sh = self.star.width(), self.star.height()
		self.star.move(QPoint(ix + iw - sw, iy + ih - sh))
