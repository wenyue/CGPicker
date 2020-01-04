#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPixmap, QImage, QPainter
from template.ui_face import Ui_Face

import os


class Face(QWidget, Ui_Face):
    def __init__(self, *args, **kwargs):
        super(Face, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.starNum.setStyleSheet("font-size:20px")
        self._image = None
        self._mtime = None
        self._faces = None

    def isSameFace(self, image, faces):
        mtime = os.path.getmtime(image)
        if (self._image == image and self._mtime == mtime
                and self._faces == faces):
            return True
        self._image = image
        self._mtime = mtime
        self._faces = faces
        return False

    def setFace(self, image, faces):
        if self.isSameFace(image, faces):
            return

        bigWidth = 0
        for face in faces:
            bigWidth += face.width / face.height * self.height()
        bigFace = QPixmap(QSize(bigWidth, self.height()))
        painter = QPainter()
        painter.begin(bigFace)
        originalImage = QImage(image)
        curPosX = 0
        for face in faces:
            faceImage = originalImage.copy(face.x, face.y, face.width, face.height)
            faceImage = faceImage.scaledToHeight(self.height(), Qt.SmoothTransformation)
            painter.drawImage(curPosX, 0, faceImage)
            curPosX += faceImage.width()
        painter.end()

        self.img.setPixmap(bigFace)
        self.setMinimumSize(bigFace.size())
        self.img.resize(bigFace.size())

        ix, iy = self.img.x(), self.img.y()
        iw, ih = self.img.width(), self.img.height()
        sw, sh = self.icons.width(), self.icons.height()
        self.icons.move(QPoint(ix + iw - sw, iy + ih - sh))

    def selected(self, isSelected):
        if isSelected:
            self.img.setStyleSheet('border: 5px solid red')
        else:
            self.img.setStyleSheet('')
