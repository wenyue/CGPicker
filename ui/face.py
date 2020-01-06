#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QThread, QPoint, QSize
from PyQt5.QtGui import QPixmap, QImage, QPainter
from template.ui_face import Ui_Face

import os


class LoadFaceThread(QThread):

    def __init__(self, image, faces, faceSize):
        super(LoadFaceThread, self).__init__()
        self._image = image
        self._faces = faces
        self._faceSize = faceSize
        self._pixmap = None

    def run(self):
        self._pixmap = QPixmap(self._faceSize)
        painter = QPainter()
        painter.begin(self._pixmap)
        originalImage = QImage(self._image)
        curPosX = 0
        for face in self._faces:
            faceImage = originalImage.copy(face.x, face.y, face.width, face.height)
            faceImage = faceImage.scaledToHeight(self._faceSize.height(), Qt.SmoothTransformation)
            painter.drawImage(curPosX, 0, faceImage)
            curPosX += faceImage.width()
        painter.end()

    def getFacePixmap(self):
        self.wait()
        return self._pixmap


class Face(QWidget, Ui_Face):

    def __init__(self, *args, **kwargs):
        super(Face, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.starNum.setStyleSheet("font-size:20px")

        self._thread = None
        self._image = None
        self._mtime = None
        self._faces = None

    def selected(self, isSelected):
        if isSelected:
            self.setEnabled(True)
            self.img.setStyleSheet('border: 5px solid red')
        else:
            self.setEnabled(False)
            self.img.setStyleSheet('')

    def isSameFace(self, image, faces):
        mtime = os.path.getmtime(image)
        if (self._image == image and self._mtime == mtime and self._faces == faces):
            return True
        self._image = image
        self._mtime = mtime
        self._faces = faces
        return False

    def setFace(self, image, faces):
        if self.isSameFace(image, faces):
            return

        bigWidth = 0
        for face in self._faces:
            bigWidth += face.width / face.height * self.height()
        faceSize = QSize(bigWidth, self.height())

        self.setMinimumSize(faceSize)
        self.img.resize(faceSize)

        ix, iy = self.img.x(), self.img.y()
        iw, ih = self.img.width(), self.img.height()
        sw, sh = self.icons.width(), self.icons.height()
        self.icons.move(QPoint(ix + iw - sw, iy + ih - sh))

        if self._thread:
            self._thread.quit()
        self._thread = LoadFaceThread(image, faces, faceSize)
        self._thread.finished.connect(lambda thread=self._thread: self._setFacePixmap(thread))
        self._thread.start()

    def _setFacePixmap(self, thread):
        if thread != self._thread:
            return
        pixmap = self._thread.getFacePixmap()
        self.img.setPixmap(pixmap)
        self._thread = None
