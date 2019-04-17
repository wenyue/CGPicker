#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QPixmap
from template.ui_face import Ui_Face
import os


class Face(Ui_Face):
    def __init__(self, *args, **kwargs):
        self.root = QWidget(*args, **kwargs)
        self.setupUi(self.root)
        self.starNum.setStyleSheet("font-size:20px")
        self._face = None
        self._mtime = None

    def setFace(self, face):
        mtime = os.path.getmtime(face)
        if (self._face == face and self._mtime == mtime):
            return
        self._face = face
        self._mtime = mtime
        pixmap = QPixmap(face)
        height = self.root.height()
        width = pixmap.width() / pixmap.height() * height
        pixmap = pixmap.scaled(QSize(width, height))

        self.img.setPixmap(pixmap)
        size = pixmap.size()
        self.root.setMinimumSize(size)
        self.img.resize(size)

        ix, iy = self.img.x(), self.img.y()
        iw, ih = self.img.width(), self.img.height()
        sw, sh = self.icons.width(), self.icons.height()
        self.icons.move(QPoint(ix + iw - sw, iy + ih - sh))

    def selected(self, isSelected):
        if isSelected:
            self.img.setStyleSheet('border: 5px solid red')
        else:
            self.img.setStyleSheet('')
